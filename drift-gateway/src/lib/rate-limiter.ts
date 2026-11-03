/**
 * Sliding Window Rate Limiter for CutWire Drift Gateway.
 * Bars abusive clients and bots before they consume CPU or trigger heavy pipelines.
 */

export interface RateLimiterOptions {
  windowMs?: number;      // Window size in ms (default: 60,000ms = 1 min)
  maxRequests?: number;   // Max allowed requests per window (default: 100)
}

export class FastRateLimiter {
  private requests = new Map<string, number[]>();
  private readonly windowMs: number;
  private readonly maxRequests: number;

  constructor(options: RateLimiterOptions = {}) {
    this.windowMs = options.windowMs || 60000;
    this.maxRequests = options.maxRequests || 100;

    // Periodic cleanup of stale clients every 2 minutes
    setInterval(() => this.cleanup(), 120000).unref();
  }

  isAllowed(clientId: string): { allowed: boolean; remaining: number; resetInMs: number } {
    const now = Date.now();
    const windowStart = now - this.windowMs;

    let timestamps = this.requests.get(clientId) || [];
    // Discard timestamps outside active window
    timestamps = timestamps.filter(ts => ts > windowStart);

    if (timestamps.length >= this.maxRequests) {
      const oldest = timestamps[0];
      const resetInMs = Math.max(0, oldest + this.windowMs - now);
      return { allowed: false, remaining: 0, resetInMs };
    }

    timestamps.push(now);
    this.requests.set(clientId, timestamps);

    return {
      allowed: true,
      remaining: this.maxRequests - timestamps.length,
      resetInMs: this.windowMs
    };
  }

  private cleanup() {
    const now = Date.now();
    const windowStart = now - this.windowMs;
    for (const [id, timestamps] of this.requests.entries()) {
      const valid = timestamps.filter(ts => ts > windowStart);
      if (valid.length === 0) {
        this.requests.delete(id);
      } else {
        this.requests.set(id, valid);
      }
    }
  }

  reset(clientId?: string) {
    if (clientId) {
      this.requests.delete(clientId);
    } else {
      this.requests.clear();
    }
  }
}

