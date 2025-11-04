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

const users: MockUserRecord[] = [];

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
  async findById(id: string): Promise<MockUserRecord | null> {
    return users.find((user) => user.id === id) ?? null;
  },
  async findByEmail(email: string): Promise<MockUserRecord | null> {
    return users.find((user) => user.email === email) ?? null;
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

const jestUserRepositoryMock = {
  create: jest.fn(userRepositoryMock.create),
  findById: jest.fn(userRepositoryMock.findById),
  findByEmail: jest.fn(userRepositoryMock.findByEmail),
  update: jest.fn(userRepositoryMock.update),
};

jest.mock('../../src/repositories/user.repository', () => ({
  __esModule: true,
  userRepository: jestUserRepositoryMock,
  default: jestUserRepositoryMock,
}));

const productRepositoryStub = {
  findAll: jest.fn(async () => []),
  findById: jest.fn(async () => null),
  findBySku: jest.fn(async () => null),
  create: jest.fn(),
  update: jest.fn(),
  delete: jest.fn(),
};

jest.mock('../../src/repositories/product.repository', () => ({
  __esModule: true,
  productRepository: productRepositoryStub,
  default: productRepositoryStub,
}));

const resetRepository = () => {
  users.splice(0, users.length);
  jestUserRepositoryMock.create.mockClear();
  jestUserRepositoryMock.findById.mockClear();
  jestUserRepositoryMock.findByEmail.mockClear();
  jestUserRepositoryMock.update.mockClear();
};

let createApp: () => Express;

describe('Users integration', () => {
  let app: Express;

  beforeAll(async () => {
    process.env.JWT_SECRET = 'test-secret';
    ({ createApp } = await import('../../src/app'));
  });

  beforeEach(() => {
    resetRepository();
    app = createApp();
  });

  it('creates a user via POST /users', async () => {
    const response = await request(app)
      .post('/users')
      .send({ email: 'new.user@example.com', name: 'New User', password: 'password123' })
      .expect(201);

    expect(response.body).toMatchObject({
      email: 'new.user@example.com',
      name: 'New User',
    });
    expect(response.body).toHaveProperty('id');
    expect(response.body).not.toHaveProperty('password');
    expect(jestUserRepositoryMock.create).toHaveBeenCalled();
  });

  it('retrieves a user via GET /users/:id', async () => {
    const createResponse = await request(app)
      .post('/users')
      .send({ email: 'jane.doe@example.com', name: 'Jane Doe', password: 'password123' })
      .expect(201);

    const { id } = createResponse.body;
    const getResponse = await request(app).get(`/users/${id}`).expect(200);

    expect(getResponse.body).toMatchObject({
      id,
      email: 'jane.doe@example.com',
      name: 'Jane Doe',
    });
    expect(getResponse.body).not.toHaveProperty('password');
    expect(jestUserRepositoryMock.findById).toHaveBeenCalledWith(id);
  });
});
