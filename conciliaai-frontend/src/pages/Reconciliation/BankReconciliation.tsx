import { useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Grid,
  IconButton,
  TextField,
  Typography,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';

import { apiClient } from '@/api/axios-config';

interface BankPaymentForm {
  payment_date: string;
  amount: string;
  reference?: string;
}

interface MatchedResult {
  payment_date: string;
  amount: number;
  settlement_id: string;
  expected_date: string;
}

interface AutoMatchResponse {
  matched: MatchedResult[];
  unmatched: { payment_date: string; amount: number; reference?: string }[];
}

const BankReconciliationPage = () => {
  const [payments, setPayments] = useState<BankPaymentForm[]>([
    { payment_date: new Date().toISOString().split('T')[0], amount: '' },
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<AutoMatchResponse | null>(null);

  const handleAddPayment = () => {
    setPayments((current) => [
      ...current,
      { payment_date: new Date().toISOString().split('T')[0], amount: '' },
    ]);
  };

  const handleRemovePayment = (index: number) => {
    setPayments((current) => current.filter((_, idx) => idx !== index));
  };

  const handleChange = (index: number, field: keyof BankPaymentForm, value: string) => {
    setPayments((current) =>
      current.map((item, idx) =>
        idx === index
          ? {
              ...item,
              [field]: value,
            }
          : item
      )
    );
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const payload = payments
        .filter((payment) => payment.amount)
        .map((payment) => ({
          payment_date: payment.payment_date,
          amount: Number(payment.amount.replace(',', '.')),
          reference: payment.reference,
        }));

      if (!payload.length) {
        setError('Informe pelo menos um pagamento para conciliar.');
        setLoading(false);
        return;
      }

      const response = await apiClient.post<AutoMatchResponse>(
        '/api/v1/bank-reconciliation/auto-match',
        payload
      );
      setResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Não foi possível conciliar os pagamentos.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Conciliação Bancária Automática
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Informe os créditos recebidos em conta e o ConciliaAI irá marcar automaticamente os
        recebimentos liquidados nas adquirentes.
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2}>
            {payments.map((payment, index) => (
              <Grid item xs={12} key={`payment-${index}`}>
                <Grid container spacing={2} alignItems="center">
                  <Grid item xs={12} md={3}>
                    <TextField
                      label="Data do crédito"
                      type="date"
                      value={payment.payment_date}
                      onChange={(event) => handleChange(index, 'payment_date', event.target.value)}
                      fullWidth
                    />
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <TextField
                      label="Valor recebido"
                      value={payment.amount}
                      onChange={(event) => handleChange(index, 'amount', event.target.value)}
                      placeholder="0,00"
                      fullWidth
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <TextField
                      label="Referência (opcional)"
                      value={payment.reference || ''}
                      onChange={(event) => handleChange(index, 'reference', event.target.value)}
                      fullWidth
                    />
                  </Grid>
                  <Grid item xs={12} md={2}>
                    <IconButton onClick={() => handleRemovePayment(index)} disabled={payments.length === 1}>
                      <DeleteIcon />
                    </IconButton>
                  </Grid>
                </Grid>
              </Grid>
            ))}
          </Grid>

          <Button variant="outlined" sx={{ mt: 2 }} onClick={handleAddPayment}>
            Adicionar pagamento
          </Button>
        </CardContent>
      </Card>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Button variant="contained" onClick={handleSubmit} disabled={loading}>
        {loading ? 'Conciliando...' : 'Conciliar pagamentos'}
      </Button>

      {result && (
        <Box sx={{ mt: 4 }}>
          <Typography variant="h6" gutterBottom>
            Resultado da conciliação
          </Typography>

          <Typography variant="subtitle1" gutterBottom>
            Pagamentos conciliados
          </Typography>
          {result.matched.length === 0 ? (
            <Alert severity="info" sx={{ mb: 2 }}>
              Nenhum pagamento coincidiu com os recebimentos previstos.
            </Alert>
          ) : (
            <Table size="small" sx={{ mb: 3 }}>
              <TableHead>
                <TableRow>
                  <TableCell>Data do pagamento</TableCell>
                  <TableCell>Valor</TableCell>
                  <TableCell>ID do settlement</TableCell>
                  <TableCell>Data prevista</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {result.matched.map((item) => (
                  <TableRow key={item.settlement_id}>
                    <TableCell>{item.payment_date}</TableCell>
                    <TableCell>{item.amount.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</TableCell>
                    <TableCell>{item.settlement_id}</TableCell>
                    <TableCell>{item.expected_date}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}

          <Typography variant="subtitle1" gutterBottom>
            Pagamentos sem correspondência
          </Typography>
          {result.unmatched.length === 0 ? (
            <Alert severity="success">Todos os pagamentos foram conciliados!</Alert>
          ) : (
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Data</TableCell>
                  <TableCell>Valor</TableCell>
                  <TableCell>Referência</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {result.unmatched.map((item, idx) => (
                  <TableRow key={`${item.payment_date}-${idx}`}>
                    <TableCell>{item.payment_date}</TableCell>
                    <TableCell>{item.amount.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</TableCell>
                    <TableCell>{item.reference || '-'}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </Box>
      )}
    </Box>
  );
};

export default BankReconciliationPage;
