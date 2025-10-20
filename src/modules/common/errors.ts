export class ApplicationError extends Error {
  constructor(message: string, public readonly statusCode: number) {
    super(message);
    this.name = this.constructor.name;
  }
}

export class ValidationError extends ApplicationError {
  constructor(message: string) {
    super(message, 400);
  }
}

export class ConflictError extends ApplicationError {
  constructor(message: string) {
    super(message, 400);
  }
}

export class NotFoundError extends ApplicationError {
  constructor(message: string) {
    super(message, 404);
  }
}

export class UnauthorizedError extends ApplicationError {
  constructor(message: string) {
    super(message, 401);
  }
}
