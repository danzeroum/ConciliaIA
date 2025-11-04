import React from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Grid,
  Paper,
  Typography,
} from '@mui/material';
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
  subtitle?: string;
  icon: React.ReactElement;
  color?: 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success';
  trend?: {
    value: number;
    isPositive: boolean;
  };
}

function KPICard({ title, value, subtitle, icon, color = 'primary', trend }: KPICardProps) {
  return (
    <Card
      sx={{
        height: '100%',
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 4,
        },
      }}
    >
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start">
          <Box flex={1}>
            <Typography color="text.secondary" variant="body2" gutterBottom fontWeight="medium">
              {title}
            </Typography>
            <Typography variant="h4" component="div" fontWeight="bold" gutterBottom>
              {value}
            </Typography>
            {subtitle && (
              <Typography variant="body2" color="text.secondary">
                {subtitle}
              </Typography>
            )}
            {trend && (
              <Box display="flex" alignItems="center" mt={1}>
                <TrendingUpIcon
                  fontSize="small"
                  color={trend.isPositive ? 'success' : 'error'}
                  sx={{
                    transform: trend.isPositive ? 'none' : 'rotate(180deg)',
                    mr: 0.5,
                  }}
                />
                <Typography
                  variant="body2"
                  color={trend.isPositive ? 'success.main' : 'error.main'}
                  fontWeight="medium"
                >
                  {trend.isPositive ? '+' : ''}
                  {trend.value}%
                </Typography>
              </Box>
            )}
          </Box>
          <Box
            sx={{
              color: `${color}.main`,
              backgroundColor: `${color}.50`,
              borderRadius: '12px',
              p: 1.5,
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

export default function Dashboard() {
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
        <Typography color="error">
          Erro ao carregar estatísticas do dashboard. Tente recarregar a página.
        </Typography>
      </Box>
    );
  }

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography variant="h4" fontWeight="bold">
          Dashboard
        </Typography>
        <Button variant="outlined" onClick={() => (window.location.href = '/reconciliation')}>
          Nova Reconciliação
        </Button>
      </Box>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Accuracy"
            value={`${stats.kpis.accuracy.toFixed(1)}%`}
            subtitle="Taxa de acerto"
            icon={<TrendingUpIcon />}
            color="success"
            trend={{ value: 2.5, isPositive: true }}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Matches"
            value={stats.kpis.total_matches.toLocaleString('pt-BR')}
            subtitle="Reconciliações bem-sucedidas"
            icon={<CheckCircleIcon />}
            color="primary"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Divergências"
            value={stats.kpis.pending_divergences}
            subtitle="Pendentes de resolução"
            icon={<WarningIcon />}
            color="warning"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Resolvidas Hoje"
            value={stats.kpis.resolved_today}
            subtitle="Divergências tratadas"
            icon={<DoneAllIcon />}
            color="info"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          <Paper
            sx={{
              p: 3,
              height: '100%',
              transition: 'all 0.3s ease',
              '&:hover': {
                boxShadow: 3,
              },
            }}
          >
            <AccuracyTrendChart data={stats.accuracy_trend} title="Evolução da Accuracy - Últimos 30 dias" />
          </Paper>
        </Grid>

        <Grid item xs={12} lg={4}>
          <Paper
            sx={{
              p: 3,
              height: '100%',
              transition: 'all 0.3s ease',
              '&:hover': {
                boxShadow: 3,
              },
            }}
          >
            <DivergencesPieChart data={stats.top_divergence_types} title="Tipos de Divergências" />
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper
            sx={{
              p: 3,
              transition: 'all 0.3s ease',
              '&:hover': {
                boxShadow: 3,
              },
            }}
          >
            <AcquirerBarChart data={stats.acquirer_breakdown} title="Desempenho por Adquirente" />
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card
            sx={{
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'translateY(-2px)',
                boxShadow: 3,
              },
            }}
          >
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight="bold">
                📊 Resumo do Período
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Box display="flex" justifyContent="space-between" alignItems="center" py={1}>
                  <Typography variant="body2" color="text.secondary">
                    Total de Vendas:
                  </Typography>
                  <Typography variant="body2" fontWeight="medium">
                    {stats.kpis.total_sales.toLocaleString('pt-BR')}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between" alignItems="center" py={1}>
                  <Typography variant="body2" color="text.secondary">
                    Total de Transações:
                  </Typography>
                  <Typography variant="body2" fontWeight="medium">
                    {stats.kpis.total_transactions.toLocaleString('pt-BR')}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between" alignItems="center" py={1}>
                  <Typography variant="body2" color="text.secondary">
                    Valor Reconciliado:
                  </Typography>
                  <Typography variant="body2" fontWeight="medium">
                    {formatCurrency(stats.kpis.total_amount_reconciled)}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card
            sx={{
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'translateY(-2px)',
                boxShadow: 3,
              },
            }}
          >
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight="bold">
                ⚡ Ações Rápidas
              </Typography>
              <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => (window.location.href = '/reconciliation')}
                  sx={{ justifyContent: 'flex-start' }}
                >
                  🔄 Executar Nova Reconciliação
                </Button>
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => (window.location.href = '/divergences')}
                  sx={{ justifyContent: 'flex-start' }}
                >
                  ⚠️ Ver Divergências ({stats.kpis.pending_divergences} pendentes)
                </Button>
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => (window.location.href = '/reports')}
                  sx={{ justifyContent: 'flex-start' }}
                >
                  📈 Gerar Relatórios
                </Button>
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => (window.location.href = '/sales/import')}
                  sx={{ justifyContent: 'flex-start' }}
                >
                  📤 Importar Dados
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
