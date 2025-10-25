import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  CircularProgress
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import { apiClient } from '@/api/axios-config';

interface CashFlowData {
  summary_message: string;
  total_expected: number;
  total_received: number;
  daily_forecast: Array<{
    date: string;
    date_formatted: string;
    expected: number;
    received: number;
  }>;
}

export default function CashFlowDashboard() {
  const [data, setData] = useState<CashFlowData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void loadData();
  }, []);

  const loadData = async () => {
    try {
      const response = await apiClient.get<CashFlowData>(
        '/api/v1/cash-flow/forecast',
        {
          params: { days_ahead: 30 }
        }
      );
      setData(response.data);
    } catch (error) {
      console.error('Erro ao carregar fluxo de caixa:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!data) {
    return <Typography>Erro ao carregar dados</Typography>;
  }

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', py: 4 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
        <TrendingUpIcon sx={{ fontSize: 40, color: 'primary.main' }} />
        <Box>
          <Typography variant="h4">Fluxo de Caixa</Typography>
          <Typography variant="body2" color="text.secondary">
            Próximos 30 dias
          </Typography>
        </Box>
      </Box>

      {/* Resumo em Linguagem Natural */}
      <Card sx={{ mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            {data.summary_message}
          </Typography>
          <Box sx={{ display: 'flex', gap: 4, mt: 2 }}>
            <Box>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                A receber
              </Typography>
              <Typography variant="h4">
                {formatCurrency(data.total_expected)}
              </Typography>
            </Box>
            <Box>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                Já recebido
              </Typography>
              <Typography variant="h4">
                {formatCurrency(data.total_received)}
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Gráfico */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Previsão diária
          </Typography>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={data.daily_forecast}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="date_formatted" 
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis 
                tickFormatter={(value) => `R$ ${(value / 1000).toFixed(0)}k`}
              />
              <Tooltip 
                formatter={(value: number) => formatCurrency(value)}
                labelStyle={{ color: '#000' }}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="expected" 
                stroke="#667eea" 
                name="Previsto"
                strokeWidth={2}
                dot={{ r: 4 }}
              />
              <Line 
                type="monotone" 
                dataKey="received" 
                stroke="#48bb78" 
                name="Recebido"
                strokeWidth={2}
                dot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Explicação */}
      <Box sx={{ mt: 2 }}>
        <Typography variant="caption" color="text.secondary">
          💡 <strong>Como funciona:</strong> O gráfico mostra suas vendas parceladas que ainda vão cair na conta. 
          Linha azul = previsto pela adquirente. Linha verde = já recebido.
        </Typography>
      </Box>
    </Box>
  );
}
