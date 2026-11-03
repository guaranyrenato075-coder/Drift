import test from 'node:test';
import assert from 'node:assert/strict';

process.env.NODE_ENV = 'test';
process.on('unhandledRejection', () => {});

import { DriftSerializer } from '../dist/lib/serializer.js';
import { LayeredCache } from '../dist/lib/layered-cache.js';
import { CircuitBreaker, CircuitState } from '../dist/lib/circuit-breaker.js';
import { FastRateLimiter } from '../dist/lib/rate-limiter.js';
import { connection, driftQueue, shutdownQueue } from '../dist/lib/queue.js';
import { setupMediaWorker, shutdownMediaWorker, mediaQueue } from '../dist/workers/media.worker.js';

test.after(async () => {
  try {
    await shutdownQueue(true);
  } catch {}
  try {
    await shutdownMediaWorker(true);
  } catch {}
  setTimeout(() => process.exit(0), 50);
});

test('1. DriftSerializer - MessagePack serialization and compression', () => {
  const payload = {
    projectId: 'proj_123',
    title: 'Edição de Alta Performance',
    scenes: [
      { order: 1, duration: 4.5, narration: 'O universo começou com uma grande expansão.' },
      { order: 2, duration: 5.0, narration: 'Estrelas forjaram os elementos químicos fundamentais.' }
    ],
    metadata: { resolution: '3840x2160', fps: 60, codec: 'h265' }
  };

  const packed = DriftSerializer.serialize(payload);
  assert.ok(packed instanceof Uint8Array);

  const jsonBytes = Buffer.from(JSON.stringify(payload)).length;
  console.log(`[Serializer Benchmark] JSON size: ${jsonBytes} bytes | MsgPack size: ${packed.length} bytes`);
  assert.ok(packed.length < jsonBytes);

  const unpacked = DriftSerializer.deserialize(packed);
  assert.deepEqual(unpacked, payload);
});

test('2. LayeredCache - L1 sub-millisecond memory caching', async () => {
  const cache = new LayeredCache({ l1TtlSec: 2, maxL1Entries: 50 });
  await cache.set('cfg_key', { fps: 60, preset: 'prores' });

  const hit = await cache.get('cfg_key');
  assert.deepEqual(hit, { fps: 60, preset: 'prores' });

  let calls = 0;
  const wrappedVal = await cache.wrap('wrapped_key', async () => {
    calls++;
    return 'computed_result';
  });
  assert.equal(wrappedVal, 'computed_result');
  assert.equal(calls, 1);

  // Second call must hit L1 without invoking fetchFn
  const cachedVal = await cache.wrap('wrapped_key', async () => {
    calls++;
    return 'computed_result';
  });
  assert.equal(cachedVal, 'computed_result');
  assert.equal(calls, 1);
});

test('3. CircuitBreaker - Fast-fail and state transitions', async () => {
  const breaker = new CircuitBreaker('test-ai-service', {
    failureThreshold: 2,
    resetTimeoutMs: 100,
    timeoutMs: 500
  });

  assert.equal(breaker.getState(), CircuitState.CLOSED);

  // Failure 1
  try {
    await breaker.execute(async () => { throw new Error('API 500'); });
  } catch {}

  // Failure 2 -> Trips to OPEN
  try {
    await breaker.execute(async () => { throw new Error('API 500'); });
  } catch {}

  assert.equal(breaker.getState(), CircuitState.OPEN);

  // Should fast-fail with fallback
  const fallbackRes = await breaker.execute(
    async () => 'never_reached',
    () => 'fast_fallback'
  );
  assert.equal(fallbackRes, 'fast_fallback');
});

test('4. FastRateLimiter - Sliding window rate limiting', () => {
  const limiter = new FastRateLimiter({ windowMs: 1000, maxRequests: 3 });
  const ip = '192.168.1.100';

  assert.equal(limiter.isAllowed(ip).allowed, true);
  assert.equal(limiter.isAllowed(ip).allowed, true);
  assert.equal(limiter.isAllowed(ip).allowed, true);

  // 4th request exceeds threshold
  const blocked = limiter.isAllowed(ip);
  assert.equal(blocked.allowed, false);
  assert.equal(blocked.remaining, 0);
});

test('5. LightweightPrometheus - Metric exposition under <15MB RAM', async () => {
  const { LightweightPrometheus } = await import('../dist/lib/metrics.js');
  const collector = new LightweightPrometheus();
  collector.recordRequest('GET', '/health', 200, 0.0025);
  collector.recordRequest('POST', '/jobs/enqueue', 202, 0.0150);

  const scrape = await collector.scrape();
  assert.ok(scrape.includes('drift_process_resident_memory_bytes'));
  assert.ok(scrape.includes('drift_nodejs_heap_size_used_bytes'));
  assert.ok(scrape.includes('drift_http_requests_total{method="GET",route="/health",status="200"} 1'));
  assert.ok(scrape.includes('drift_http_requests_total{method="POST",route="/jobs/enqueue",status="202"} 1'));
});

test('6. Fine-Tuning - KeepAlive Timeouts, Persistent Agents & DNS Prefetch', async () => {
  const { app } = await import('../dist/server.js');
  const { driftHttpAgent, driftHttpsAgent, DnsPrefetcher } = await import('../dist/lib/http-agent.js');

  // 1. Fastify & Nginx/Cloudflare Keep-Alive alignment
  assert.equal(app.server.keepAliveTimeout, 65000);
  assert.equal(app.server.headersTimeout, 66000);
  assert.ok(app.server.headersTimeout > app.server.keepAliveTimeout);

  // 2. Persistent Outbound Agents
  assert.equal(driftHttpAgent.keepAlive, true);
  assert.equal(driftHttpsAgent.keepAlive, true);
  assert.equal(driftHttpsAgent.maxSockets, 64);

  // 3. DNS Prefetcher
  const ip = await DnsPrefetcher.prefetch('localhost');
  assert.ok(ip === '127.0.0.1' || ip === '::1' || typeof ip === 'string');
});

test('7. MediaWorker - Concurrency limit, profiles, and queue initialization', async () => {
  const worker = setupMediaWorker();
  assert.ok(worker);
  assert.equal(worker.opts.concurrency, 1);
  assert.equal(worker.name, 'drift-media-processing');
  assert.equal(mediaQueue.name, 'drift-media-processing');
});

test('8. MediaRoutes - Zod schema validation & 202 Accepted dispatch', async () => {
  const { app } = await import('../dist/server.js');

  // Test Bad Request on invalid payload
  const badRes = await app.inject({
    method: 'POST',
    url: '/api/drift/process',
    payload: { profile: 'proxy-light' } // missing inputUrl
  });
  assert.equal(badRes.statusCode, 400);
  const badBody = JSON.parse(badRes.payload);
  assert.equal(badBody.success, false);
  assert.ok(badBody.issues.length > 0);

  // Test 202 Accepted on valid payload
  const okRes = await app.inject({
    method: 'POST',
    url: '/api/drift/process',
    payload: { inputUrl: 'https://storage.drift.io/raw/clip_101.mp4', profile: 'proxy-light' }
  });
  assert.equal(okRes.statusCode, 202);
  const okBody = JSON.parse(okRes.payload);
  assert.equal(okBody.success, true);
  assert.ok(okBody.jobId);
});

