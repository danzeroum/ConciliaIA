import { BaseRepository } from './base.repository';

export interface UserRecord {
  id: string;
  email: string;
  name: string | null;
  password: string;
  createdAt: Date;
  updatedAt: Date;
}

export type CreateUserData = {
  email: string;
  name: string;
  password: string;
};

export type UpdateUserData = Partial<Pick<UserRecord, 'email' | 'name' | 'password'>>;

export class UserRepository extends BaseRepository {
  async findById(id: string): Promise<UserRecord | null> {
    return this.prisma.user.findUnique({
      where: { id },
    });
  }

  async findByEmail(email: string): Promise<UserRecord | null> {
    return this.prisma.user.findUnique({
      where: { email },
    });
  }

  async create(data: CreateUserData): Promise<UserRecord> {
    return this.prisma.user.create({
      data,
    });
  }

  async update(id: string, data: UpdateUserData): Promise<UserRecord> {
    return this.prisma.user.update({
      where: { id },
      data,
    });
  }
}

export const userRepository = new UserRepository();

export default userRepository;
