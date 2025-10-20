import { AppError, ConflictError, NotFoundError, UnauthorizedError, ValidationError } from '../../../src/utils/errors';

describe('Error utilities', () => {
  it('creates an AppError with message, status code and details', () => {
    const details = { field: 'email' };
    const error = new AppError('Something went wrong', 422, details);

    expect(error).toBeInstanceOf(Error);
    expect(error.message).toBe('Something went wrong');
    expect(error.statusCode).toBe(422);
    expect(error.details).toEqual(details);
    expect(error.name).toBe('AppError');
  });

  it('creates specific HTTP errors with default status codes', () => {
    const validation = new ValidationError('Invalid input');
    const notFound = new NotFoundError('Resource missing');
    const unauthorized = new UnauthorizedError('Unauthorized');
    const conflict = new ConflictError('Conflict detected');

    expect(validation.statusCode).toBe(400);
    expect(notFound.statusCode).toBe(404);
    expect(unauthorized.statusCode).toBe(401);
    expect(conflict.statusCode).toBe(409);

    expect(validation).toBeInstanceOf(AppError);
    expect(notFound).toBeInstanceOf(AppError);
    expect(unauthorized).toBeInstanceOf(AppError);
    expect(conflict).toBeInstanceOf(AppError);
  });
});
