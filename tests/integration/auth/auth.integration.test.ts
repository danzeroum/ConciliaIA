import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('../../../src/lib/prisma', () => ({
  default: {},
}));

import express from 'express';
import request from 'supertest';
import { hash } from 'bcryptjs';

import AuthController from '../../../src/modules/auth/auth.controller';
import { AuthService } from '../../../src/modules/auth/services/auth.service';
import UsersController from '../../../src/modules/users/users.controller';
import { UserService } from '../../../src/modules/users/services/user.service';
import { UserRecord, UserRepository } from '../../../src/repositories/user.repository';
import { authMiddleware } from '../../../src/middleware/auth.middleware';
import errorMiddleware from '../../../src/middleware/error.middleware';

const buildTestApp = async () => {
  const app = express();
  app.use(express.json());

  const passwordHash = await hash('StrongPass123', 10);

  const user: UserRecord = {
    id: 'user-1',
    email: 'user@example.com',
    name: 'Jane Doe',
    password: passwordHash,
    createdAt: new Date(),
    updatedAt: new Date(),
  };

  const findByEmail = vi.fn(async (email: string) => (email === user.email ? user : null));

  const userRepository: Pick<UserRepository, 'findByEmail'> = {
    findByEmail,
  };

  const authService = new AuthService(userRepository as UserRepository);
  const authController = new AuthController(authService);

  const usersService = {
    createUser: vi.fn(),
    getUserById: vi.fn(),
    updateUser: vi.fn(async (_id: string, data: Record<string, unknown>) => ({
      ...user,
      ...data,
      updatedAt: new Date(),
    })),
  };

  const usersController = new UsersController(usersService as unknown as UserService);

  app.use(authController.router);
  app.use(usersController.router);
  app.get('/protected', authMiddleware, (req, res) => {
    return res.status(200).json({ user: req.user });
  });
  app.use(errorMiddleware);

  return { app, user, usersService, findByEmail };
};

describe('Authentication integration', () => {
  beforeEach(() => {
    process.env.JWT_SECRET = 'test-secret';
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('logs in successfully with valid credentials and returns a JWT token', async () => {
    const { app, user, findByEmail } = await buildTestApp();

    const response = await request(app).post('/auth/login').send({
      email: user.email,
      password: 'StrongPass123',
    });

    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('token');
    expect(response.body.user).toMatchObject({
      id: user.id,
      email: user.email,
      name: user.name,
    });
    expect(response.body.user).not.toHaveProperty('password');
    expect(findByEmail).toHaveBeenCalledWith(user.email);
  });

  it('rejects login attempts with invalid credentials', async () => {
    const { app } = await buildTestApp();

    const response = await request(app).post('/auth/login').send({
      email: 'user@example.com',
      password: 'WrongPassword',
    });

    expect(response.status).toBe(401);
    expect(response.body).toMatchObject({
      error: 'Invalid email or password.',
      statusCode: 401,
    });
    expect(response.body).toHaveProperty('timestamp');
  });

  it('blocks access to protected user update routes without a token', async () => {
    const { app } = await buildTestApp();

    const response = await request(app).patch('/users/user-1').send({ name: 'New Name' });

    expect(response.status).toBe(401);
    expect(response.body).toMatchObject({
      error: 'Unauthorized.',
      statusCode: 401,
    });
    expect(response.body).toHaveProperty('timestamp');
  });

  it('allows access to protected routes when a valid token is provided', async () => {
    const { app, user, usersService } = await buildTestApp();

    const loginResponse = await request(app).post('/auth/login').send({
      email: user.email,
      password: 'StrongPass123',
    });

    const token = loginResponse.body.token as string;

    const response = await request(app)
      .patch('/users/user-1')
      .set('Authorization', `Bearer ${token}`)
      .send({ name: 'Updated Name' });

    expect(response.status).toBe(200);
    expect(usersService.updateUser).toHaveBeenCalledWith('user-1', { name: 'Updated Name' });
    expect(response.body).toMatchObject({
      id: user.id,
      email: user.email,
      name: 'Updated Name',
    });
    expect(response.body).not.toHaveProperty('password');
  });

  it('attaches the authenticated user to the request object', async () => {
    const { app, user } = await buildTestApp();

    const loginResponse = await request(app).post('/auth/login').send({
      email: user.email,
      password: 'StrongPass123',
    });

    const token = loginResponse.body.token as string;

    const response = await request(app)
      .get('/protected')
      .set('Authorization', `Bearer ${token}`);

    expect(response.status).toBe(200);
    expect(response.body).toEqual({
      user: {
        userId: user.id,
        email: user.email,
      },
    });
  });
});
