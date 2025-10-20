import { Prisma, Product } from '@prisma/client';

import { BaseRepository } from './base.repository';

export class ProductRepository extends BaseRepository {
  async findAll(params: Prisma.ProductFindManyArgs = {}): Promise<Product[]> {
    return this.prisma.product.findMany(params);
  }

  async findById(id: string): Promise<Product | null> {
    return this.prisma.product.findUnique({
      where: { id },
    });
  }

  async create(data: Prisma.ProductCreateInput): Promise<Product> {
    return this.prisma.product.create({
      data,
    });
  }

  async update(id: string, data: Prisma.ProductUpdateInput): Promise<Product> {
    return this.prisma.product.update({
      where: { id },
      data,
    });
  }
}

export const productRepository = new ProductRepository();

export default productRepository;
