import { NextFunction, Request, Response, Router } from 'express';

import { parseWithSchema } from '../../utils/validation';
import { AuthService } from './services/auth.service';
import { loginSchema } from './dtos/login.dto';

/**
 * @swagger
 * tags:
 *   - name: Auth
 *     description: Authentication endpoints
 */

export class AuthController {
  public readonly router: Router;

  constructor(private readonly authService: AuthService) {
    this.router = Router();
    this.registerRoutes();
  }

  private registerRoutes(): void {
    /**
     * @swagger
     * /auth/login:
     *   post:
     *     summary: Authenticate user and issue JWT token
     *     tags: [Auth]
     *     requestBody:
     *       required: true
     *       content:
     *         application/json:
     *           schema:
     *             $ref: '#/components/schemas/AuthLoginInput'
     *     responses:
     *       200:
     *         description: Authentication successful
     *         content:
     *           application/json:
     *             schema:
     *               $ref: '#/components/schemas/AuthResponse'
     *       400:
     *         description: Validation error
     *         content:
     *           application/json:
     *             schema:
     *               $ref: '#/components/schemas/ErrorResponse'
     *       401:
     *         description: Invalid credentials
     *         content:
     *           application/json:
     *             schema:
     *               $ref: '#/components/schemas/ErrorResponse'
     */
    this.router.post('/auth/login', this.login);
  }

  private login = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const payload = parseWithSchema(loginSchema, req.body, 'Invalid request body.');
      const result = await this.authService.login(payload);
      res.status(200).json(result);
    } catch (error) {
      next(error);
    }
  };
}

export default AuthController;
