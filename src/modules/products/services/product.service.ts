import { ConflictError, NotFoundError, ValidationError } from '../../../utils/errors';
import { parseWithSchema } from '../../../utils/validation';
import {
  CreateProductData,
  ProductRecord,
  ProductRepository,
  UpdateProductData,
} from '../../../repositories/product.repository';
import { CreateProductDto, createProductSchema } from '../dtos/create-product.dto';
import { UpdateProductDto, updateProductSchema } from '../dtos/update-product.dto';

export class ProductService {
  constructor(private readonly productRepository: ProductRepository) {}

  async createProduct(data: CreateProductDto): Promise<ProductRecord> {
    const payload = parseWithSchema(createProductSchema, data, 'Invalid product data.');

    const existing = await this.productRepository.findBySku(payload.sku);
    if (existing) {
      throw new ConflictError('SKU already in use.');
    }

    const createData: CreateProductData = {
      name: payload.name,
      sku: payload.sku,
      description: payload.description,
      price: payload.price,
    };

    return this.productRepository.create(createData);
  }

  async getProductById(id: string): Promise<ProductRecord> {
    if (!id) {
      throw new ValidationError('Product id is required.');
    }

    const product = await this.productRepository.findById(id);

    if (!product) {
      throw new NotFoundError('Product not found.');
    }

    return product;
  }

  async getAllProducts(): Promise<ProductRecord[]> {
    return this.productRepository.findAll();
  }

  async updateProduct(id: string, data: UpdateProductDto): Promise<ProductRecord> {
    if (!id) {
      throw new ValidationError('Product id is required.');
    }

    const payload = parseWithSchema(updateProductSchema, data, 'Invalid product update payload.');
    const existingProduct = await this.getProductById(id);

    if (payload.sku && payload.sku !== existingProduct.sku) {
      const productWithSku = await this.productRepository.findBySku(payload.sku);
      if (productWithSku) {
        throw new ConflictError('SKU already in use.');
      }
    }

    const updateData: UpdateProductData = {};

    if (payload.name !== undefined) {
      updateData.name = payload.name;
    }

    if (payload.sku !== undefined) {
      updateData.sku = payload.sku;
    }

    if (payload.description !== undefined) {
      updateData.description = payload.description;
    }

    if (payload.price !== undefined) {
      updateData.price = payload.price;
    }

    return this.productRepository.update(id, updateData);
  }

  async deleteProduct(id: string): Promise<ProductRecord> {
    if (!id) {
      throw new ValidationError('Product id is required.');
    }

    await this.getProductById(id);
    return this.productRepository.delete(id);
  }
}
