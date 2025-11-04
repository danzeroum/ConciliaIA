import { ZodError, ZodType } from 'zod';

import { ValidationError } from './errors';

export const parseWithSchema = <T>(
  schema: ZodType<T>,
  data: unknown,
  fallbackMessage: string,
): T => {
  try {
    return schema.parse(data);
  } catch (error) {
    if (error instanceof ZodError) {
      const message = error.issues[0]?.message ?? fallbackMessage;
      throw new ValidationError(message, error.flatten());
    }

    throw error;
  }
};
