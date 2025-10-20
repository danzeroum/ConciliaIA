import React from 'react';
import { Box, Grid, Paper, Typography, Card, CardContent } from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import DoneAllIcon from '@mui/icons-material/DoneAll';

interface KPICardProps {
  title: string;
  value: string | number;
  icon: React.ReactElement;
  trend?: string;
  color?: string;
}

function KPICard({ title, value, icon, trend, color = 'primary' }: KPICardProps) {
  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography color="text.secondary" variant="body2" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h4" component="div">
              {value}
            </Typography>
            {trend && (
              <Typography variant="body2" color="success.main" sx={{ mt: 1 }}>
                {trend}
              </Typography>
            )}
          </Box>
          <Box
            sx={{
              color: `${color}.main`,
              bgcolor: `${color}.light`,
              borderRadius: '50%',
              p: 2,
              display: 'flex',
            }}
          >
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}

export function DashboardPage() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Accuracy"
            value="99.5%"
            icon={<TrendingUpIcon />}
            trend="▲ 0.2%"
            color="success"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Total de Matches"
            value="1,234"
            icon={<CheckCircleIcon />}
            color="primary"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Divergências Pendentes"
            value="12"
            icon={<WarningIcon />}
            color="warning"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Resolvidas Hoje"
            value="45"
            icon={<DoneAllIcon />}
            color="success"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Accuracy Trend (Últimos 30 dias)
            </Typography>
            <Box
              sx={{
                height: 300,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'text.secondary',
              }}
            >
              <Typography>Gráfico de Accuracy</Typography>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Top Divergências
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" gutterBottom>
                • Transação Faltando: 8
              </Typography>
              <Typography variant="body2" gutterBottom>
                • Duplicada: 2
              </Typography>
              <Typography variant="body2" gutterBottom>
                • Variação MDR: 1
              </Typography>
              <Typography variant="body2">• Divergência de Valor: 1</Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
