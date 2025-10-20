import { z } from 'zod';

import { createUserSchema } from './create-user.dto';

export const updateUserSchema = createUserSchema
  .partial()
  .extend({
    password: createUserSchema.shape.password.optional(),
  })
  .refine((data) => Object.keys(data).length > 0, {
    message: 'At least one field must be provided to update the user.',
  });

export type UpdateUserDto = z.infer<typeof updateUserSchema>;
