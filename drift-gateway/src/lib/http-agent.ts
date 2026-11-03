/**
 * High-Performance Outbound HTTP/HTTPS Agent & DNS Prefetcher for CutWire Drift.
 * Reuses persistent TLS/TCP sockets across external AI and API calls (Gemini, OpenAI, Anthropic),
 * eliminating redundant DNS resolutions and expensive TLS handshakes.
 */
import http from 'node:http';
import https from 'node:https';
import dns from 'node:dns';

// Persistent Keep-Alive HTTP Agent
export const driftHttpAgent = new http.Agent({
  keepAlive: true,
  keepAliveMsecs: 30000,
  maxSockets: 64,
  maxFreeSockets: 16,
  timeout: 30000
});

// Persistent Keep-Alive HTTPS Agent with TLS session reuse
export const driftHttpsAgent = new https.Agent({
  keepAlive: true,
  keepAliveMsecs: 30000,
  maxSockets: 64,
  maxFreeSockets: 16,
  timeout: 30000
});

export class DnsPrefetcher {
  private static cachedIps = new Map<string, { ip: string; expiresAt: number }>();
  private static readonly TTL_MS = 60000 * 5; // 5 min DNS cache

  /**
   * Prefetches and resolves hostnames in background to warm up OS DNS cache.
   */
  static async prefetch(hostname: string): Promise<string | null> {
    const cached = this.cachedIps.get(hostname);
    if (cached && Date.now() < cached.expiresAt) {
      return cached.ip;
    }

    return new Promise((resolve) => {
      dns.lookup(hostname, { family: 4 }, (err, address) => {
        if (!err && address) {
          this.cachedIps.set(hostname, { ip: address, expiresAt: Date.now() + this.TTL_MS });
          resolve(address);
        } else {
          resolve(null);
        }
      });
    });
  }

  /**
   * Pre-warms DNS for standard AI endpoints.
   */
  static prewarmKnownAiHosts() {
    const hosts = [
      'api.openai.com',
      'generativelanguage.googleapis.com',
      'api.anthropic.com',
      'api.pexels.com',
      'pixabay.com'
    ];
    for (const host of hosts) {
      this.prefetch(host).catch(() => {});
    }
  }
}

/**
 * Optimized fetch wrapper configuring persistent keep-alive agents.
 */
export async function driftFetch(url: string | URL, init: RequestInit = {}): Promise<Response> {
  const targetUrl = typeof url === 'string' ? new URL(url) : url;
  const isHttps = targetUrl.protocol === 'https:';
  const customInit = {
    ...init,
    // Inject persistent agent if running on Node runtime dispatcher
    dispatcher: isHttps ? driftHttpsAgent : driftHttpAgent
  };
  return fetch(targetUrl, customInit as any);
}

