import { jest } from '@jest/globals';
import { randomUUID } from 'crypto';
import request from 'supertest';
import type { Express } from 'express';

interface MockUserRecord {
  id: string;
  email: string;
  name: string | null;
  password: string;
  createdAt: Date;
  updatedAt: Date;
}

interface MockProductRecord {
  id: string;
  name: string;
  sku: string;
  description: string | null;
  price: number;
  createdAt: Date;
  updatedAt: Date;
}

const users: MockUserRecord[] = [];
const products: MockProductRecord[] = [];

const userRepositoryMock = {
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
  async findByEmail(email: string): Promise<MockUserRecord | null> {
    return users.find((user) => user.email === email) ?? null;
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

const productRepositoryMock = {
  async findAll(): Promise<MockProductRecord[]> {
    return [...products];
  },
  async findById(): Promise<MockProductRecord | null> {
    return null;
  },
  async findBySku(): Promise<MockProductRecord | null> {
    return null;
  },
  async create(): Promise<MockProductRecord> {
    const now = new Date();
    const product: MockProductRecord = {
      id: randomUUID(),
      name: 'placeholder',
      sku: randomUUID(),
      description: null,
      price: 0,
      createdAt: now,
      updatedAt: now,
    };
    products.push(product);
    return product;
  },
  async update(id: string): Promise<MockProductRecord> {
    const product = products.find((item) => item.id === id);
    if (!product) {
      throw new Error('Product not found');
    }
    return product;
  },
  async delete(id: string): Promise<MockProductRecord> {
    const index = products.findIndex((item) => item.id === id);
    if (index === -1) {
      throw new Error('Product not found');
    }
    const [removed] = products.splice(index, 1);
    return removed;
  },
};

const jestUserRepositoryMock = {
  create: jest.fn(userRepositoryMock.create),
  findByEmail: jest.fn(userRepositoryMock.findByEmail),
  findById: jest.fn(userRepositoryMock.findById),
  update: jest.fn(userRepositoryMock.update),
};

const jestProductRepositoryMock = {
  findAll: jest.fn(productRepositoryMock.findAll),
  findById: jest.fn(productRepositoryMock.findById),
  findBySku: jest.fn(productRepositoryMock.findBySku),
  create: jest.fn(productRepositoryMock.create),
  update: jest.fn(productRepositoryMock.update),
  delete: jest.fn(productRepositoryMock.delete),
};

jest.mock('../../src/repositories/user.repository', () => ({
  __esModule: true,
  userRepository: jestUserRepositoryMock,
  default: jestUserRepositoryMock,
}));

jest.mock('../../src/repositories/product.repository', () => ({
  __esModule: true,
  productRepository: jestProductRepositoryMock,
  default: jestProductRepositoryMock,
}));

const resetRepositories = () => {
  users.splice(0, users.length);
  products.splice(0, products.length);

  (Object.values(jestUserRepositoryMock) as jest.Mock[]).forEach((mock) => mock.mockClear());
  (Object.values(jestProductRepositoryMock) as jest.Mock[]).forEach((mock) => mock.mockClear());
};

let createApp: () => Express;

describe('Auth integration', () => {
  let app: Express;

  beforeAll(async () => {
    process.env.JWT_SECRET = 'test-secret';
    ({ createApp } = await import('../../src/app'));
  });

  beforeEach(() => {
    resetRepositories();
    app = createApp();
  });

  it('logs in a user with valid credentials', async () => {
    const email = 'login@example.com';
    const password = 'Password123!';

    await request(app)
      .post('/users')
      .send({ email, name: 'Login User', password })
      .expect(201);

    const response = await request(app)
      .post('/auth/login')
      .send({ email, password })
      .expect(200);

    expect(response.body).toHaveProperty('token');
    expect(response.body.user).toMatchObject({ email, name: 'Login User' });
    expect(response.body.user).not.toHaveProperty('password');
  });

  it('returns 401 when credentials are invalid', async () => {
    const email = 'invalid@example.com';
    const password = 'Password123!';

    await request(app)
      .post('/users')
      .send({ email, name: 'Invalid User', password })
      .expect(201);

    await request(app)
      .post('/auth/login')
      .send({ email, password: 'wrong-password' })
      .expect(401);
  });

  it('returns 401 when user does not exist', async () => {
    await request(app)
      .post('/auth/login')
      .send({ email: 'missing@example.com', password: 'Password123!' })
      .expect(401);
  });
});
