import { Request, Response, Router } from 'express';

import { ApplicationError } from '../common/errors';
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
    this.router.post('/products', this.createProduct);
    this.router.get('/products', this.getAllProducts);
    this.router.get('/products/:id', this.getProductById);
    this.router.patch('/products/:id', this.updateProduct);
    this.router.delete('/products/:id', this.deleteProduct);
  }

  private createProduct = async (req: Request, res: Response): Promise<Response> => {
    const validation = createProductSchema.safeParse(req.body);

    if (!validation.success) {
      return res.status(400).json({
        message: 'Invalid request body.',
        errors: validation.error.flatten(),
      });
    }

    try {
      const product = await this.productService.createProduct(validation.data);
      return res.status(201).json(product);
    } catch (error) {
      return this.handleError(res, error);
    }
  };

  private getAllProducts = async (_req: Request, res: Response): Promise<Response> => {
    try {
      const products = await this.productService.getAllProducts();
      return res.status(200).json(products);
    } catch (error) {
      return this.handleError(res, error);
    }
  };

  private getProductById = async (req: Request, res: Response): Promise<Response> => {
    try {
      const product = await this.productService.getProductById(req.params.id);
      return res.status(200).json(product);
    } catch (error) {
      return this.handleError(res, error);
    }
  };

  private updateProduct = async (req: Request, res: Response): Promise<Response> => {
    const validation = updateProductSchema.safeParse(req.body);

    if (!validation.success) {
      return res.status(400).json({
        message: 'Invalid request body.',
        errors: validation.error.flatten(),
      });
    }

    try {
      const product = await this.productService.updateProduct(req.params.id, validation.data);
      return res.status(200).json(product);
    } catch (error) {
      return this.handleError(res, error);
    }
  };

  private deleteProduct = async (req: Request, res: Response): Promise<Response> => {
    try {
      const product = await this.productService.deleteProduct(req.params.id);
      return res.status(200).json(product);
    } catch (error) {
      return this.handleError(res, error);
    }
  };

  private handleError(res: Response, error: unknown): Response {
    if (error instanceof ApplicationError) {
      return res.status(error.statusCode).json({ message: error.message });
    }

    console.error('Unexpected error in ProductsController', error);
    return res.status(500).json({ message: 'Internal server error.' });
  }
}

export default ProductsController;
