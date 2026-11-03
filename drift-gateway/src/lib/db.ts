import { PrismaClient } from '@prisma/client';

// Configuração otimizada para reutilização estrita via pool PgBouncer
const globalForPrisma = global as unknown as { prisma: PrismaClient };

export const prisma =
  globalForPrisma.prisma ||
  new PrismaClient({
    log: ['error', 'warn'],
    datasources: {
      db: {
        // Aponte a URL diretamente para a porta do PgBouncer (ex: 6543)
        url: process.env.DATABASE_URL || 'postgresql://drift:drift@localhost:6543/driftdb?pgbouncer=true',
      },
    },
  });

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma;

export async function disconnectDb(): Promise<void> {
  try {
    await prisma.$disconnect();
    console.log('[Drift DB] Pool de conexões do PgBouncer desconectado com sucesso.');
  } catch (err: any) {
    console.warn(`[Drift DB] Disconnect warning: ${err.message}`);
  }
}
