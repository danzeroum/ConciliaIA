import { useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Grid,
  MenuItem,
} from '@mui/material';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const saleSchema = z.object({
  nsu: z.string().min(1, 'NSU é obrigatório'),
  amount: z.number().positive('Valor deve ser positivo'),
  sale_date: z.string().min(1, 'Data é obrigatória'),
  payment_method: z.string().min(1, 'Método de pagamento é obrigatório'),
  installments: z.number().int().min(1).max(24).default(1),
  card_brand: z.string().optional(),
  authorization_code: z.string().optional(),
});

export type SaleFormData = z.infer<typeof saleSchema>;

interface SaleFormDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: SaleFormData) => void;
  initialData?: Partial<SaleFormData>;
  mode: 'create' | 'edit';
}

const paymentMethods = [
  { value: 'credit', label: 'Crédito' },
  { value: 'debit', label: 'Débito' },
  { value: 'pix', label: 'PIX' },
  { value: 'voucher', label: 'Voucher' },
];

const cardBrands = [
  { value: 'Visa', label: 'Visa' },
  { value: 'Mastercard', label: 'Mastercard' },
  { value: 'Elo', label: 'Elo' },
  { value: 'Amex', label: 'American Express' },
  { value: 'Hipercard', label: 'Hipercard' },
];

export function SaleFormDialog({
  open,
  onClose,
  onSubmit,
  initialData,
  mode,
}: SaleFormDialogProps) {
  const {
    control,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<SaleFormData>({
    resolver: zodResolver(saleSchema),
    defaultValues: {
      nsu: '',
      amount: 0,
      sale_date: new Date().toISOString().split('T')[0],
      payment_method: 'credit',
      installments: 1,
      card_brand: '',
      authorization_code: '',
      ...initialData,
    },
  });

  useEffect(() => {
    if (open) {
      reset({
        nsu: initialData?.nsu ?? '',
        amount: initialData?.amount ?? 0,
        sale_date: initialData?.sale_date ?? new Date().toISOString().split('T')[0],
        payment_method: initialData?.payment_method ?? 'credit',
        installments: initialData?.installments ?? 1,
        card_brand: initialData?.card_brand ?? '',
        authorization_code: initialData?.authorization_code ?? '',
      });
    }
  }, [initialData, open, reset]);

  const handleClose = () => {
    reset();
    onClose();
  };

  const handleFormSubmit = (data: SaleFormData) => {
    onSubmit(data);
    handleClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {mode === 'create' ? 'Nova Venda' : 'Editar Venda'}
      </DialogTitle>
      <form onSubmit={handleSubmit(handleFormSubmit)}>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <Controller
                name="nsu"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="NSU"
                    fullWidth
                    error={!!errors.nsu}
                    helperText={errors.nsu?.message}
                    disabled={mode === 'edit'}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <Controller
                name="amount"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    value={field.value ?? ''}
                    label="Valor (R$)"
                    type="number"
                    fullWidth
                    error={!!errors.amount}
                    helperText={errors.amount?.message}
                    onChange={(e) => field.onChange(Number(e.target.value))}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <Controller
                name="sale_date"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Data da Venda"
                    type="date"
                    fullWidth
                    error={!!errors.sale_date}
                    helperText={errors.sale_date?.message}
                    InputLabelProps={{ shrink: true }}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <Controller
                name="payment_method"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    select
                    label="Método de Pagamento"
                    fullWidth
                    error={!!errors.payment_method}
                    helperText={errors.payment_method?.message}
                  >
                    {paymentMethods.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </TextField>
                )}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <Controller
                name="installments"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    value={field.value ?? ''}
                    label="Parcelas"
                    type="number"
                    fullWidth
                    error={!!errors.installments}
                    helperText={errors.installments?.message}
                    onChange={(e) => field.onChange(Number(e.target.value))}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <Controller
                name="card_brand"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    select
                    label="Bandeira"
                    fullWidth
                    error={!!errors.card_brand}
                    helperText={errors.card_brand?.message}
                  >
                    <MenuItem value="">Nenhuma</MenuItem>
                    {cardBrands.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </TextField>
                )}
              />
            </Grid>

            <Grid item xs={12}>
              <Controller
                name="authorization_code"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Código de Autorização"
                    fullWidth
                    error={!!errors.authorization_code}
                    helperText={errors.authorization_code?.message}
                  />
                )}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancelar</Button>
          <Button type="submit" variant="contained">
            {mode === 'create' ? 'Criar' : 'Salvar'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}
