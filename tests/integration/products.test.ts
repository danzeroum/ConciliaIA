import { jest } from '@jest/globals';
import { randomUUID } from 'crypto';
import jwt from 'jsonwebtoken';
import request from 'supertest';
import type { Express } from 'express';

interface MockProductRecord {
  id: string;
  name: string;
  sku: string;
  description: string | null;
  price: number;
  createdAt: Date;
  updatedAt: Date;
}

interface MockUserRecord {
  id: string;
  email: string;
  name: string | null;
  password: string;
  createdAt: Date;
  updatedAt: Date;
}

const products: MockProductRecord[] = [];
const users: MockUserRecord[] = [];

const productRepositoryMock = {
  async findAll(): Promise<MockProductRecord[]> {
    return [...products];
  },
  async findById(id: string): Promise<MockProductRecord | null> {
    return products.find((product) => product.id === id) ?? null;
  },
  async findBySku(sku: string): Promise<MockProductRecord | null> {
    return products.find((product) => product.sku === sku) ?? null;
  },
  async create(data: { name: string; sku: string; description?: string; price: number }): Promise<MockProductRecord> {
    const now = new Date();
    const product: MockProductRecord = {
      id: randomUUID(),
      name: data.name,
      sku: data.sku,
      description: data.description ?? null,
      price: data.price,
      createdAt: now,
      updatedAt: now,
    };

    products.push(product);
    return product;
  },
  async update(id: string, data: Partial<MockProductRecord>): Promise<MockProductRecord> {
    const index = products.findIndex((product) => product.id === id);
    if (index === -1) {
      throw new Error('Product not found');
    }

    const updated: MockProductRecord = {
      ...products[index],
      ...data,
      updatedAt: new Date(),
    };

    products[index] = updated;
    return updated;
  },
  async delete(id: string): Promise<MockProductRecord> {
    const index = products.findIndex((product) => product.id === id);
    if (index === -1) {
      throw new Error('Product not found');
    }

    const [removed] = products.splice(index, 1);
    return removed;
  },
};

const userRepositoryMock = {
  async findByEmail(email: string): Promise<MockUserRecord | null> {
    return users.find((user) => user.email === email) ?? null;
  },
  async create(data: { email: string; name: string; password: string }): Promise<MockUserRecord> {
    const now = new Date();
    const user: MockUserRecord = {
      id: randomUUID(),
      email: data.email,
      name: data.name ?? null,
      password: data.password,
      createdAt: now,
      updatedAt: now,
    };

    users.push(user);
    return user;
  },
  async findById(id: string): Promise<MockUserRecord | null> {
    return users.find((user) => user.id === id) ?? null;
  },
  async update(id: string, data: Partial<MockUserRecord>): Promise<MockUserRecord> {
    const index = users.findIndex((user) => user.id === id);
    if (index === -1) {
      throw new Error('User not found');
    }

    const updated: MockUserRecord = {
      ...users[index],
      ...data,
      updatedAt: new Date(),
    };

    users[index] = updated;
    return updated;
  },
};

const jestProductRepositoryMock = {
  findAll: jest.fn(productRepositoryMock.findAll),
  findById: jest.fn(productRepositoryMock.findById),
  findBySku: jest.fn(productRepositoryMock.findBySku),
  create: jest.fn(productRepositoryMock.create),
  update: jest.fn(productRepositoryMock.update),
  delete: jest.fn(productRepositoryMock.delete),
};

const jestUserRepositoryMock = {
  findByEmail: jest.fn(userRepositoryMock.findByEmail),
  create: jest.fn(userRepositoryMock.create),
  findById: jest.fn(userRepositoryMock.findById),
  update: jest.fn(userRepositoryMock.update),
};

jest.mock('../../src/repositories/product.repository', () => ({
  __esModule: true,
  productRepository: jestProductRepositoryMock,
  default: jestProductRepositoryMock,
}));

jest.mock('../../src/repositories/user.repository', () => ({
  __esModule: true,
  userRepository: jestUserRepositoryMock,
  default: jestUserRepositoryMock,
}));

const resetRepositories = () => {
  products.splice(0, products.length);
  users.splice(0, users.length);

  (Object.values(jestProductRepositoryMock) as jest.Mock[]).forEach((mock) => mock.mockClear());
  (Object.values(jestUserRepositoryMock) as jest.Mock[]).forEach((mock) => mock.mockClear());
};

let createApp: () => Express;

describe('Products integration', () => {
  let app: Express;
  let authToken: string;

  beforeAll(async () => {
    process.env.JWT_SECRET = 'test-secret';
    ({ createApp } = await import('../../src/app'));
  });

  beforeEach(() => {
    resetRepositories();
    app = createApp();
    authToken = jwt.sign({ userId: 'user-id', email: 'user@example.com' }, 'test-secret');
  });

  it('creates a product via POST /products', async () => {
    const response = await request(app)
      .post('/products')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'Test Product',
        sku: 'SKU-001',
        description: 'A product for testing',
        price: 99.99,
      })
      .expect(201);

    expect(response.body).toMatchObject({
      name: 'Test Product',
      sku: 'SKU-001',
      description: 'A product for testing',
    });
    expect(response.body).toHaveProperty('id');
    expect(jestProductRepositoryMock.create).toHaveBeenCalled();
  });

  it('lists products via GET /products', async () => {
    await request(app)
      .post('/products')
      .set('Authorization', `Bearer ${authToken}`)
      .send({ name: 'Product A', sku: 'SKU-A', price: 10 })
      .expect(201);

    await request(app)
      .post('/products')
      .set('Authorization', `Bearer ${authToken}`)
      .send({ name: 'Product B', sku: 'SKU-B', price: 20 })
      .expect(201);

    const response = await request(app).get('/products').expect(200);

    expect(Array.isArray(response.body)).toBe(true);
    expect(response.body).toHaveLength(2);
    expect(jestProductRepositoryMock.findAll).toHaveBeenCalled();
  });

  it('retrieves a product via GET /products/:id', async () => {
    const createResponse = await request(app)
      .post('/products')
      .set('Authorization', `Bearer ${authToken}`)
      .send({ name: 'Product C', sku: 'SKU-C', price: 30 })
      .expect(201);

    const { id } = createResponse.body;
    const response = await request(app).get(`/products/${id}`).expect(200);

    expect(response.body).toMatchObject({ id, name: 'Product C', sku: 'SKU-C' });
    expect(jestProductRepositoryMock.findById).toHaveBeenCalledWith(id);
  });

  it('updates a product via PATCH /products/:id', async () => {
    const createResponse = await request(app)
      .post('/products')
      .set('Authorization', `Bearer ${authToken}`)
      .send({ name: 'Product D', sku: 'SKU-D', price: 50 })
      .expect(201);

    const { id } = createResponse.body;
    const response = await request(app)
      .patch(`/products/${id}`)
      .set('Authorization', `Bearer ${authToken}`)
      .send({ price: 55 })
      .expect(200);

    expect(response.body).toMatchObject({ id, price: 55 });
    expect(jestProductRepositoryMock.update).toHaveBeenCalled();
  });

  it('deletes a product via DELETE /products/:id', async () => {
    const createResponse = await request(app)
      .post('/products')
      .set('Authorization', `Bearer ${authToken}`)
      .send({ name: 'Product E', sku: 'SKU-E', price: 70 })
      .expect(201);

    const { id } = createResponse.body;
    await request(app)
      .delete(`/products/${id}`)
      .set('Authorization', `Bearer ${authToken}`)
      .expect(200);

    expect(jestProductRepositoryMock.delete).toHaveBeenCalledWith(id);
    const listResponse = await request(app).get('/products').expect(200);
    expect(listResponse.body).toHaveLength(0);
  });
});
