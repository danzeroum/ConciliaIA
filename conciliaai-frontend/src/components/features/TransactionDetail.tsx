import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Grid,
  Typography,
  Chip,
  Box,
  Divider,
} from '@mui/material';
import { Transaction } from '@/api/transactions.api';
import { formatCurrency, formatDateTime } from '@/utils/formatters';

interface TransactionDetailProps {
  open: boolean;
  transaction: Transaction | null;
  onClose: () => void;
}

export function TransactionDetail({ open, transaction, onClose }: TransactionDetailProps) {
  if (!transaction) {
    return null;
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Detalhes da Transação</DialogTitle>
      <DialogContent dividers>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2" color="text.secondary">
              NSU
            </Typography>
            <Typography variant="body1">{transaction.nsu}</Typography>
          </Grid>

          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2" color="text.secondary">
              Adquirente
            </Typography>
            <Typography variant="body1">{transaction.acquirer.toUpperCase()}</Typography>
          </Grid>

          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2" color="text.secondary">
              Valor Bruto
            </Typography>
            <Typography variant="body1">{formatCurrency(transaction.amount)}</Typography>
          </Grid>

          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2" color="text.secondary">
              MDR
            </Typography>
            <Typography variant="body1">
              {transaction.mdr_amount !== null
                ? `${formatCurrency(transaction.mdr_amount)} (${transaction.mdr_rate ?? 0}%)`
                : 'N/A'}
            </Typography>
          </Grid>

          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2" color="text.secondary">
              Data da Transação
            </Typography>
            <Typography variant="body1">
              {formatDateTime(transaction.transaction_date)}
            </Typography>
          </Grid>

          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2" color="text.secondary">
              Data de Liquidação
            </Typography>
            <Typography variant="body1">
              {transaction.settlement_date
                ? formatDateTime(transaction.settlement_date)
                : 'Não liquidado'}
            </Typography>
          </Grid>

          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2" color="text.secondary">
              Bandeira
            </Typography>
            <Typography variant="body1">{transaction.card_brand}</Typography>
          </Grid>

          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2" color="text.secondary">
              Parcelas
            </Typography>
            <Typography variant="body1">{transaction.installments}</Typography>
          </Grid>

          <Grid item xs={12}>
            <Typography variant="subtitle2" color="text.secondary">
              Status
            </Typography>
            <Box sx={{ mt: 0.5 }}>
              <Chip
                label={transaction.matched ? 'Conciliada' : 'Não conciliada'}
                color={transaction.matched ? 'success' : 'warning'}
                size="small"
              />
            </Box>
          </Grid>

          {transaction.metadata && Object.keys(transaction.metadata).length > 0 && (
            <Grid item xs={12}>
              <Divider sx={{ my: 1 }} />
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Metadados
              </Typography>
              <Box
                component="pre"
                sx={{
                  bgcolor: 'background.default',
                  p: 2,
                  borderRadius: 1,
                  overflowX: 'auto',
                  fontSize: '0.85rem',
                }}
              >
                {JSON.stringify(transaction.metadata, null, 2)}
              </Box>
            </Grid>
          )}
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Fechar</Button>
      </DialogActions>
    </Dialog>
  );
}
