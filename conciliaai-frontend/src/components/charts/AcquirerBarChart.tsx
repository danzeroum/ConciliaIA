import { Box, Typography, useTheme } from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

interface AcquirerBarChartProps {
  data: Array<{ acquirer: string; transactions: number; amount: number }>;
  title?: string;
}

export function AcquirerBarChart({
  data,
  title = 'Desempenho por Adquirente',
}: AcquirerBarChartProps) {
  const theme = useTheme();

  const chartData = data.map((item) => ({
    name: item.acquirer.toUpperCase(),
    transacoes: item.transactions,
    valor: item.amount,
  }));

  return (
    <Box>
      {title && (
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
      )}
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
          <XAxis dataKey="name" stroke={theme.palette.text.secondary} />
          <YAxis stroke={theme.palette.text.secondary} />
          <Tooltip
            contentStyle={{
              backgroundColor: theme.palette.background.paper,
              border: `1px solid ${theme.palette.divider}`,
            }}
            formatter={(value: number, name: string) => [
              name === 'valor' ? `R$ ${value.toFixed(2)}` : value,
              name === 'valor' ? 'Valor Total' : 'Transações',
            ]}
          />
          <Legend />
          <Bar dataKey="transacoes" fill={theme.palette.primary.main} name="Transações" />
          <Bar dataKey="valor" fill={theme.palette.secondary.main} name="Valor (R$)" />
        </BarChart>
      </ResponsiveContainer>
    </Box>
  );
}
