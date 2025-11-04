import { z } from 'zod';

export const createProductSchema = z.object({
  name: z.string().min(1, { message: 'Name is required.' }).max(255),
  sku: z.string().min(1, { message: 'SKU is required.' }).max(64),
  description: z.string().max(1000).optional(),
  price: z.number().nonnegative({ message: 'Price must be greater than or equal to zero.' }),
});

export type CreateProductDto = z.infer<typeof createProductSchema>;
