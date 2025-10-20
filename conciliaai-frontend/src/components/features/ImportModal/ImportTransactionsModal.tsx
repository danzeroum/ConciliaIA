import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Grid,
  TextField,
  MenuItem,
  Typography,
} from '@mui/material';
import { ACQUIRERS } from '@/utils/constants';
import { validateDateRange } from '@/utils/validators';
import { useTransactions } from '@/hooks/useTransactions';

interface ImportTransactionsModalProps {
  open: boolean;
  onClose: () => void;
}

export function ImportTransactionsModal({ open, onClose }: ImportTransactionsModalProps) {
  const { importFromAcquirer, isImporting } = useTransactions();
  const [acquirer, setAcquirer] = React.useState<string>('cielo');
  const [startDate, setStartDate] = React.useState<string>('');
  const [endDate, setEndDate] = React.useState<string>('');
  const [error, setError] = React.useState<string | null>(null);

  const handleSubmit = () => {
    if (!acquirer || !startDate || !endDate) {
      setError('Informe adquirente e intervalo de datas');
      return;
    }

    const validation = validateDateRange(startDate, endDate);
    if (!validation.valid) {
      setError(validation.error ?? 'Intervalo de datas inválido');
      return;
    }

    setError(null);
    importFromAcquirer(
      { acquirer, startDate, endDate },
      {
        onSuccess: () => {
          onClose();
          setStartDate('');
          setEndDate('');
          setAcquirer('cielo');
        },
      }
    );
  };

  const handleClose = () => {
    setError(null);
    setStartDate('');
    setEndDate('');
    setAcquirer('cielo');
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} fullWidth maxWidth="sm">
      <DialogTitle>Importar Transações</DialogTitle>
      <DialogContent dividers>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <TextField
              select
              label="Adquirente"
              value={acquirer}
              onChange={(event) => setAcquirer(event.target.value)}
              fullWidth
            >
              {ACQUIRERS.map((item) => (
                <MenuItem key={item.value} value={item.value}>
                  {item.label}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              label="Data inicial"
              type="date"
              value={startDate}
              onChange={(event) => setStartDate(event.target.value)}
              InputLabelProps={{ shrink: true }}
              fullWidth
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              label="Data final"
              type="date"
              value={endDate}
              onChange={(event) => setEndDate(event.target.value)}
              InputLabelProps={{ shrink: true }}
              fullWidth
            />
          </Grid>
          {error && (
            <Grid item xs={12}>
              <Typography variant="body2" color="error">
                {error}
              </Typography>
            </Grid>
          )}
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} color="inherit" disabled={isImporting}>
          Cancelar
        </Button>
        <Button onClick={handleSubmit} variant="contained" disabled={isImporting}>
          {isImporting ? 'Importando...' : 'Importar'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
