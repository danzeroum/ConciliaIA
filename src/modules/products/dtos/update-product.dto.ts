import { z } from 'zod';

import { createProductSchema } from './create-product.dto';

export const updateProductSchema = createProductSchema
  .partial()
  .refine((data) => Object.keys(data).length > 0, {
    message: 'At least one field must be provided to update the product.',
  });

export type UpdateProductDto = z.infer<typeof updateProductSchema>;
