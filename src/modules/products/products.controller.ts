import { NextFunction, Request, Response, Router } from 'express';

import { parseWithSchema } from '../../utils/validation';
import { authMiddleware } from '../../middleware/auth.middleware';
import { createProductSchema } from './dtos/create-product.dto';
import { updateProductSchema } from './dtos/update-product.dto';
import { ProductService } from './services/product.service';

/**
 * @swagger
 * tags:
 *   - name: Products
 *     description: Product catalog management
 */

export class ProductsController {
  public readonly router: Router;

  constructor(private readonly productService: ProductService) {
    this.router = Router();
    this.registerRoutes();
  }

  private registerRoutes(): void {
    /**
     * @swagger
     * /products:
     *   post:
     *     summary: Create a new product
     *     tags: [Products]
     *     security:
     *       - bearerAuth: []
     *     requestBody:
     *       required: true
     *       content:
     *         application/json:
     *           schema:
     *             $ref: '#/components/schemas/CreateProductInput'
     *     responses:
     *       201:
     *         description: Product created successfully
     *         content:
     *           application/json:
     *             schema:
     *               $ref: '#/components/schemas/Product'
     *       400:
     *         description: Validation error
     *         content:
     *           application/json:
     *             schema:
     *               $ref: '#/components/schemas/ErrorResponse'
     *       401:
     *         description: Unauthorized
     *         content:
     *           application/json:
     *             schema:
     *               $ref: '#/components/schemas/ErrorResponse'
     *       409:
     *         description: SKU already in use
     *         content:
     *           application/json:
     *             schema:
     *               $ref: '#/components/schemas/ErrorResponse'
     */
    this.router.post('/products', authMiddleware, this.createProduct);

    /**
     * @swagger
     * /products:
     *   get:
     *     summary: List products
     *     tags: [Products]
     *     responses:
     *       200:
     *         description: Products found
     *         content:
     *           application/json:
     *             schema:
     *               type: array
     *               items:
     *                 $ref: '#/components/schemas/Product'
     */
    this.router.get('/products', this.getAllProducts);

    /**
     * @swagger
     * /products/{id}:
     *   get:
     *     summary: Get product by ID
     *     tags: [Products]
     *     parameters:
     *       - in: path
     *         name: id
     *         schema:
     *           type: string
     *         required: true
     *         description: Product identifier
     *     responses:
     *       200:
     *         description: Product found
     *         content:
     *           application/json:
     *             schema:
     *               $ref: '#/components/schemas/Product'
     *       404:
     *         description: Product not found
     *         content:
     *           application/json:
     *             schema:
     *               $ref: '#/components/schemas/ErrorResponse'
     */
    this.router.get('/products/:id', this.getProductById);

    /**
     * @swagger
     * /products/{id}:
     *   patch:
     *     summary: Update a product
     *     tags: [Products]
     *     security:
     *       - bearerAuth: []
     *     parameters:
     *       - in: path
     *         name: id
     *         schema:
     *           type: string
     *         required: true
     *         description: Product identifier
     *     requestBody:
     *       required: true
     *       content:
     *         application/json:
     *           schema:
     *             $ref: '#/components/schemas/UpdateProductInput'
     *     responses:
     *       200:
     *         description: Product updated successfully
     *         content:
     *           application/json:
     *             schema:
     *               $ref: '#/components/schemas/Product'
     *       400:
     *         description: Validation error
     *         content:
     *           application/json:
     *             schema:
     *               $ref: '#/components/schemas/ErrorResponse'
     *       401:
     *         description: Unauthorized
     *         content:
     *           application/json:
     *             schema:
     *               $ref: '#/components/schemas/ErrorResponse'
     *       404:
     *         description: Product not found
     *         content:
     *           application/json:
     *             schema:
     *               $ref: '#/components/schemas/ErrorResponse'
     */
    this.router.patch('/products/:id', authMiddleware, this.updateProduct);

    /**
     * @swagger
     * /products/{id}:
     *   delete:
     *     summary: Delete a product
     *     tags: [Products]
     *     security:
     *       - bearerAuth: []
     *     parameters:
     *       - in: path
     *         name: id
     *         schema:
     *           type: string
     *         required: true
     *         description: Product identifier
     *     responses:
     *       200:
     *         description: Product deleted successfully
     *         content:
     *           application/json:
     *             schema:
     *               $ref: '#/components/schemas/Product'
     *       401:
     *         description: Unauthorized
     *         content:
     *           application/json:
     *             schema:
     *               $ref: '#/components/schemas/ErrorResponse'
     *       404:
     *         description: Product not found
     *         content:
     *           application/json:
     *             schema:
     *               $ref: '#/components/schemas/ErrorResponse'
     */
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
