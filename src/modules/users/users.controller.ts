import { NextFunction, Request, Response, Router } from 'express';

import { parseWithSchema } from '../../utils/validation';
import { authMiddleware } from '../../middleware/auth.middleware';
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
    this.router.patch('/users/:id', authMiddleware, this.updateUser);
  }

  private createUser = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const payload = parseWithSchema(createUserSchema, req.body, 'Invalid request body.');
      const user = await this.userService.createUser(payload);
      const { password, ...userWithoutPassword } = user;
      res.status(201).json(userWithoutPassword);
    } catch (error) {
      next(error);
    }
  };

  private getUserById = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const user = await this.userService.getUserById(req.params.id);
      const { password, ...userWithoutPassword } = user;
      res.status(200).json(userWithoutPassword);
    } catch (error) {
      next(error);
    }
  };

  private updateUser = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const payload = parseWithSchema(updateUserSchema, req.body, 'Invalid request body.');
      const user = await this.userService.updateUser(req.params.id, payload);
      const { password, ...userWithoutPassword } = user;
      res.status(200).json(userWithoutPassword);
    } catch (error) {
      next(error);
    }
  };
}

export default UsersController;
