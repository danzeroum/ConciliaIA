import { NextFunction, Request, Response } from 'express';
import jwt from 'jsonwebtoken';

import { AppError, UnauthorizedError } from '../utils/errors';
import { getJwtSecret } from '../modules/auth/services/auth.service';

export interface RequestUser {
  userId: string;
  email: string;
}

declare module 'express-serve-static-core' {
  interface Request {
    user?: RequestUser;
  }
}

export const authMiddleware = (req: Request, res: Response, next: NextFunction): void => {
  const authHeader = req.headers.authorization;

  if (!authHeader?.startsWith('Bearer ')) {
    next(new UnauthorizedError('Unauthorized.'));
    return;
  }

  const token = authHeader.slice(7);

  try {
    const secret = getJwtSecret();
    const decoded = jwt.verify(token, secret);

    if (typeof decoded !== 'object' || decoded === null) {
      throw new UnauthorizedError('Invalid token payload.');
    }

    const { userId, email } = decoded as jwt.JwtPayload & RequestUser;

    if (!userId || !email) {
      throw new UnauthorizedError('Invalid token payload.');
    }

    req.user = { userId: String(userId), email: String(email) };

    next();
  } catch (error) {
    if (error instanceof UnauthorizedError) {
      next(error);
      return;
    }

    if (error instanceof jwt.TokenExpiredError) {
      next(new UnauthorizedError('Token expired.'));
      return;
    }

    if (error instanceof jwt.JsonWebTokenError) {
      next(new UnauthorizedError('Invalid token.'));
      return;
    }

    next(error instanceof Error ? error : new AppError('Failed to authenticate request.', 500));
  }
};

export default authMiddleware;
