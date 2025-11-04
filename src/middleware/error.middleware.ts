import { NextFunction, Request, Response } from 'express';

import { AppError } from '../utils/errors';

const logger = {
  error: (...args: unknown[]): void => {
    console.error(...args);
  },
};

const logError = (error: unknown): void => {
  const isProduction = process.env.NODE_ENV === 'production';

  if (isProduction) {
    logger.error(error);
    return;
  }

  console.error(error);
};

export const errorMiddleware = (
  error: unknown,
  _req: Request,
  res: Response,
  _next: NextFunction,
): Response => {
  const timestamp = new Date().toISOString();

  if (error instanceof AppError) {
    logError(error);

    const responseBody: Record<string, unknown> = {
      error: error.message,
      statusCode: error.statusCode,
      timestamp,
    };

    if (error.details) {
      responseBody.details = error.details;
    }

    return res.status(error.statusCode).json(responseBody);
  }

  logError(error);

  const message = error instanceof Error ? error.message : 'Internal server error.';

  return res.status(500).json({
    error: process.env.NODE_ENV === 'production' ? 'Internal server error.' : message,
    statusCode: 500,
    timestamp,
  });
};

export default errorMiddleware;
