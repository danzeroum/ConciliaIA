import { NextFunction, Request, Response, Router } from 'express';

import { parseWithSchema } from '../../utils/validation';
import { authMiddleware } from '../../middleware/auth.middleware';
import { createProductSchema } from './dtos/create-product.dto';
import { updateProductSchema } from './dtos/update-product.dto';
import { ProductService } from './services/product.service';

export class ProductsController {
  public readonly router: Router;

  constructor(private readonly productService: ProductService) {
    this.router = Router();
    this.registerRoutes();
  }

  private registerRoutes(): void {
    this.router.post('/products', authMiddleware, this.createProduct);
    this.router.get('/products', this.getAllProducts);
    this.router.get('/products/:id', this.getProductById);
    this.router.patch('/products/:id', authMiddleware, this.updateProduct);
    this.router.delete('/products/:id', authMiddleware, this.deleteProduct);
  }

  private createProduct = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const payload = parseWithSchema(createProductSchema, req.body, 'Invalid request body.');
      const product = await this.productService.createProduct(payload);
      res.status(201).json(product);
    } catch (error) {
      next(error);
    }
  };

  private getAllProducts = async (_req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const products = await this.productService.getAllProducts();
      res.status(200).json(products);
    } catch (error) {
      next(error);
    }
  };

  private getProductById = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const product = await this.productService.getProductById(req.params.id);
      res.status(200).json(product);
    } catch (error) {
      next(error);
    }
  };

  private updateProduct = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const payload = parseWithSchema(updateProductSchema, req.body, 'Invalid request body.');
      const product = await this.productService.updateProduct(req.params.id, payload);
      res.status(200).json(product);
    } catch (error) {
      next(error);
    }
  };

  private deleteProduct = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const product = await this.productService.deleteProduct(req.params.id);
      res.status(200).json(product);
    } catch (error) {
      next(error);
    }
  };
}

export default ProductsController;
