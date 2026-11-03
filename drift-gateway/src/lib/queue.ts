import { Queue, Worker, Job } from 'bullmq';
import { Redis } from 'ioredis';

const redisUrl = process.env.REDIS_URL || 'redis://localhost:6379';

export const connection = new Redis(redisUrl, {
  maxRetriesPerRequest: null,
  lazyConnect: true,
  retryStrategy(times: number) {
    if (process.env.NODE_ENV === 'test') {
      return null; // Don't reconnect in test environment to avoid keeping event loop open
    }
    return Math.min(times * 100, 3000);
  }
});

connection.on('error', (err: any) => {
  if (process.env.NODE_ENV !== 'test') {
    console.warn(`[BullMQ/Redis] Redis connection warning: ${err.message}`);
  }
});

// Fila de tarefas pesadas
export const driftQueue = new Queue('drift-heavy-tasks', { connection });

let activeWorker: Worker | null = null;

export function setupWorkers(): Worker {
  if (activeWorker) {
    return activeWorker;
  }

  activeWorker = new Worker(
    'drift-heavy-tasks',
    async (job: Job) => {
      const { type, payload } = job.data;
      console.log(`[Worker] Processando job ${job.id} do tipo: ${type}`);

      if (type === 'ai-processing') {
        console.log(`[Worker] Executando pipeline assíncrono para payload:`, payload);
      }

      return { success: true, processedAt: new Date() };
    },
    { connection, concurrency: 4 } // Limita concorrência para poupar CPU/RAM
  );

  activeWorker.on('completed', (job) => {
    console.log(`[Worker] Job ${job.id} concluído com sucesso.`);
  });

  activeWorker.on('failed', (job, err) => {
    console.error(`[Worker] Job ${job?.id} falhou:`, err.message);
  });

  activeWorker.on('error', (err: any) => {
    if (process.env.NODE_ENV !== 'test') {
      console.warn(`[Worker] Background worker warning: ${err.message}`);
    }
  });

  return activeWorker;
}

export async function shutdownQueue(force: boolean = false): Promise<void> {
  if (activeWorker) {
    try {
      await activeWorker.close(force);
    } catch {}
    activeWorker = null;
  }
  try {
    await driftQueue.close();
  } catch {}
  try {
    connection.disconnect(false);
  } catch {}
}
