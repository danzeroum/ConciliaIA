import { z } from 'zod';

export const saleSchema = z.object({
  nsu: z.string().min(1, 'NSU é obrigatório').max(50, 'NSU muito longo'),
  amount: z
    .string()
    .refine(
      (val) => !Number.isNaN(Number(val)) && Number(val) > 0,
      'Valor deve ser maior que zero'
    ),
  date: z.string().min(1, 'Data é obrigatória'),
  payment_method: z.string().min(1, 'Método de pagamento é obrigatório'),
});

export type SaleFormData = z.infer<typeof saleSchema>;

export function validateCSVFile(file: File): { valid: boolean; error?: string } {
  if (!file.name.toLowerCase().endsWith('.csv')) {
    return { valid: false, error: 'Arquivo deve ser CSV' };
  }

  if (file.size > 10 * 1024 * 1024) {
    return { valid: false, error: 'Arquivo muito grande (máx 10MB)' };
  }

  return { valid: true };
}

export function validateDateRange(
  startDate: string,
  endDate: string
): { valid: boolean; error?: string } {
  const start = new Date(startDate);
  const end = new Date(endDate);

  if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) {
    return { valid: false, error: 'Datas inválidas' };
  }

  if (start > end) {
    return { valid: false, error: 'Data inicial deve ser anterior à data final' };
  }

  return { valid: true };
}
