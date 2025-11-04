import { hash } from 'bcryptjs';

import { ConflictError, NotFoundError, ValidationError } from '../../../utils/errors';
import { parseWithSchema } from '../../../utils/validation';
import { CreateUserDto, createUserSchema } from '../dtos/create-user.dto';
import { UpdateUserDto, updateUserSchema } from '../dtos/update-user.dto';
import { UpdateUserData, UserRecord, UserRepository } from '../../../repositories/user.repository';

export class UserService {
  constructor(private readonly userRepository: UserRepository) {}

  async createUser(data: CreateUserDto): Promise<UserRecord> {
    const payload = parseWithSchema(createUserSchema, data, 'Invalid user data.');

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

    const payload = parseWithSchema(updateUserSchema, data, 'Invalid user update payload.');
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
}
