import { jest } from '@jest/globals';

import { ConflictError, NotFoundError, ValidationError } from '../../../src/utils/errors';
import { UserService } from '../../../src/modules/users/services/user.service';
import type { UserRepository } from '../../../src/repositories/user.repository';

jest.mock('bcryptjs', () => {
  const hashMock = jest.fn(async (_password: string, _salt: number) => 'hashed-password');
  return { hash: hashMock };
});

const { hash } = jest.requireMock('bcryptjs') as { hash: jest.Mock };

type UserRepositoryMethods = Pick<UserRepository, 'findByEmail' | 'findById' | 'create' | 'update'>;

type MockUserRepository = jest.Mocked<UserRepositoryMethods>;

const createRepository = (): MockUserRepository => ({
  findByEmail: jest.fn(),
  findById: jest.fn(),
  create: jest.fn(),
  update: jest.fn(),
});

describe('UserService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const buildService = (repository: MockUserRepository): UserService =>
    new UserService(repository as unknown as UserRepository);

  const createUserRecord = (overrides: Partial<ReturnType<typeof baseUserRecord>> = {}) => ({
    ...baseUserRecord(),
    ...overrides,
  });

  function baseUserRecord() {
    const now = new Date();
    return {
      id: 'user-id',
      email: 'jane.doe@example.com',
      name: 'Jane Doe',
      password: 'stored-password',
      createdAt: now,
      updatedAt: now,
    };
  }

  it('hashes password and creates user when email is available', async () => {
    const repository = createRepository();
    const now = new Date();

    repository.findByEmail.mockResolvedValue(null);
    repository.create.mockImplementation(async (data) => ({
      id: 'new-user-id',
      email: data.email,
      name: data.name ?? null,
      password: data.password,
      createdAt: now,
      updatedAt: now,
    }));

    const service = buildService(repository);

    const result = await service.createUser({
      email: 'john.doe@example.com',
      name: 'John Doe',
      password: 'my-secret',
    });

    expect(repository.findByEmail).toHaveBeenCalledWith('john.doe@example.com');
    expect(hash).toHaveBeenCalledWith('my-secret', 10);
    expect(repository.create).toHaveBeenCalledWith({
      email: 'john.doe@example.com',
      name: 'John Doe',
      password: 'hashed-password',
    });
    expect(result).toEqual({
      id: 'new-user-id',
      email: 'john.doe@example.com',
      name: 'John Doe',
      password: 'hashed-password',
      createdAt: now,
      updatedAt: now,
    });
  });

  it('throws ConflictError when email already exists', async () => {
    const repository = createRepository();
    repository.findByEmail.mockResolvedValue(baseUserRecord());

    const service = buildService(repository);

    await expect(
      service.createUser({ email: 'jane.doe@example.com', name: 'Jane', password: 'secret123' }),
    ).rejects.toBeInstanceOf(ConflictError);

    expect(repository.create).not.toHaveBeenCalled();
  });

  it('returns user when found by id', async () => {
    const repository = createRepository();
    const user = createUserRecord({ id: 'existing-id' });
    repository.findById.mockResolvedValue(user);

    const service = buildService(repository);

    await expect(service.getUserById('existing-id')).resolves.toEqual(user);
    expect(repository.findById).toHaveBeenCalledWith('existing-id');
  });

  it('throws ValidationError when id is empty', async () => {
    const repository = createRepository();
    const service = buildService(repository);

    await expect(service.getUserById('')).rejects.toBeInstanceOf(ValidationError);
    expect(repository.findById).not.toHaveBeenCalled();
  });

  it('throws NotFoundError when user does not exist', async () => {
    const repository = createRepository();
    repository.findById.mockResolvedValue(null);

    const service = buildService(repository);

    await expect(service.getUserById('missing-id')).rejects.toBeInstanceOf(NotFoundError);
  });

  it('updates user and rehashes password when provided', async () => {
    const repository = createRepository();
    const originalUser = createUserRecord({
      id: 'update-id',
      email: 'jane.doe@example.com',
      name: 'Jane Doe',
    });

    repository.findById.mockResolvedValue(originalUser);
    repository.findByEmail.mockResolvedValueOnce(null);

    repository.update.mockImplementation(async (_id, data) => ({
      ...originalUser,
      ...data,
      updatedAt: new Date(),
    }));

    const service = buildService(repository);

    const result = await service.updateUser('update-id', {
      email: 'new.email@example.com',
      name: 'Jane Updated',
      password: 'new-password',
    });

    expect(repository.findById).toHaveBeenCalledWith('update-id');
    expect(repository.findByEmail).toHaveBeenCalledWith('new.email@example.com');
    expect(hash).toHaveBeenCalledWith('new-password', 10);
    expect(repository.update).toHaveBeenCalledWith(
      'update-id',
      expect.objectContaining({
        email: 'new.email@example.com',
        name: 'Jane Updated',
        password: 'hashed-password',
      }),
    );
    expect(result.email).toBe('new.email@example.com');
    expect(result.name).toBe('Jane Updated');
  });

  it('throws ValidationError when updating without id', async () => {
    const repository = createRepository();
    const service = buildService(repository);

    await expect(
      service.updateUser('', { email: 'jane.doe@example.com' }),
    ).rejects.toBeInstanceOf(ValidationError);
    expect(repository.update).not.toHaveBeenCalled();
  });

  it('throws ConflictError when updating with an email already used by another user', async () => {
    const repository = createRepository();
    const existingUser = createUserRecord({ id: 'user-1' });
    const conflictingUser = createUserRecord({ id: 'user-2', email: 'taken@example.com' });

    repository.findById.mockResolvedValue(existingUser);
    repository.findByEmail.mockResolvedValue(conflictingUser);

    const service = buildService(repository);

    await expect(
      service.updateUser('user-1', { email: 'taken@example.com' }),
    ).rejects.toBeInstanceOf(ConflictError);
    expect(repository.update).not.toHaveBeenCalled();
  });

  it('updates user without password and keeps existing hash', async () => {
    const repository = createRepository();
    const existingUser = createUserRecord({ id: 'user-1' });

    repository.findById.mockResolvedValue(existingUser);
    repository.findByEmail.mockResolvedValue(null);
    repository.update.mockImplementation(async (_id, data) => ({
      ...existingUser,
      ...data,
      updatedAt: new Date(),
    }));

    const service = buildService(repository);

    const result = await service.updateUser('user-1', { name: 'Updated Name' });

    expect(hash).not.toHaveBeenCalled();
    expect(repository.update).toHaveBeenCalledWith(
      'user-1',
      expect.objectContaining({ name: 'Updated Name' }),
    );
    expect(result.name).toBe('Updated Name');
  });

  it('skips email uniqueness check when email remains unchanged', async () => {
    const repository = createRepository();
    const existingUser = createUserRecord({ id: 'user-1' });

    repository.findById.mockResolvedValue(existingUser);
    repository.update.mockImplementation(async (_id, data) => ({
      ...existingUser,
      ...data,
      updatedAt: new Date(),
    }));

    const service = buildService(repository);

    await service.updateUser('user-1', { name: 'Same Email Name' });

    expect(repository.findByEmail).not.toHaveBeenCalled();
  });
});
