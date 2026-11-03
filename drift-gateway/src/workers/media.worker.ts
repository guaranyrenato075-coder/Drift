/**
 * Audiovisual Media Processing Worker for CutWire Drift.
 * Dedicated background worker executing on 'drift-media-processing' queue.
 * Features intelligent GPU NVENC hardware acceleration with automatic CPU fallback,
 * lightweight 720p proxy generation, and concurrency limit of 1 to prevent resource thrashing.
 */
import { Worker, Job, Queue } from 'bullmq';
import { Redis } from 'ioredis';
import { execFile } from 'child_process';
import { promisify } from 'util';
import path from 'path';

const execFileAsync = promisify(execFile);

const redisUrl = process.env.REDIS_URL || 'redis://localhost:6379';

export const mediaConnection = new Redis(redisUrl, {
  maxRetriesPerRequest: null,
  lazyConnect: true,
  retryStrategy(times: number) {
    if (process.env.NODE_ENV === 'test') {
      return null;
    }
    return Math.min(times * 100, 3000);
  }
});

mediaConnection.on('error', (err: any) => {
  if (process.env.NODE_ENV !== 'test') {
    console.warn(`[Media Worker/Redis] Connection notice: ${err.message}`);
  }
});

// Fila dedicada de processamento audiovisual
export const mediaQueue = new Queue('drift-media-processing', { connection: mediaConnection });

let activeMediaWorker: Worker | null = null;

export function setupMediaWorker(): Worker {
  if (activeMediaWorker) {
    return activeMediaWorker;
  }

  activeMediaWorker = new Worker(
    'drift-media-processing',
    async (job: Job) => {
      const { inputPath, outputPath, profile } = job.data;
      console.log(`[Media Worker] Iniciando processamento do job ${job.id} [Perfil: ${profile}]`);

      // 1. Tentar render acelerado por hardware NVIDIA (NVENC)
      let nvencArgs: string[];
      let cpuFallbackArgs: string[];

      if (profile === 'proxy-light') {
        // Proxy leve 720p para visualização fluida na timeline sem estressar RAM/GPU
        nvencArgs = [
          '-y',
          '-hwaccel', 'cuda',
          '-i', inputPath,
          '-c:v', 'h264_nvenc',
          '-preset', 'p4',
          '-vf', 'scale=-2:720',
          '-b:v', '2M',
          '-c:a', 'aac',
          '-b:a', '128k',
          outputPath
        ];

        cpuFallbackArgs = [
          '-y',
          '-i', inputPath,
          '-c:v', 'libx264',
          '-preset', 'veryfast',
          '-vf', 'scale=-2:720',
          '-b:v', '2M',
          '-c:a', 'aac',
          '-b:a', '128k',
          outputPath
        ];
      } else {
        // Render final otimizado mantendo alta qualidade de exportação
        nvencArgs = [
          '-y',
          '-hwaccel', 'cuda',
          '-i', inputPath,
          '-c:v', 'h264_nvenc',
          '-preset', 'p6',
          '-c:a', 'aac',
          outputPath
        ];

        cpuFallbackArgs = [
          '-y',
          '-i', inputPath,
          '-c:v', 'libx264',
          '-preset', 'medium',
          '-crf', '20',
          '-c:a', 'aac',
          outputPath
        ];
      }

      try {
        // Tentativa primária: Aceleração por Hardware GPU
        await execFileAsync('ffmpeg', nvencArgs);
        console.log(`[Media Worker] Job ${job.id} renderizado com sucesso via NVENC: ${outputPath}`);
        return { success: true, outputPath, acceleration: 'cuda_nvenc' };
      } catch (nvencError: any) {
        console.warn(
          `[Media Worker] GPU NVENC indisponível (${nvencError.message.split('\n')[0]}). Acionando fallback por CPU...`
        );
        try {
          // Fallback secundário automático: CPU
          await execFileAsync('ffmpeg', cpuFallbackArgs);
          console.log(`[Media Worker] Job ${job.id} renderizado com sucesso via CPU Fallback: ${outputPath}`);
          return { success: true, outputPath, acceleration: 'cpu_fallback' };
        } catch (cpuError: any) {
          console.error(`[Media Worker] Falha no processamento do job ${job.id}:`, cpuError.message);
          throw cpuError;
        }
      }
    },
    {
      connection: mediaConnection,
      concurrency: 1 // Limita a 1 render por vez para zerar picos simultâneos de GPU e RAM
    }
  );

  activeMediaWorker.on('completed', (job) => {
    console.log(`[Media Worker] Tarefa de mídia ${job.id} finalizada.`);
  });

  activeMediaWorker.on('failed', (job, err) => {
    console.error(`[Media Worker] Tarefa ${job?.id} falhou:`, err.message);
  });

  activeMediaWorker.on('error', (err: any) => {
    if (process.env.NODE_ENV !== 'test') {
      console.warn(`[Media Worker] Worker notice: ${err.message}`);
    }
  });

  return activeMediaWorker;
}

export async function shutdownMediaWorker(force: boolean = false): Promise<void> {
  if (activeMediaWorker) {
    try {
      await activeMediaWorker.close(force);
    } catch {}
    activeMediaWorker = null;
  }
  try {
    await mediaQueue.close();
  } catch {}
  try {
    mediaConnection.disconnect(false);
  } catch {}
}
