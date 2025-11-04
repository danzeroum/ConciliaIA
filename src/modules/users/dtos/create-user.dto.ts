import { z } from 'zod';

export const createUserSchema = z.object({
  email: z.string().email({ message: 'Invalid email format.' }),
  password: z
    .string()
    .min(8, { message: 'Password must be at least 8 characters long.' })
    .max(128, { message: 'Password must be at most 128 characters long.' }),
  name: z.string().min(1, { message: 'Name is required.' }).max(255),
});

export type CreateUserDto = z.infer<typeof createUserSchema>;
