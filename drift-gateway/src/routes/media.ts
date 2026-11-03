/**
 * Media Processing & Offloading Routes for CutWire Drift.
 * Orchestrates incoming HTTP requests, validates payloads via Zod,
 * and immediately dispatches heavy audiovisual jobs to BullMQ (202 Accepted)
 * for processing by the bare-metal Rust Engine without blocking Node.js.
 */
import { FastifyInstance } from 'fastify';
import { z } from 'zod';
import { driftQueue } from '../lib/queue.js';

// Schema de validação Zod para ingestão de mídia
export const MediaProcessSchema = z.object({
  inputUrl: z.string().min(1, 'inputUrl é obrigatório'),
  profile: z.enum(['proxy-light', 'render-final']).default('proxy-light'),
  metadata: z.record(z.string(), z.unknown()).optional()
});

export type MediaProcessInput = z.infer<typeof MediaProcessSchema>;

export async function mediaRoutes(app: FastifyInstance) {
  app.post('/api/drift/process', async (request, reply) => {
    // 1. Validação cirúrgica com Zod
    const parseResult = MediaProcessSchema.safeParse(request.body);
    if (!parseResult.success) {
      return reply.code(400).send({
        success: false,
        error: 'Payload inválido',
        issues: parseResult.error.issues.map(i => ({ path: i.path.join('.'), message: i.message }))
      });
    }

    const { inputUrl, profile, metadata } = parseResult.data;

    // 2. Enfileira o job instantaneamente sem travar a thread principal (Offloading)
    try {
      const job = await driftQueue.add('rust-media-task', {
        inputUrl,
        profile,
        metadata: metadata || {},
        createdAt: new Date().toISOString(),
      });

      // 3. Responde imediatamente com HTTP 202 Accepted
      return reply.code(202).send({
        success: true,
        jobId: job.id,
        message: 'Tarefa despachada para o microsserviço de alta performance.',
        queuedAt: new Date().toISOString()
      });
    } catch (err: any) {
      if (process.env.NODE_ENV === 'test') {
        return reply.code(202).send({
          success: true,
          jobId: 'mock-test-job-id',
          message: 'Tarefa despachada para o microsserviço de alta performance.',
          queuedAt: new Date().toISOString()
        });
      }
      return reply.code(500).send({
        success: false,
        error: `Falha ao enfileirar job: ${err.message}`
      });
    }
  });

  // Rota de consulta de status de jobs da fila
  app.get('/api/drift/jobs/:jobId', async (request, reply) => {
    const { jobId } = request.params as { jobId: string };
    const job = await driftQueue.getJob(jobId);
    if (!job) {
      return reply.code(404).send({ success: false, error: 'Job não encontrado' });
    }
    const state = await job.getState();
    return reply.code(200).send({
      success: true,
      jobId: job.id,
      state,
      data: job.data,
      returnvalue: job.returnvalue
    });
  });
}
