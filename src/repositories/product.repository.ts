import { Prisma, Product as PrismaProduct } from '@prisma/client';
import { BaseRepository } from './base.repository';

export type ProductRecord = Omit<PrismaProduct, 'price'> & { price: number };

export type ProductQueryParams = Prisma.ProductFindManyArgs;

export type CreateProductData = {
  name: string;
  sku: string;
  description?: string;
  price: number;
};

export type UpdateProductData = Partial<
  Pick<ProductRecord, 'name' | 'sku' | 'description' | 'price'>
>;

const mapProduct = (product: PrismaProduct): ProductRecord => ({
  ...product,
  price: Number(product.price),
});

export class ProductRepository extends BaseRepository {
  async findAll(params: ProductQueryParams = {}): Promise<ProductRecord[]> {
    const products = await this.prisma.product.findMany(params);
    return products.map(mapProduct);
  }

  async findById(id: string): Promise<ProductRecord | null> {
    const product = await this.prisma.product.findUnique({
      where: { id },
    });

    return product ? mapProduct(product) : null;
  }

  async findBySku(sku: string): Promise<ProductRecord | null> {
    const product = await this.prisma.product.findUnique({
      where: { sku },
    });

    return product ? mapProduct(product) : null;
  }

  async create(data: CreateProductData): Promise<ProductRecord> {
    const product = await this.prisma.product.create({
      data,
    });

    return mapProduct(product);
  }

  async update(id: string, data: UpdateProductData): Promise<ProductRecord> {
    const product = await this.prisma.product.update({
      where: { id },
      data,
    });

    return mapProduct(product);
  }

  async delete(id: string): Promise<ProductRecord> {
    const product = await this.prisma.product.delete({
      where: { id },
    });

    return mapProduct(product);
  }
}

export const productRepository = new ProductRepository();

export default productRepository;
