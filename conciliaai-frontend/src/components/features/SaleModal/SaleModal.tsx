import React from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
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
import { saleSchema, type SaleFormData } from '@/utils/validators';
import { PAYMENT_METHODS } from '@/utils/constants';
import { useSales } from '@/hooks/useSales';
import type { Sale } from '@/types/api.types';

interface SaleModalProps {
  open: boolean;
  onClose: () => void;
  sale?: Sale | null;
  mode: 'create' | 'edit';
}

const defaultValues: SaleFormData = {
  nsu: '',
  amount: '',
  date: new Date().toISOString().split('T')[0],
  payment_method: 'credit_card',
};

export function SaleModal({ open, onClose, sale, mode }: SaleModalProps) {
  const isEditMode = mode === 'edit';
  const { createSale, updateSale, isCreating, isUpdating } = useSales();

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<SaleFormData>({
    resolver: zodResolver(saleSchema),
    defaultValues,
  });

  React.useEffect(() => {
    if (open) {
      if (sale) {
        reset({
          nsu: sale.nsu,
          amount: sale.amount,
          date: sale.date.split('T')[0] ?? sale.date,
          payment_method: sale.payment_method,
        });
      } else {
        reset(defaultValues);
      }
    }
  }, [sale, open, reset]);

  const onSubmit = (data: SaleFormData) => {
    if (isEditMode && sale) {
      updateSale(
        { id: sale.id, data },
        {
          onSuccess: () => {
            reset(defaultValues);
            onClose();
          },
        }
      );
      return;
    }

    createSale(data, {
      onSuccess: () => {
        reset(defaultValues);
        onClose();
      },
    });
  };

  const handleClose = () => {
    reset(defaultValues);
    onClose();
  };

  const isSubmitting = isEditMode ? isUpdating : isCreating;

  return (
    <Dialog open={open} onClose={handleClose} fullWidth maxWidth="sm">
      <DialogTitle>{isEditMode ? 'Editar Venda' : 'Nova Venda'}</DialogTitle>
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <DialogContent dividers>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Controller
                name="nsu"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="NSU"
                    fullWidth
                    error={Boolean(errors.nsu)}
                    helperText={errors.nsu?.message}
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
                    label="Valor"
                    fullWidth
                    error={Boolean(errors.amount)}
                    helperText={errors.amount?.message}
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Controller
                name="date"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Data"
                    type="date"
                    fullWidth
                    InputLabelProps={{ shrink: true }}
                    error={Boolean(errors.date)}
                    helperText={errors.date?.message}
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
                    error={Boolean(errors.payment_method)}
                    helperText={errors.payment_method?.message}
                  >
                    {PAYMENT_METHODS.map((method) => (
                      <MenuItem key={method.value} value={method.value}>
                        {method.label}
                      </MenuItem>
                    ))}
                  </TextField>
                )}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} color="inherit" disabled={isSubmitting}>
            Cancelar
          </Button>
          <Button type="submit" variant="contained" disabled={isSubmitting}>
            {isSubmitting ? 'Salvando...' : isEditMode ? 'Salvar' : 'Criar'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}
