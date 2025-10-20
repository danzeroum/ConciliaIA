import { Prisma, User } from '@prisma/client';

import { BaseRepository } from './base.repository';

export class UserRepository extends BaseRepository {
  async findById(id: string): Promise<User | null> {
    return this.prisma.user.findUnique({
      where: { id },
    });
  }

  async findByEmail(email: string): Promise<User | null> {
    return this.prisma.user.findUnique({
      where: { email },
    });
  }

  async create(data: Prisma.UserCreateInput): Promise<User> {
    return this.prisma.user.create({
      data,
    });
  }
}

export const userRepository = new UserRepository();

export default userRepository;
