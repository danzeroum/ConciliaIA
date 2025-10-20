import express, { Express } from 'express';

import { swaggerUiServe, swaggerUiSetup } from './docs/swagger';
import errorMiddleware from './middleware/error.middleware';
import AuthController from './modules/auth/auth.controller';
import { AuthService } from './modules/auth/services/auth.service';
import ProductsController from './modules/products/products.controller';
import { ProductService } from './modules/products/services/product.service';
import UsersController from './modules/users/users.controller';
import { UserService } from './modules/users/services/user.service';
import productRepository from './repositories/product.repository';
import userRepository from './repositories/user.repository';

export const createApp = (): Express => {
  const app = express();

  app.use(express.json());

  const authService = new AuthService(userRepository);
  const authController = new AuthController(authService);
  app.use(authController.router);

  const userService = new UserService(userRepository);
  const usersController = new UsersController(userService);
  app.use(usersController.router);

  const productService = new ProductService(productRepository);
  const productsController = new ProductsController(productService);
  app.use(productsController.router);

  app.use('/api-docs', swaggerUiServe, swaggerUiSetup);

  app.use(errorMiddleware);

  return app;
};

export default createApp;
