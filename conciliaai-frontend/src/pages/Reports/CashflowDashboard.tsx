import { useEffect, useState } from 'react';
import {
  Alert,
  Box,
  Card,
  CardContent,
  CircularProgress,
  Grid,
  TextField,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Paper,
  Button,
} from '@mui/material';

import { apiClient } from '../../services/api';

interface CashflowTimelineItem {
  date: string;
  expected_amount: number;
  received_amount: number;
  delayed_amount: number;
}

interface CashflowResponse {
  period_start: string;
  period_end: string;
  total_expected: number;
  total_received: number;
  delayed_amount: number;
  pending_amount: number;
  timeline: CashflowTimelineItem[];
}

const formatCurrency = (value: number) =>
  value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

const CashflowDashboard = () => {
  const [startDate, setStartDate] = useState(() => {
    const date = new Date();
    date.setDate(date.getDate() - 29);
    return date.toISOString().split('T')[0];
  });
  const [endDate, setEndDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [data, setData] = useState<CashflowResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchData = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await apiClient.get<CashflowResponse>(
        `/reports/cashflow-overview?start_date=${startDate}&end_date=${endDate}`
      );
      setData(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Não foi possível carregar o fluxo de caixa.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Fluxo de Caixa Previsto vs Recebido
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Acompanhe os pagamentos previstos pelas adquirentes e identifique atrasos rapidamente.
      </Typography>

      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <TextField
            type="date"
            label="Início"
            value={startDate}
            onChange={(event) => setStartDate(event.target.value)}
            fullWidth
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <TextField
            type="date"
            label="Fim"
            value={endDate}
            onChange={(event) => setEndDate(event.target.value)}
            fullWidth
          />
        </Grid>
      </Grid>

      <Box sx={{ mb: 3 }}>
        <Typography variant="body2" color="text.secondary">
          Alterou o período? clique em atualizar
        </Typography>
        <Button variant="outlined" onClick={fetchData} disabled={loading} sx={{ mt: 1 }}>
          {loading ? 'Atualizando...' : 'Atualizar'}
        </Button>
      </Box>

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {error && <Alert severity="error">{error}</Alert>}

      {data && !loading && (
        <Box>
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography variant="subtitle2" color="text.secondary">
                    Total Previsto
                  </Typography>
                  <Typography variant="h5">{formatCurrency(data.total_expected)}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography variant="subtitle2" color="text.secondary">
                    Recebido
                  </Typography>
                  <Typography variant="h5">{formatCurrency(data.total_received)}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography variant="subtitle2" color="text.secondary">
                    Atrasado
                  </Typography>
                  <Typography variant="h5">{formatCurrency(data.delayed_amount)}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography variant="subtitle2" color="text.secondary">
                    Pendente
                  </Typography>
                  <Typography variant="h5">{formatCurrency(data.pending_amount)}</Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          <Paper>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Data</TableCell>
                  <TableCell align="right">Previsto</TableCell>
                  <TableCell align="right">Recebido</TableCell>
                  <TableCell align="right">Atrasado</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {data.timeline.map((item) => (
                  <TableRow key={item.date}>
                    <TableCell>{item.date}</TableCell>
                    <TableCell align="right">{formatCurrency(item.expected_amount)}</TableCell>
                    <TableCell align="right">{formatCurrency(item.received_amount)}</TableCell>
                    <TableCell align="right">{formatCurrency(item.delayed_amount)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Paper>
        </Box>
      )}
    </Box>
  );
};

export default CashflowDashboard;
