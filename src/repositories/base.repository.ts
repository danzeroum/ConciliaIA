import prisma from '../lib/prisma';

export abstract class BaseRepository {
  protected readonly prisma = prisma;
}

export type BaseRepositoryConstructor<T extends BaseRepository> = new (...args: never[]) => T;
