import React from 'react';
import { Box, Grid, Paper, Typography, Card, CardContent, CircularProgress } from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import DoneAllIcon from '@mui/icons-material/DoneAll';
import { useDashboardStats } from '@/hooks/useStats';
import { AccuracyTrendChart } from '@/components/charts/AccuracyTrendChart';
import { DivergencesPieChart } from '@/components/charts/DivergencesPieChart';
import { AcquirerBarChart } from '@/components/charts/AcquirerBarChart';

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
  const { data: stats, isLoading, error } = useDashboardStats(30);

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error || !stats) {
    return (
      <Box>
        <Typography color="error">Erro ao carregar estatísticas do dashboard</Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      {/* KPIs */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Accuracy"
            value={`${stats.kpis.accuracy.toFixed(1)}%`}
            icon={<TrendingUpIcon />}
            color="success"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Total de Matches"
            value={stats.kpis.total_matches.toLocaleString('pt-BR')}
            icon={<CheckCircleIcon />}
            color="primary"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Divergências Pendentes"
            value={stats.kpis.pending_divergences}
            icon={<WarningIcon />}
            color="warning"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Resolvidas Hoje"
            value={stats.kpis.resolved_today}
            icon={<DoneAllIcon />}
            color="success"
          />
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <AccuracyTrendChart
              data={stats.accuracy_trend}
              title="Accuracy - Últimos 30 dias"
            />
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <DivergencesPieChart
              data={stats.top_divergence_types}
              title="Top Divergências"
            />
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <AcquirerBarChart
              data={stats.acquirer_breakdown}
              title="Desempenho por Adquirente"
            />
          </Paper>
        </Grid>

        {/* Summary Cards */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Resumo do Período
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                <strong>Total de Vendas:</strong>{' '}
                {stats.kpis.total_sales.toLocaleString('pt-BR')}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                <strong>Total de Transações:</strong>{' '}
                {stats.kpis.total_transactions.toLocaleString('pt-BR')}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                <strong>Valor Reconciliado:</strong>{' '}
                {new Intl.NumberFormat('pt-BR', {
                  style: 'currency',
                  currency: 'BRL',
                }).format(stats.kpis.total_amount_reconciled)}
              </Typography>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Ações Rápidas
            </Typography>
            <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Typography
                variant="body2"
                color="primary"
                sx={{ cursor: 'pointer', '&:hover': { textDecoration: 'underline' } }}
                onClick={() => (window.location.href = '/reconciliation')}
              >
                → Executar Nova Reconciliação
              </Typography>
              <Typography
                variant="body2"
                color="primary"
                sx={{ cursor: 'pointer', '&:hover': { textDecoration: 'underline' } }}
                onClick={() => (window.location.href = '/divergences')}
              >
                → Ver Divergências Pendentes ({stats.kpis.pending_divergences})
              </Typography>
              <Typography
                variant="body2"
                color="primary"
                sx={{ cursor: 'pointer', '&:hover': { textDecoration: 'underline' } }}
                onClick={() => (window.location.href = '/reports')}
              >
                → Gerar Relatórios
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
