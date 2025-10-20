import { jest } from '@jest/globals';

import { AppError, UnauthorizedError, ValidationError } from '../../../src/utils/errors';
import { AuthService, getJwtSecret } from '../../../src/modules/auth/services/auth.service';
import type { UserRepository } from '../../../src/repositories/user.repository';

jest.mock('bcryptjs', () => {
  const compareMock = jest.fn(async () => false);
  return { compare: compareMock };
});

jest.mock('jsonwebtoken', () => ({
  sign: jest.fn(),
}));

const { compare } = jest.requireMock('bcryptjs') as { compare: jest.Mock };
const { sign } = jest.requireMock('jsonwebtoken') as { sign: jest.Mock };

type UserRepositoryMethods = Pick<UserRepository, 'findByEmail'>;

type MockUserRepository = jest.Mocked<UserRepositoryMethods>;

const createRepository = (): MockUserRepository => ({
  findByEmail: jest.fn(),
});

describe('AuthService', () => {
  const now = new Date();
  const baseUser = {
    id: 'auth-user-id',
    email: 'auth@example.com',
    name: 'Auth User',
    password: 'hashed-password',
    createdAt: now,
    updatedAt: now,
  };

  beforeEach(() => {
    process.env.JWT_SECRET = 'test-secret';
    jest.clearAllMocks();
    compare.mockImplementation(async () => false);
  });

  it('authenticates user with valid credentials', async () => {
    const repository = createRepository();
    repository.findByEmail.mockResolvedValue(baseUser);
    compare.mockImplementation(async () => true);
    sign.mockReturnValue('signed-token');

    const service = new AuthService(repository as unknown as UserRepository);
    const result = await service.login({ email: baseUser.email, password: 'plain-password' });

    expect(repository.findByEmail).toHaveBeenCalledWith(baseUser.email);
    expect(compare).toHaveBeenCalledWith('plain-password', baseUser.password);
    expect(sign).toHaveBeenCalledWith(
      { userId: baseUser.id, email: baseUser.email },
      'test-secret',
      { expiresIn: '24h' },
    );
    expect(result).toEqual({
      token: 'signed-token',
      user: {
        id: baseUser.id,
        email: baseUser.email,
        name: baseUser.name,
        createdAt: baseUser.createdAt,
        updatedAt: baseUser.updatedAt,
      },
    });
  });

  it('throws UnauthorizedError when user is not found', async () => {
    const repository = createRepository();
    repository.findByEmail.mockResolvedValue(null);

    const service = new AuthService(repository as unknown as UserRepository);

    await expect(service.login({ email: baseUser.email, password: 'plain-password' })).rejects.toBeInstanceOf(
      UnauthorizedError,
    );
  });

  it('throws UnauthorizedError when password does not match', async () => {
    const repository = createRepository();
    repository.findByEmail.mockResolvedValue(baseUser);

    const service = new AuthService(repository as unknown as UserRepository);

    await expect(service.login({ email: baseUser.email, password: 'wrong-password' })).rejects.toBeInstanceOf(
      UnauthorizedError,
    );
  });

  it('validates login payload', async () => {
    const repository = createRepository();
    repository.findByEmail.mockResolvedValue(baseUser);
    compare.mockImplementation(async () => true);

    const service = new AuthService(repository as unknown as UserRepository);

    await expect(service.login({ email: 'not-an-email', password: '' })).rejects.toBeInstanceOf(ValidationError);
  });

  it('throws AppError when JWT secret is not set', () => {
    delete process.env.JWT_SECRET;

    expect(() => getJwtSecret()).toThrow(AppError);
    expect(() => new AuthService(createRepository() as unknown as UserRepository)).toThrow(AppError);
  });
});
