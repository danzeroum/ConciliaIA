import { BaseRepository } from './base.repository';

export interface ProductRecord {
  id: string;
  name: string;
  sku: string;
  description: string | null;
  price: number;
  createdAt: Date;
  updatedAt: Date;
}

export type ProductQueryParams = Record<string, unknown>;

export type CreateProductData = {
  name: string;
  sku: string;
  description?: string;
  price: number;
};

export type UpdateProductData = Partial<
  Pick<ProductRecord, 'name' | 'sku' | 'description' | 'price'>
>;

export class ProductRepository extends BaseRepository {
  async findAll(params: ProductQueryParams = {}): Promise<ProductRecord[]> {
    return this.prisma.product.findMany(params);
  }

  async findById(id: string): Promise<ProductRecord | null> {
    return this.prisma.product.findUnique({
      where: { id },
    });
  }

  async findBySku(sku: string): Promise<ProductRecord | null> {
    return this.prisma.product.findUnique({
      where: { sku },
    });
  }

  async create(data: CreateProductData): Promise<ProductRecord> {
    return this.prisma.product.create({
      data,
    });
  }

  async update(id: string, data: UpdateProductData): Promise<ProductRecord> {
    return this.prisma.product.update({
      where: { id },
      data,
    });
  }

  async delete(id: string): Promise<ProductRecord> {
    return this.prisma.product.delete({
      where: { id },
    });
  }
}

export const productRepository = new ProductRepository();

export default productRepository;
