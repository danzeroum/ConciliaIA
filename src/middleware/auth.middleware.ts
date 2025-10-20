import { NextFunction, Request, Response } from 'express';
import jwt from 'jsonwebtoken';

import { getJwtSecret } from '../modules/auth/services/auth.service';
import { UnauthorizedError } from '../modules/common/errors';

export interface RequestUser {
  userId: string;
  email: string;
}

declare module 'express-serve-static-core' {
  interface Request {
    user?: RequestUser;
  }
}

export const authMiddleware = (req: Request, res: Response, next: NextFunction): Response | void => {
  const authHeader = req.headers.authorization;

  if (!authHeader?.startsWith('Bearer ')) {
    return res.status(401).json({ message: 'Unauthorized.' });
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
      return res.status(error.statusCode).json({ message: error.message });
    }

    if (error instanceof jwt.TokenExpiredError) {
      return res.status(401).json({ message: 'Token expired.' });
    }

    if (error instanceof jwt.JsonWebTokenError) {
      return res.status(401).json({ message: 'Invalid token.' });
    }

    console.error('Failed to authenticate request', error);
    return res.status(500).json({ message: 'Internal server error.' });
  }
};

export default authMiddleware;
