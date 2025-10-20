import { hash } from 'bcryptjs';
import { ZodError, ZodType } from 'zod';

import { ConflictError, NotFoundError, ValidationError } from '../../common/errors';
import { CreateUserDto, createUserSchema } from '../dtos/create-user.dto';
import { UpdateUserDto, updateUserSchema } from '../dtos/update-user.dto';
import { UpdateUserData, UserRecord, UserRepository } from '../../../repositories/user.repository';

export class UserService {
  constructor(private readonly userRepository: UserRepository) {}

  async createUser(data: CreateUserDto): Promise<UserRecord> {
    const payload = this.parseWithSchema(createUserSchema, data, 'Invalid user data.');

    const existing = await this.userRepository.findByEmail(payload.email);
    if (existing) {
      throw new ConflictError('Email already in use.');
    }

    const passwordHash = await this.hashPassword(payload.password);

    return this.userRepository.create({
      email: payload.email,
      name: payload.name,
      password: passwordHash,
    });
  }

  async getUserById(id: string): Promise<UserRecord> {
    if (!id) {
      throw new ValidationError('User id is required.');
    }

    const user = await this.userRepository.findById(id);

    if (!user) {
      throw new NotFoundError('User not found.');
    }

    return user;
  }

  async updateUser(id: string, data: UpdateUserDto): Promise<UserRecord> {
    if (!id) {
      throw new ValidationError('User id is required.');
    }

    const payload = this.parseWithSchema(updateUserSchema, data, 'Invalid user update payload.');
    const currentUser = await this.getUserById(id);

    if (payload.email && payload.email !== currentUser.email) {
      const userWithEmail = await this.userRepository.findByEmail(payload.email);
      if (userWithEmail) {
        throw new ConflictError('Email already in use.');
      }
    }

    const updateData: UpdateUserData = {};

    if (payload.email) {
      updateData.email = payload.email;
    }

    if (payload.name !== undefined) {
      updateData.name = payload.name;
    }

    if (payload.password) {
      updateData.password = await this.hashPassword(payload.password);
    }

    return this.userRepository.update(id, updateData);
  }

  private async hashPassword(password: string): Promise<string> {
    return hash(password, 10);
  }

  private parseWithSchema<T>(schema: ZodType<T>, data: unknown, fallbackMessage: string): T {
    try {
      return schema.parse(data);
    } catch (error) {
      if (error instanceof ZodError) {
        const firstIssue = error.issues[0];
        throw new ValidationError(firstIssue?.message ?? fallbackMessage);
      }

      throw error;
    }
  }
}
