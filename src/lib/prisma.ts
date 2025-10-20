import { PrismaClient } from '@prisma/client';

const globalForPrisma = globalThis as unknown as {
  prisma?: PrismaClient;
  prismaShutdownHookRegistered?: boolean;
};

const normaliseDatabaseUrl = (rawUrl?: string): string | undefined => {
  if (!rawUrl) {
    return undefined;
  }

  const url = rawUrl.replace(/^postgresql\+[^:]+:\/\//i, 'postgresql://');

  try {
    const parsed = new URL(url);
    const { searchParams } = parsed;

    const poolMax = process.env.DATABASE_POOL_MAX;
    const poolTimeout = process.env.DATABASE_POOL_TIMEOUT;

    if (poolMax) {
      searchParams.set('connection_limit', poolMax);
    }

    if (poolTimeout) {
      searchParams.set('pool_timeout', poolTimeout);
    }

    parsed.search = searchParams.toString();

    return parsed.toString();
  } catch (error) {
    console.warn('[Prisma] Failed to parse DATABASE_URL, using raw value.', error);
    return url;
  }
};

const createPrismaClient = (): PrismaClient => {
  const datasourceUrl = normaliseDatabaseUrl(process.env.DATABASE_URL);

  const logLevels: Array<'info' | 'query' | 'warn' | 'error'> =
    process.env.NODE_ENV === 'development'
      ? ['query', 'info', 'warn', 'error']
      : ['warn', 'error'];

  const prisma = new PrismaClient({
    datasources: datasourceUrl ? { db: { url: datasourceUrl } } : undefined,
    log: logLevels,
  });

  if (process.env.NODE_ENV === 'development') {
    prisma.$use(async (params: Record<string, unknown>, next: (params: Record<string, unknown>) => Promise<unknown>) => {
      const start = Date.now();
      const result = await next(params);
      const duration = Date.now() - start;
      const action = [params.model, params.action].filter(Boolean).join('.');
      console.debug(`[Prisma] ${action} executed in ${duration}ms`);
      return result;
    });
  }

  if (!globalForPrisma.prismaShutdownHookRegistered) {
    const shutdown = async () => {
      await prisma.$disconnect();
    };

    prisma.$on('beforeExit', shutdown);

    const signals: NodeJS.Signals[] = ['SIGINT', 'SIGTERM'];
    signals.forEach((signal) => {
      process.once(signal, async () => {
        await shutdown();
        process.exit(0);
      });
    });

    globalForPrisma.prismaShutdownHookRegistered = true;
  }

  return prisma;
};

const prisma = globalForPrisma.prisma ?? createPrismaClient();

if (process.env.NODE_ENV !== 'production') {
  globalForPrisma.prisma = prisma;
}

export default prisma;
