import { describe, expect, it, beforeEach, vi } from 'vitest';

import { ConflictError, NotFoundError, ValidationError } from '../../../../src/utils/errors';
import { ProductService } from '../../../../src/modules/products/services/product.service';
import { ProductRepository } from '../../../../src/repositories/product.repository';

type MockedProductRepository = {
  findById: ReturnType<typeof vi.fn>;
  findBySku: ReturnType<typeof vi.fn>;
  findAll: ReturnType<typeof vi.fn>;
  create: ReturnType<typeof vi.fn>;
  update: ReturnType<typeof vi.fn>;
  delete: ReturnType<typeof vi.fn>;
};

describe('ProductService', () => {
  let repository: MockedProductRepository;
  let service: ProductService;

  beforeEach(() => {
    repository = {
      findById: vi.fn(),
      findBySku: vi.fn(),
      findAll: vi.fn(),
      create: vi.fn(),
      update: vi.fn(),
      delete: vi.fn(),
    };

    service = new ProductService(repository as unknown as ProductRepository);
  });

  it('should create a product when SKU is unique', async () => {
    repository.findBySku.mockResolvedValue(null);
    repository.create.mockImplementation(async (data) => ({
      id: 'product-1',
      ...data,
      createdAt: new Date(),
      updatedAt: new Date(),
    }));

    const result = await service.createProduct({
      name: 'Product 1',
      sku: 'SKU123',
      price: 100,
      description: 'Test product',
    });

    expect(repository.create).toHaveBeenCalled();
    expect(result.sku).toBe('SKU123');
  });

  it('should throw ConflictError when creating a product with duplicated SKU', async () => {
    repository.findBySku.mockResolvedValue({
      id: 'product-1',
      name: 'Existing',
      sku: 'SKU123',
      price: 100,
      description: 'Existing product',
      createdAt: new Date(),
      updatedAt: new Date(),
    });

    await expect(
      service.createProduct({
        name: 'Product 1',
        sku: 'SKU123',
        price: 100,
      }),
    ).rejects.toBeInstanceOf(ConflictError);
  });

  it('should retrieve a product by id', async () => {
    const product = {
      id: 'product-1',
      name: 'Product 1',
      sku: 'SKU123',
      price: 100,
      description: 'Test product',
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    repository.findById.mockResolvedValue(product);

    const result = await service.getProductById('product-1');

    expect(result).toEqual(product);
  });

  it('should throw NotFoundError when product does not exist', async () => {
    repository.findById.mockResolvedValue(null);

    await expect(service.getProductById('missing')).rejects.toBeInstanceOf(NotFoundError);
  });

  it('should list all products', async () => {
    repository.findAll.mockResolvedValue([
      {
        id: 'product-1',
        name: 'Product 1',
        sku: 'SKU123',
        price: 100,
        description: 'Test product',
        createdAt: new Date(),
        updatedAt: new Date(),
      },
    ]);

    const result = await service.getAllProducts();

    expect(result).toHaveLength(1);
  });

  it('should update an existing product', async () => {
    const product = {
      id: 'product-1',
      name: 'Product 1',
      sku: 'SKU123',
      price: 100,
      description: 'Test product',
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    repository.findById.mockResolvedValue(product);
    repository.findBySku.mockResolvedValue(null);
    repository.update.mockImplementation(async (_id, data) => ({
      ...product,
      ...data,
    }));

    const result = await service.updateProduct('product-1', {
      name: 'Updated Product',
    });

    expect(result.name).toBe('Updated Product');
  });

  it('should validate update payload before applying changes', async () => {
    await expect(service.updateProduct('product-1', {} as never)).rejects.toBeInstanceOf(ValidationError);
  });

  it('should throw ConflictError when updating SKU to an existing one', async () => {
    const product = {
      id: 'product-1',
      name: 'Product 1',
      sku: 'SKU123',
      price: 100,
      description: 'Test product',
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    repository.findById.mockResolvedValue(product);
    repository.findBySku.mockResolvedValue({
      ...product,
      id: 'product-2',
      sku: 'SKU999',
    });

    await expect(
      service.updateProduct('product-1', {
        sku: 'SKU999',
      }),
    ).rejects.toBeInstanceOf(ConflictError);
  });

  it('should delete an existing product', async () => {
    const product = {
      id: 'product-1',
      name: 'Product 1',
      sku: 'SKU123',
      price: 100,
      description: 'Test product',
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    repository.findById.mockResolvedValue(product);
    repository.delete.mockResolvedValue(product);

    const result = await service.deleteProduct('product-1');

    expect(result).toEqual(product);
  });

  it('should validate product id before deleting', async () => {
    await expect(service.deleteProduct('')).rejects.toBeInstanceOf(ValidationError);
  });
});
