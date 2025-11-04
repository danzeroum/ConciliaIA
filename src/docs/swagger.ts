import path from 'node:path';

import swaggerJsdoc from 'swagger-jsdoc';
import swaggerUi from 'swagger-ui-express';

const controllersGlob = path.resolve(__dirname, '../modules/**/*.controller.ts');

const swaggerDefinition: swaggerJsdoc.Options['definition'] = {
  openapi: '3.0.0',
  info: {
    title: 'ConciliaIA API',
    version: '1.0.0',
    description:
      'API documentation for the ConciliaIA platform, covering authentication, users and products resources.',
  },
  servers: [
    {
      url: 'http://localhost:3000',
      description: 'Local server',
    },
  ],
  components: {
    securitySchemes: {
      bearerAuth: {
        type: 'http',
        scheme: 'bearer',
        bearerFormat: 'JWT',
      },
    },
    schemas: {
      ErrorResponse: {
        type: 'object',
        properties: {
          error: { type: 'string', description: 'Error message' },
          statusCode: { type: 'integer', format: 'int32' },
          timestamp: { type: 'string', format: 'date-time' },
          details: {
            type: 'object',
            additionalProperties: true,
            description: 'Optional error details',
          },
        },
        required: ['error', 'statusCode', 'timestamp'],
      },
      User: {
        type: 'object',
        properties: {
          id: { type: 'string', description: 'User identifier' },
          email: { type: 'string', format: 'email' },
          name: { type: 'string', nullable: true },
          createdAt: { type: 'string', format: 'date-time' },
          updatedAt: { type: 'string', format: 'date-time' },
        },
        required: ['id', 'email', 'createdAt', 'updatedAt'],
      },
      CreateUserInput: {
        type: 'object',
        properties: {
          name: { type: 'string' },
          email: { type: 'string', format: 'email' },
          password: { type: 'string', format: 'password' },
        },
        required: ['name', 'email', 'password'],
      },
      UpdateUserInput: {
        type: 'object',
        properties: {
          name: { type: 'string', nullable: true },
          email: { type: 'string', format: 'email', nullable: true },
          password: { type: 'string', format: 'password', nullable: true },
        },
      },
      Product: {
        type: 'object',
        properties: {
          id: { type: 'string', description: 'Product identifier' },
          name: { type: 'string' },
          sku: { type: 'string' },
          description: { type: 'string', nullable: true },
          price: { type: 'number', format: 'float' },
          createdAt: { type: 'string', format: 'date-time' },
          updatedAt: { type: 'string', format: 'date-time' },
        },
        required: ['id', 'name', 'sku', 'price', 'createdAt', 'updatedAt'],
      },
      CreateProductInput: {
        type: 'object',
        properties: {
          name: { type: 'string' },
          sku: { type: 'string' },
          description: { type: 'string', nullable: true },
          price: { type: 'number', format: 'float' },
        },
        required: ['name', 'sku', 'price'],
      },
      UpdateProductInput: {
        type: 'object',
        properties: {
          name: { type: 'string', nullable: true },
          sku: { type: 'string', nullable: true },
          description: { type: 'string', nullable: true },
          price: { type: 'number', format: 'float', nullable: true },
        },
      },
      AuthLoginInput: {
        type: 'object',
        properties: {
          email: { type: 'string', format: 'email' },
          password: { type: 'string', format: 'password' },
        },
        required: ['email', 'password'],
      },
      AuthResponse: {
        type: 'object',
        properties: {
          token: { type: 'string', description: 'JWT token' },
          user: { $ref: '#/components/schemas/User' },
        },
        required: ['token', 'user'],
      },
    },
  },
};

const swaggerOptions: swaggerJsdoc.Options = {
  definition: swaggerDefinition,
  apis: [controllersGlob],
};

export const swaggerSpec = swaggerJsdoc(swaggerOptions);
export const swaggerUiServe = swaggerUi.serve;
export const swaggerUiSetup = swaggerUi.setup(swaggerSpec, {
  explorer: true,
});

export default swaggerSpec;
