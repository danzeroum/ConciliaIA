import { Box, Typography, useTheme } from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { TrendDataPoint } from '@/api/stats.api';

interface AccuracyTrendChartProps {
  data: TrendDataPoint[];
  title?: string;
}

export function AccuracyTrendChart({ data, title = 'Accuracy Trend' }: AccuracyTrendChartProps) {
  const theme = useTheme();

  const formattedData = data.map((point) => ({
    date: new Date(point.date).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }),
    accuracy: point.value,
  }));

  return (
    <Box>
      {title && (
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
      )}
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={formattedData}>
          <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
          <XAxis
            dataKey="date"
            stroke={theme.palette.text.secondary}
            style={{ fontSize: '12px' }}
          />
          <YAxis
            stroke={theme.palette.text.secondary}
            style={{ fontSize: '12px' }}
            domain={[90, 100]}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: theme.palette.background.paper,
              border: `1px solid ${theme.palette.divider}`,
            }}
            formatter={(value: number) => [`${value.toFixed(2)}%`, 'Accuracy']}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="accuracy"
            stroke={theme.palette.primary.main}
            strokeWidth={2}
            dot={{ fill: theme.palette.primary.main }}
            name="Accuracy (%)"
          />
        </LineChart>
      </ResponsiveContainer>
    </Box>
  );
}
