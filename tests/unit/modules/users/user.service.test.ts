import { describe, expect, it, beforeEach, vi } from 'vitest';
import { compareSync } from 'bcryptjs';

import { ConflictError, NotFoundError, ValidationError } from '../../../../src/modules/common/errors';
import { UserService } from '../../../../src/modules/users/services/user.service';
import { UserRepository } from '../../../../src/repositories/user.repository';

type MockedUserRepository = {
  findByEmail: ReturnType<typeof vi.fn>;
  findById: ReturnType<typeof vi.fn>;
  create: ReturnType<typeof vi.fn>;
  update: ReturnType<typeof vi.fn>;
};

describe('UserService', () => {
  let repository: MockedUserRepository;
  let service: UserService;

  beforeEach(() => {
    repository = {
      findByEmail: vi.fn(),
      findById: vi.fn(),
      create: vi.fn(),
      update: vi.fn(),
    };

    service = new UserService(repository as unknown as UserRepository);
  });

  it('should create a user with hashed password when email is unique', async () => {
    repository.findByEmail.mockResolvedValue(null);
    repository.create.mockImplementation(async (data) => ({
      id: 'user-1',
      email: data.email,
      name: data.name,
      password: data.password,
      createdAt: new Date(),
      updatedAt: new Date(),
    }));

    const result = await service.createUser({
      email: 'user@example.com',
      password: 'SecurePass123',
      name: 'John Doe',
    });

    expect(repository.create).toHaveBeenCalled();
    expect(result.password).not.toBe('SecurePass123');
    expect(compareSync('SecurePass123', result.password)).toBe(true);
  });

  it('should throw ConflictError when creating a user with an existing email', async () => {
    repository.findByEmail.mockResolvedValue({
      id: 'user-1',
      email: 'user@example.com',
      name: 'Existing',
      password: 'hash',
      createdAt: new Date(),
      updatedAt: new Date(),
    });

    await expect(
      service.createUser({
        email: 'user@example.com',
        password: 'SecurePass123',
        name: 'John Doe',
      }),
    ).rejects.toBeInstanceOf(ConflictError);
  });

  it('should retrieve a user by id', async () => {
    const user = {
      id: 'user-1',
      email: 'user@example.com',
      name: 'John Doe',
      password: 'hash',
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    repository.findById.mockResolvedValue(user);

    const result = await service.getUserById('user-1');

    expect(result).toEqual(user);
  });

  it('should throw NotFoundError when user does not exist', async () => {
    repository.findById.mockResolvedValue(null);

    await expect(service.getUserById('missing')).rejects.toBeInstanceOf(NotFoundError);
  });

  it('should throw ValidationError when id is not provided', async () => {
    await expect(service.getUserById('')).rejects.toBeInstanceOf(ValidationError);
  });

  it('should update a user and hash password when provided', async () => {
    const existingUser = {
      id: 'user-1',
      email: 'user@example.com',
      name: 'John Doe',
      password: 'hash',
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    repository.findById.mockResolvedValue(existingUser);
    repository.update.mockImplementation(async (_id, data) => ({
      ...existingUser,
      ...data,
    }));
    repository.findByEmail.mockResolvedValue(null);

    const result = await service.updateUser('user-1', {
      password: 'NewSecurePass123',
    });

    expect(repository.update).toHaveBeenCalled();
    expect(result.password).not.toBe('NewSecurePass123');
    expect(compareSync('NewSecurePass123', result.password as string)).toBe(true);
  });

  it('should validate update payload before applying changes', async () => {
    await expect(service.updateUser('user-1', {} as never)).rejects.toBeInstanceOf(ValidationError);
  });

  it('should throw ConflictError when updating email to an existing one', async () => {
    const existingUser = {
      id: 'user-1',
      email: 'user@example.com',
      name: 'John Doe',
      password: 'hash',
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    repository.findById.mockResolvedValue(existingUser);
    repository.findByEmail.mockResolvedValue({
      ...existingUser,
      id: 'user-2',
      email: 'new@example.com',
    });

    await expect(
      service.updateUser('user-1', {
        email: 'new@example.com',
      }),
    ).rejects.toBeInstanceOf(ConflictError);
  });
});
