import React, { useMemo, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Grid,
  MenuItem,
  Paper,
  Tab,
  Tabs,
  TextField,
  Typography,
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { ptBR } from 'date-fns/locale';
import { AccuracyTrendChart } from '@/components/charts/AccuracyTrendChart';
import { DivergencesPieChart } from '@/components/charts/DivergencesPieChart';
import { AcquirerBarChart } from '@/components/charts/AcquirerBarChart';
import { PDFExport } from '@/components/features/PDFExport';
import {
  useAccuracyReport,
  useAcquirerPerformanceReport,
  useDivergenceAnalysisReport,
} from '@/hooks/useReports';
import {
  useExportAccuracyReportExcel,
  useExportDivergenceReportExcel,
} from '@/hooks/useExport';
import { useUIStore } from '@/store/ui.store';
import type { TrendDataPoint } from '@/api/stats.api';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel({ children, value, index, ...other }: TabPanelProps) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`report-tabpanel-${index}`}
      aria-labelledby={`report-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const reportTypes = [
  { value: 'accuracy', label: 'Accuracy' },
  { value: 'divergence', label: 'Análise de Divergências' },
  { value: 'acquirer', label: 'Desempenho por Adquirente' },
  { value: 'settlement', label: 'Análise de Liquidação' },
  { value: 'mdr', label: 'Variação de MDR' },
];

export function ReportsPage() {
  const [tabValue, setTabValue] = useState(0);
  const [startDate, setStartDate] = useState<Date | null>(
    new Date(new Date().getFullYear(), new Date().getMonth(), 1)
  );
  const [endDate, setEndDate] = useState<Date | null>(new Date());

  const startDateParam = startDate ? startDate.toISOString().split('T')[0] : '';
  const endDateParam = endDate ? endDate.toISOString().split('T')[0] : '';

  const accuracyReport = useAccuracyReport(startDateParam, endDateParam);
  const divergenceReport = useDivergenceAnalysisReport(startDateParam, endDateParam);
  const acquirerReport = useAcquirerPerformanceReport(startDateParam, endDateParam);

  const showNotification = useUIStore((state) => state.showNotification);
  const exportAccuracyExcel = useExportAccuracyReportExcel();
  const exportDivergenceExcel = useExportDivergenceReportExcel();

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleExportExcel = () => {
    if (!startDate || !endDate) {
      showNotification('Selecione o período para exportar o relatório', 'warning');
      return;
    }

    const payload = {
      start_date: startDate.toISOString().split('T')[0],
      end_date: endDate.toISOString().split('T')[0],
    };

    switch (tabValue) {
      case 0:
        exportAccuracyExcel.mutate(payload);
        break;
      case 1:
        exportDivergenceExcel.mutate(payload);
        break;
      default:
        showNotification('Exportação para este relatório ainda não está disponível', 'info');
    }
  };

  const excelExporting = exportAccuracyExcel.isPending || exportDivergenceExcel.isPending;

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);

  const accuracyTrendData: TrendDataPoint[] = useMemo(() => {
    if (!accuracyReport.data?.trend) {
      return [];
    }

    return accuracyReport.data.trend.map((item) => ({
      date: item.date,
      value: item.accuracy,
    }));
  }, [accuracyReport.data?.trend]);

  const renderAccuracyReport = () => {
    if (accuracyReport.isLoading) return <CircularProgress />;
    if (accuracyReport.error) return <Alert severity="error">Erro ao carregar relatório de accuracy</Alert>;
    if (!accuracyReport.data) return <Alert severity="info">Selecione um período para gerar o relatório</Alert>;

    return (
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <AccuracyTrendChart data={accuracyTrendData} title="Evolução da Accuracy" />
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📊 Métricas Principais
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Box display="flex" justifyContent="space-between" alignItems="center" py={1}>
                  <Typography variant="body2" color="text.secondary">
                    Accuracy Geral:
                  </Typography>
                  <Typography variant="body1" fontWeight="bold" color="primary.main">
                    {accuracyReport.data.overall_accuracy}%
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between" alignItems="center" py={1}>
                  <Typography variant="body2" color="text.secondary">
                    Total de Vendas:
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {accuracyReport.data.total_sales.toLocaleString('pt-BR')}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between" alignItems="center" py={1}>
                  <Typography variant="body2" color="text.secondary">
                    Matches Realizados:
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {accuracyReport.data.total_matches.toLocaleString('pt-BR')}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between" alignItems="center" py={1}>
                  <Typography variant="body2" color="text.secondary">
                    Divergências:
                  </Typography>
                  <Typography variant="body1" fontWeight="medium" color="warning.main">
                    {accuracyReport.data.total_divergences.toLocaleString('pt-BR')}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📈 Análise de Performance
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary" paragraph>
                  O relatório de accuracy mostra a eficiência do processo de reconciliação durante o período
                  selecionado. Uma accuracy acima de 95% é considerada excelente.
                </Typography>
                <Box display="flex" alignItems="center" gap={1}>
                  <Box
                    sx={{
                      width: 12,
                      height: 12,
                      borderRadius: '50%',
                      backgroundColor:
                        accuracyReport.data.overall_accuracy >= 95
                          ? 'success.main'
                          : accuracyReport.data.overall_accuracy >= 90
                          ? 'warning.main'
                          : 'error.main',
                    }}
                  />
                  <Typography variant="body2" color="text.secondary">
                    {accuracyReport.data.overall_accuracy >= 95
                      ? 'Performance Excelente'
                      : accuracyReport.data.overall_accuracy >= 90
                      ? 'Performance Boa'
                      : 'Performance Requer Atenção'}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  const renderDivergenceReport = () => {
    if (divergenceReport.isLoading) return <CircularProgress />;
    if (divergenceReport.error) return <Alert severity="error">Erro ao carregar relatório de divergências</Alert>;
    if (!divergenceReport.data) return <Alert severity="info">Selecione um período para gerar o relatório</Alert>;

    return (
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <DivergencesPieChart
            data={divergenceReport.data.by_type.map((item) => ({
              type: item.type,
              count: item.count,
            }))}
            title="Divergências por Tipo"
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📋 Resumo de Divergências
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Box display="flex" justifyContent="space-between" alignItems="center" py={1}>
                  <Typography variant="body2" color="text.secondary">
                    Total de Divergências:
                  </Typography>
                  <Typography variant="body1" fontWeight="bold">
                    {divergenceReport.data.total_divergences}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between" alignItems="center" py={1}>
                  <Typography variant="body2" color="text.secondary">
                    Valor em Risco:
                  </Typography>
                  <Typography variant="body1" fontWeight="bold" color="error.main">
                    {formatCurrency(divergenceReport.data.total_amount_at_risk)}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between" alignItems="center" py={1}>
                  <Typography variant="body2" color="text.secondary">
                    Taxa de Resolução:
                  </Typography>
                  <Typography variant="body1" fontWeight="medium" color="success.main">
                    {divergenceReport.data.resolution_rate}%
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between" alignItems="center" py={1}>
                  <Typography variant="body2" color="text.secondary">
                    Tempo Médio de Resolução:
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {divergenceReport.data.avg_resolution_time_hours
                      ? `${divergenceReport.data.avg_resolution_time_hours.toFixed(1)}h`
                      : 'N/A'}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                🚨 Análise por Severidade
              </Typography>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                {divergenceReport.data.by_severity.map((severity) => (
                  <Grid item xs={12} sm={6} md={3} key={severity.severity}>
                    <Paper
                      sx={{
                        p: 2,
                        textAlign: 'center',
                        border: 1,
                        borderColor: 'divider',
                      }}
                    >
                      <Typography
                        variant="h4"
                        fontWeight="bold"
                        color={
                          severity.severity === 'critical'
                            ? 'error.main'
                            : severity.severity === 'high'
                            ? 'warning.main'
                            : severity.severity === 'medium'
                            ? 'info.main'
                            : 'success.main'
                        }
                      >
                        {severity.count}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" textTransform="capitalize">
                        {severity.severity}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {formatCurrency(severity.total_amount)}
                      </Typography>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  const renderAcquirerReport = () => {
    if (acquirerReport.isLoading) return <CircularProgress />;
    if (acquirerReport.error) return <Alert severity="error">Erro ao carregar relatório de adquirentes</Alert>;
    if (!acquirerReport.data) return <Alert severity="info">Selecione um período para gerar o relatório</Alert>;

    return (
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <AcquirerBarChart
            data={acquirerReport.data.acquirers.map((acquirer) => ({
              acquirer: acquirer.acquirer,
              transactions: acquirer.total_transactions,
              amount: acquirer.total_amount,
            }))}
            title="Desempenho por Adquirente"
          />
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📊 Métricas Detalhadas por Adquirente
              </Typography>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                {acquirerReport.data.acquirers.map((acquirer) => (
                  <Grid item xs={12} md={6} lg={4} key={acquirer.acquirer}>
                    <Paper sx={{ p: 2 }}>
                      <Typography variant="subtitle1" fontWeight="bold" gutterBottom textTransform="capitalize">
                        {acquirer.acquirer}
                      </Typography>
                      <Box display="flex" justifyContent="space-between" alignItems="center" py={0.5}>
                        <Typography variant="body2" color="text.secondary">
                          Transações:
                        </Typography>
                        <Typography variant="body2" fontWeight="medium">
                          {acquirer.total_transactions.toLocaleString('pt-BR')}
                        </Typography>
                      </Box>
                      <Box display="flex" justifyContent="space-between" alignItems="center" py={0.5}>
                        <Typography variant="body2" color="text.secondary">
                          Valor Total:
                        </Typography>
                        <Typography variant="body2" fontWeight="medium">
                          {formatCurrency(acquirer.total_amount)}
                        </Typography>
                      </Box>
                      <Box display="flex" justifyContent="space-between" alignItems="center" py={0.5}>
                        <Typography variant="body2" color="text.secondary">
                          Taxa de Match:
                        </Typography>
                        <Typography
                          variant="body2"
                          fontWeight="bold"
                          color={acquirer.match_rate >= 95 ? 'success.main' : 'warning.main'}
                        >
                          {acquirer.match_rate}%
                        </Typography>
                      </Box>
                      {acquirer.avg_mdr_rate && (
                        <Box display="flex" justifyContent="space-between" alignItems="center" py={0.5}>
                          <Typography variant="body2" color="text.secondary">
                            MDR Médio:
                          </Typography>
                          <Typography variant="body2" fontWeight="medium">
                            {acquirer.avg_mdr_rate}%
                          </Typography>
                        </Box>
                      )}
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={ptBR}>
      <Box>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h4">Relatórios</Typography>
          <Box display="flex" gap={1} alignItems="center">
            <Button
              variant="outlined"
              startIcon={excelExporting ? <CircularProgress size={20} /> : <DownloadIcon />}
              onClick={handleExportExcel}
              disabled={excelExporting}
            >
              {excelExporting ? 'Exportando...' : 'Excel'}
            </Button>
            <PDFExport targetElementId="report-content" filename={`relatorio_${reportTypes[tabValue].value}`} />
          </Box>
        </Box>

        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={3}>
                <TextField
                  select
                  fullWidth
                  label="Tipo de Relatório"
                  value={reportTypes[tabValue].value}
                  onChange={(event) => {
                    const newTab = reportTypes.findIndex((type) => type.value === event.target.value);
                    setTabValue(newTab === -1 ? 0 : newTab);
                  }}
                >
                  {reportTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>
              <Grid item xs={12} md={3}>
                <DatePicker label="Data Inicial" value={startDate} onChange={setStartDate} slotProps={{ textField: { fullWidth: true } }} />
              </Grid>
              <Grid item xs={12} md={3}>
                <DatePicker label="Data Final" value={endDate} onChange={setEndDate} slotProps={{ textField: { fullWidth: true } }} />
              </Grid>
              <Grid item xs={12} md={3}>
                <Button
                  fullWidth
                  variant="outlined"
                  onClick={() => {
                    accuracyReport.refetch();
                    divergenceReport.refetch();
                    acquirerReport.refetch();
                  }}
                  disabled={!startDate || !endDate}
                >
                  Atualizar Relatório
                </Button>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        <Paper>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="report tabs">
            <Tab label="Accuracy" />
            <Tab label="Divergências" />
            <Tab label="Adquirentes" />
            <Tab label="Liquidação" disabled />
            <Tab label="MDR" disabled />
          </Tabs>

          <Box id="report-content">
            <TabPanel value={tabValue} index={0}>
              {renderAccuracyReport()}
            </TabPanel>

            <TabPanel value={tabValue} index={1}>
              {renderDivergenceReport()}
            </TabPanel>

            <TabPanel value={tabValue} index={2}>
              {renderAcquirerReport()}
            </TabPanel>

            <TabPanel value={tabValue} index={3}>
              <Alert severity="info">Relatório de Análise de Liquidação em desenvolvimento.</Alert>
            </TabPanel>

            <TabPanel value={tabValue} index={4}>
              <Alert severity="info">Relatório de Variação de MDR em desenvolvimento.</Alert>
            </TabPanel>
          </Box>
        </Paper>
      </Box>
    </LocalizationProvider>
  );
}
