/**
 * Multi-Tier Layered Cache (L1 In-Memory + L2 Redis) for CutWire Drift.
 * Tier 1 (L1): Local process RAM with micro-TTL (<0.05ms sub-millisecond access, 0 network I/O).
 * Tier 2 (L2): Shared Redis instance with extended TTL for multi-instance sync.
 */
import type { Redis } from 'ioredis';

export interface CacheOptions {
  l1TtlSec?: number;
  l2TtlSec?: number;
  maxL1Entries?: number;
}

class FastLru<T> {
  private cache = new Map<string, { value: T; expiresAt: number }>();
  private max: number;

  constructor(maxEntries = 500) {
    this.max = maxEntries;
  }

  get(key: string): T | null {
    const entry = this.cache.get(key);
    if (!entry) return null;
    if (Date.now() > entry.expiresAt) {
      this.cache.delete(key);
      return null;
    }
    // Refresh LRU order
    this.cache.delete(key);
    this.cache.set(key, entry);
    return entry.value;
  }

  set(key: string, value: T, ttlSec: number): void {
    if (this.cache.has(key)) {
      this.cache.delete(key);
    } else if (this.cache.size >= this.max) {
      // Evict oldest item (first key in insertion order)
      const firstKey = this.cache.keys().next().value;
      if (firstKey) this.cache.delete(firstKey);
    }
    this.cache.set(key, { value, expiresAt: Date.now() + ttlSec * 1000 });
  }

  delete(key: string): void {
    this.cache.delete(key);
  }

  clear(): void {
    this.cache.clear();
  }

  size(): number {
    return this.cache.size;
  }
}

export class LayeredCache {
  private l1: FastLru<unknown>;
  private l2: Redis | null = null;
  private defaultL1Ttl: number;
  private defaultL2Ttl: number;

  constructor(options: CacheOptions = {}, redisClient?: Redis) {
    this.l1 = new FastLru(options.maxL1Entries || 1000);
    this.defaultL1Ttl = options.l1TtlSec || 15;     // 15 seconds in L1
    this.defaultL2Ttl = options.l2TtlSec || 300;    // 5 minutes in L2
    this.l2 = redisClient || null;
  }

  setRedisClient(client: Redis) {
    this.l2 = client;
  }

  async get<T>(key: string): Promise<T | null> {
    // 1. Check L1 Memory (Sub-millisecond, 0 I/O)
    const l1Hit = this.l1.get(key) as T | null;
    if (l1Hit !== null && l1Hit !== undefined) {
      return l1Hit;
    }

    // 2. Check L2 Redis (Network I/O)
    if (this.l2) {
      try {
        const l2Hit = await this.l2.get(key);
        if (l2Hit) {
          const parsed = JSON.parse(l2Hit) as T;
          // Populate L1 for future instant hits
          this.l1.set(key, parsed, this.defaultL1Ttl);
          return parsed;
        }
      } catch (err: any) {
        console.warn(`[LayeredCache] L2 read warning for ${key}: ${err.message}`);
      }
    }

    return null;
  }

  async set(key: string, value: unknown, l1TtlSec?: number, l2TtlSec?: number): Promise<void> {
    const ttl1 = l1TtlSec || this.defaultL1Ttl;
    const ttl2 = l2TtlSec || this.defaultL2Ttl;

    // Save in L1
    this.l1.set(key, value, ttl1);

    // Save in L2 Redis
    if (this.l2) {
      try {
        await this.l2.setex(key, ttl2, JSON.stringify(value));
      } catch (err: any) {
        console.warn(`[LayeredCache] L2 write warning for ${key}: ${err.message}`);
      }
    }
  }

  async delete(key: string): Promise<void> {
    this.l1.delete(key);
    if (this.l2) {
      try {
        await this.l2.del(key);
      } catch (err: any) {
        console.warn(`[LayeredCache] L2 delete warning for ${key}: ${err.message}`);
      }
    }
  }

  async wrap<T>(
    key: string,
    fetchFn: () => Promise<T>,
    l1TtlSec?: number,
    l2TtlSec?: number
  ): Promise<T> {
    const cached = await this.get<T>(key);
    if (cached !== null && cached !== undefined) {
      return cached;
    }
    const fresh = await fetchFn();
    await this.set(key, fresh, l1TtlSec, l2TtlSec);
    return fresh;
  }

  stats() {
    return {
      l1Entries: this.l1.size(),
      hasL2Redis: this.l2 !== null,
      defaultL1TtlSec: this.defaultL1Ttl,
      defaultL2TtlSec: this.defaultL2Ttl
    };
  }
}

export const globalCache = new LayeredCache();
