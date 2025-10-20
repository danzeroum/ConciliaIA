import { Request, Response, Router } from 'express';

import { ApplicationError } from '../common/errors';
import { AuthService } from './services/auth.service';
import { loginSchema } from './dtos/login.dto';

export class AuthController {
  public readonly router: Router;

  constructor(private readonly authService: AuthService) {
    this.router = Router();
    this.registerRoutes();
  }

  private registerRoutes(): void {
    this.router.post('/auth/login', this.login);
  }

  private login = async (req: Request, res: Response): Promise<Response> => {
    const validation = loginSchema.safeParse(req.body);

    if (!validation.success) {
      return res.status(400).json({
        message: 'Invalid request body.',
        errors: validation.error.flatten(),
      });
    }

    try {
      const result = await this.authService.login(validation.data);
      return res.status(200).json(result);
    } catch (error) {
      return this.handleError(res, error);
    }
  };

  private handleError(res: Response, error: unknown): Response {
    if (error instanceof ApplicationError) {
      return res.status(error.statusCode).json({ message: error.message });
    }

    console.error('Unexpected error in AuthController', error);
    return res.status(500).json({ message: 'Internal server error.' });
  }
}

export default AuthController;
