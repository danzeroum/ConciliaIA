import { compare } from 'bcryptjs';
import jwt from 'jsonwebtoken';

import { AppError, UnauthorizedError } from '../../../utils/errors';
import { parseWithSchema } from '../../../utils/validation';
import { LoginDto, loginSchema } from '../dtos/login.dto';
import { UserRecord, UserRepository } from '../../../repositories/user.repository';

export type AuthenticatedUser = Omit<UserRecord, 'password'>;

export interface AuthResult {
  token: string;
  user: AuthenticatedUser;
}

export const getJwtSecret = (): string => {
  const secret = process.env.JWT_SECRET;

  if (!secret) {
    throw new AppError('JWT_SECRET environment variable is not defined.', 500);
  }

  return secret;
};

export class AuthService {
  private readonly jwtSecret: string;

  constructor(private readonly userRepository: UserRepository) {
    this.jwtSecret = getJwtSecret();
  }

  async login(data: LoginDto): Promise<AuthResult> {
    const payload = parseWithSchema(loginSchema, data, 'Invalid login credentials.');

    const user = await this.userRepository.findByEmail(payload.email);
    if (!user) {
      throw new UnauthorizedError('Invalid email or password.');
    }

    const isPasswordValid = await compare(payload.password, user.password);
    if (!isPasswordValid) {
      throw new UnauthorizedError('Invalid email or password.');
    }

    const token = jwt.sign(
      {
        userId: user.id,
        email: user.email,
      },
      this.jwtSecret,
      { expiresIn: '24h' },
    );

    const { password, ...userWithoutPassword } = user;

    return {
      token,
      user: userWithoutPassword,
    };
  }
}
