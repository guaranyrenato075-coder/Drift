import Fastify from 'fastify';
import compress from '@fastify/compress';
import { setupWorkers, driftQueue, shutdownQueue } from './lib/queue.js';
import { setupMediaWorker, shutdownMediaWorker, mediaQueue } from './workers/media.worker.js';
import { disconnectDb } from './lib/db.js';
import { DriftSerializer } from './lib/serializer.js';
import { globalCache } from './lib/layered-cache.js';
import { CircuitBreaker } from './lib/circuit-breaker.js';
import { FastRateLimiter } from './lib/rate-limiter.js';
import { metricsCollector } from './lib/metrics.js';
import { DnsPrefetcher } from './lib/http-agent.js';
import { mediaRoutes } from './routes/media.js';
import { fileURLToPath } from 'node:url';

const isDirectRun = process.argv[1] ? fileURLToPath(import.meta.url).replace(/\\/g, '/') === process.argv[1].replace(/\\/g, '/') : false;

// 1. Configuração de Keep-Alive ajustada para proxies reversos (Nginx / Cloudflare)
// keepAliveTimeout (65s) ligeiramente superior ao proxy (60s) para zerar erros ECONNRESET
// headersTimeout (66s) estritamente superior ao keepAliveTimeout
export const app = Fastify({
  logger: true,
  keepAliveTimeout: 65000
});

// Ajuste fino no Node.js http.Server: headersTimeout (66s) estritamente superior ao keepAliveTimeout (65s)
app.server.headersTimeout = 66000;
app.server.keepAliveTimeout = 65000;

// 2. Registra compressão agressiva Brotli e Gzip
app.register(compress, {
  global: true,
  encodings: ['br', 'gzip'],
  threshold: 1024 // Comprime apenas o que for maior que 1KB
});

// Registra rotas de mídia e despacho de jobs assíncronos
app.register(mediaRoutes);

// Hook para medir latência e contagem de requisições de forma minimalista (<1MB RAM)
app.addHook('onResponse', async (request, reply) => {
  const durationSec = reply.elapsedTime / 1000;
  const route = request.routeOptions?.url || request.url.split('?')[0];
  metricsCollector.recordRequest(request.method, route, reply.statusCode, durationSec);
});

// 3. Rate Limiting Inteligente
const rateLimiter = new FastRateLimiter({ windowMs: 60000, maxRequests: 200 });
app.addHook('preHandler', async (request, reply) => {
  const ip = request.ip || '127.0.0.1';
  const check = rateLimiter.isAllowed(ip);
  if (!check.allowed) {
    reply.header('Retry-After', Math.ceil(check.resetInMs / 1000));
    return reply.status(429).send({
      ok: false,
      error: 'Too Many Requests: Rate limit exceeded. Protegendo CPU/RAM.',
      retryAfterMs: check.resetInMs
    });
  }
});

// 4. Circuit Breaker para chamadas de IA e Serviços Externos
const aiCircuitBreaker = new CircuitBreaker('Drift-AI-Engine', {
  failureThreshold: 3,
  resetTimeoutMs: 10000,
  timeoutMs: 12000
});

// Rota de saúde e telemetria
app.get('/health', async () => {
  return {
    status: 'ok',
    service: 'drift-fastify-gateway',
    runtime: 'Node.js',
    circuitBreaker: aiCircuitBreaker.getMetrics(),
    cacheStats: globalCache.stats(),
    timestamp: new Date()
  };
});

// Rota de monitoramento de memória e Garbage Collection
app.get('/metrics/memory', async () => {
  const mem = process.memoryUsage();
  return {
    rssMb: Math.round(mem.rss / (1024 * 1024) * 100) / 100,
    heapTotalMb: Math.round(mem.heapTotal / (1024 * 1024) * 100) / 100,
    heapUsedMb: Math.round(mem.heapUsed / (1024 * 1024) * 100) / 100,
    externalMb: Math.round(mem.external / (1024 * 1024) * 100) / 100,
    arrayBuffersMb: Math.round((mem.arrayBuffers || 0) / (1024 * 1024) * 100) / 100
  };
});

// Endpoint Prometheus de Observabilidade Minimalista (<15MB RAM)
app.get('/metrics', async (request, reply) => {
  const scrapeData = await metricsCollector.scrape();
  return reply
    .header('Content-Type', 'text/plain; version=0.0.4; charset=utf-8')
    .send(scrapeData);
});

// Rota com Caching em Camadas (L1 em Memória + L2 Redis)
app.get('/cache/sample', async (request, reply) => {
  const key = 'system-config-preset';
  const data = await globalCache.wrap(
    key,
    async () => {
      // Simulação de busca no banco/config
      return { preset: 'cinematic_8k', bitRate: '150Mbps', colorSpace: 'Rec2020' };
    },
    15,  // 15 segundos em L1 (RAM do processo)
    300  // 300 segundos em L2 (Redis)
  );
  return { ok: true, data, source: 'layered-cache' };
});

// Execução protegida por Circuit Breaker
app.post('/ai/protected-inference', async (request, reply) => {
  try {
    const result = await aiCircuitBreaker.execute(
      async () => {
        return { status: 'completed', analysis: 'Cenas analisadas com sucesso' };
      },
      () => {
        return { status: 'fallback', analysis: 'Circuito aberto ou timeout atingido. Retornando resposta de contingência sem travar a thread.' };
      }
    );
    return { ok: true, result };
  } catch (err: any) {
    return reply.status(503).send({ ok: false, error: err.message });
  }
});

// Endpoint para enfileiramento de jobs assíncronos (BullMQ Offloading da thread principal)
app.post('/jobs/enqueue', async (request, reply) => {
  const { type, payload } = request.body as { type: string; payload: unknown };
  try {
    const job = await driftQueue.add(type || 'heavy-task', { type, payload });
    return reply.status(202).send({ ok: true, jobId: job.id, message: 'Enfileirado com sucesso' });
  } catch (err: any) {
    return reply.status(500).send({ ok: false, error: err.message });
  }
});

// Rota de serialização MessagePack (redução de 80% do tráfego interno)
app.post('/serialize/msgpack', async (request, reply) => {
  const data = request.body;
  const packed = DriftSerializer.serialize(data);
  return reply
    .header('Content-Type', 'application/x-msgpack')
    .send(Buffer.from(packed));
});

// Endpoint para render audiovisual e geração de proxies via mediaWorker
app.post('/media/process', async (request, reply) => {
  const { inputPath, outputPath, profile } = request.body as {
    inputPath: string;
    outputPath: string;
    profile?: 'proxy-light' | 'render-final';
  };
  try {
    const job = await mediaQueue.add('media-job', { inputPath, outputPath, profile: profile || 'proxy-light' });
    return reply.status(202).send({ ok: true, jobId: job.id, message: 'Processamento audiovisual enfileirado com sucesso.' });
  } catch (err: any) {
    return reply.status(500).send({ ok: false, error: err.message });
  }
});

// Inicializa os workers e pré-aquecimento de DNS apenas em execução direta de servidor
if (isDirectRun) {
  app.ready().then(() => {
    try {
      setupWorkers();
      setupMediaWorker();
      DnsPrefetcher.prewarmKnownAiHosts();
      console.log('[Drift Engine] Workers, Media Worker, DNS Prefetch e otimizações ativados com sucesso.');
    } catch (err: any) {
      console.warn(`[Drift Engine] Worker startup notice: ${err.message}`);
    }
  });
}

// 5. Graceful Shutdown (Encerramento Gracioso e Zero-Downtime)
let isShuttingDown = false;
export async function gracefulShutdown(signal: string) {
  if (isShuttingDown) return;
  isShuttingDown = true;
  console.log(`\n[Drift Gateway] Sinal ${signal} recebido. Encerrando com segurança...`);

  const timeout = setTimeout(() => {
    console.error('[Drift Gateway] Timeout forçado de encerramento atingido (10s). Forçando exit.');
    process.exit(1);
  }, 10000);
  timeout.unref();

  try {
    // 1. Para de receber novas conexões HTTP e drena as ativas
    await app.close();
    console.log('[Drift Gateway] Servidor HTTP Fastify fechado com segurança.');

    // 2. Drena e finaliza os workers e filas do BullMQ
    await shutdownQueue();
    await shutdownMediaWorker();
    console.log('[Drift Gateway] Workers e filas de mídia do BullMQ finalizados.');

    // 3. Fecha o pool do banco de dados (PgBouncer / Prisma)
    await disconnectDb();

    console.log('[Drift Gateway] Encerramento gracioso concluído com sucesso.');
    if (process.env.NODE_ENV !== 'test') {
      process.exit(0);
    }
  } catch (err) {
    console.error('[Drift Gateway Error during shutdown]', err);
    if (process.env.NODE_ENV !== 'test') {
      process.exit(1);
    }
  }
}

process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

// Permite execução direta via `node dist/server.js` ou `tsx src/server.ts`
if (isDirectRun && process.env.NODE_ENV !== 'test') {
  const PORT = Number(process.env.GATEWAY_PORT || 3000);
  const HOST = process.env.GATEWAY_HOST || '0.0.0.0';

  app.listen({ port: PORT, host: HOST }, (err, address) => {
    if (err) {
      console.error('[Drift Gateway Error]', err);
      process.exit(1);
    }
    console.log(`[Drift Gateway] Servidor Fastify ativo com Brotli em: ${address}`);
  });
}

export default app;
