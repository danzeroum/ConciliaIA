import { Request, Response, Router } from 'express';

import { ApplicationError } from '../common/errors';
import { createUserSchema } from './dtos/create-user.dto';
import { updateUserSchema } from './dtos/update-user.dto';
import { UserService } from './services/user.service';

export class UsersController {
  public readonly router: Router;

  constructor(private readonly userService: UserService) {
    this.router = Router();
    this.registerRoutes();
  }

  private registerRoutes(): void {
    this.router.post('/users', this.createUser);
    this.router.get('/users/:id', this.getUserById);
    this.router.patch('/users/:id', this.updateUser);
  }

  private createUser = async (req: Request, res: Response): Promise<Response> => {
    const validation = createUserSchema.safeParse(req.body);

    if (!validation.success) {
      return res.status(400).json({
        message: 'Invalid request body.',
        errors: validation.error.flatten(),
      });
    }

    try {
      const user = await this.userService.createUser(validation.data);
      const { password, ...userWithoutPassword } = user;
      return res.status(201).json(userWithoutPassword);
    } catch (error) {
      return this.handleError(res, error);
    }
  };

  private getUserById = async (req: Request, res: Response): Promise<Response> => {
    try {
      const user = await this.userService.getUserById(req.params.id);
      const { password, ...userWithoutPassword } = user;
      return res.status(200).json(userWithoutPassword);
    } catch (error) {
      return this.handleError(res, error);
    }
  };

  private updateUser = async (req: Request, res: Response): Promise<Response> => {
    const validation = updateUserSchema.safeParse(req.body);

    if (!validation.success) {
      return res.status(400).json({
        message: 'Invalid request body.',
        errors: validation.error.flatten(),
      });
    }

    try {
      const user = await this.userService.updateUser(req.params.id, validation.data);
      const { password, ...userWithoutPassword } = user;
      return res.status(200).json(userWithoutPassword);
    } catch (error) {
      return this.handleError(res, error);
    }
  };

  private handleError(res: Response, error: unknown): Response {
    if (error instanceof ApplicationError) {
      return res.status(error.statusCode).json({ message: error.message });
    }

    console.error('Unexpected error in UsersController', error);
    return res.status(500).json({ message: 'Internal server error.' });
  }
}

export default UsersController;
