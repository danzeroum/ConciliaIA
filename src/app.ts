import express, { Express } from 'express';
import compression from 'compression';
import rateLimit from 'express-rate-limit';
import helmet from 'helmet';
import cors, { CorsOptions } from 'cors';

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

  const allowedOrigins = process.env.CORS_ORIGINS?.split(',')
    .map((origin) => origin.trim())
    .filter(Boolean);

  const corsOptions: CorsOptions | undefined = allowedOrigins?.length
    ? { origin: allowedOrigins, credentials: true }
    : undefined;

  if (process.env.NODE_ENV === 'production') {
    app.set('trust proxy', 1);
  }

  app.use(helmet());
  app.use(corsOptions ? cors(corsOptions) : cors());
  app.use(compression());
  app.use(
    rateLimit({
      windowMs: 15 * 60 * 1000,
      max: Number(process.env.RATE_LIMIT_MAX ?? 100),
      standardHeaders: true,
      legacyHeaders: false,
    }),
  );
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
