import React, { useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  Tab,
  Tabs,
  TextField,
  Typography,
} from '@mui/material';
import { useDivergences, useResolveDivergence } from '@/hooks/useDivergences';
import { DivergenceCard } from '@/components/features/DivergenceCard';
import type { Divergence } from '@/api/divergences.api';

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
      id={`divergence-tabpanel-${index}`}
      aria-labelledby={`divergence-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

export function DivergencesPage() {
  const [tabValue, setTabValue] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(12);
  const [typeFilter, setTypeFilter] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState<'open' | 'resolved'>('open');
  const [resolveDialogOpen, setResolveDialogOpen] = useState(false);
  const [selectedDivergence, setSelectedDivergence] = useState<Divergence | null>(null);
  const [resolutionNotes, setResolutionNotes] = useState('');

  const {
    data: divergencesData,
    isLoading,
    error,
  } = useDivergences({
    type: typeFilter || undefined,
    severity: severityFilter || undefined,
    status: statusFilter,
    page,
    page_size: pageSize,
  });

  const resolveDivergence = useResolveDivergence();

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
    setStatusFilter(newValue === 0 ? 'open' : 'resolved');
    setPage(1);
  };

  const handleResolve = (id: string) => {
    const divergence = divergencesData?.items.find((item) => item.id === id);
    if (!divergence) return;

    setSelectedDivergence(divergence);
    setResolveDialogOpen(true);
  };

  const handleResolveConfirm = async () => {
    if (!selectedDivergence) return;

    try {
      await resolveDivergence.mutateAsync({
        id: selectedDivergence.id,
        data: {
          resolution: resolutionNotes || 'Resolvido manualmente',
          notes: resolutionNotes || undefined,
        },
      });
      setResolveDialogOpen(false);
      setResolutionNotes('');
      setSelectedDivergence(null);
    } catch (mutationError) {
      console.error('Erro ao resolver divergência', mutationError);
    }
  };

  const handleResolveClose = () => {
    setResolveDialogOpen(false);
    setResolutionNotes('');
    setSelectedDivergence(null);
  };

  const handleViewDetails = (id: string) => {
    const divergence = divergencesData?.items.find((item) => item.id === id) ?? null;
    setSelectedDivergence(divergence);
  };

  const statusCounts = React.useMemo(() => {
    if (!divergencesData?.items) {
      return { open: 0, resolved: 0 };
    }

    return {
      open: divergencesData.items.filter((item) => !item.resolved_at).length,
      resolved: divergencesData.items.filter((item) => Boolean(item.resolved_at)).length,
    };
  }, [divergencesData]);

  if (error) {
    const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido';
    return (
      <Box>
        <Alert severity="error">Erro ao carregar divergências: {errorMessage}</Alert>
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Divergências</Typography>
        <Button
          variant="outlined"
          onClick={() => {
            setTypeFilter('');
            setSeverityFilter('');
            setPageSize(12);
            setPage(1);
          }}
        >
          Limpar Filtros
        </Button>
      </Box>

      <Card sx={{ mb: 3 }}>
        <CardContent sx={{ p: 0 }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="divergence tabs">
            <Tab
              id="divergence-tab-0"
              aria-controls="divergence-tabpanel-0"
              label={
                <Box display="flex" alignItems="center" gap={1}>
                  <Typography>Pendentes</Typography>
                  <Chip
                    label={statusCounts.open}
                    size="small"
                    color="warning"
                    variant={tabValue === 0 ? 'filled' : 'outlined'}
                  />
                </Box>
              }
            />
            <Tab
              id="divergence-tab-1"
              aria-controls="divergence-tabpanel-1"
              label={
                <Box display="flex" alignItems="center" gap={1}>
                  <Typography>Resolvidas</Typography>
                  <Chip
                    label={statusCounts.resolved}
                    size="small"
                    color="success"
                    variant={tabValue === 1 ? 'filled' : 'outlined'}
                  />
                </Box>
              }
            />
          </Tabs>

          <Box sx={{ p: 2 }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={4}>
                <FormControl fullWidth size="small">
                  <InputLabel id="filter-type-label">Tipo</InputLabel>
                  <Select
                    labelId="filter-type-label"
                    value={typeFilter}
                    label="Tipo"
                    onChange={(event) => {
                      setTypeFilter(event.target.value);
                      setPage(1);
                    }}
                  >
                    <MenuItem value="">Todos os Tipos</MenuItem>
                    <MenuItem value="amount_mismatch">Diferença de Valor</MenuItem>
                    <MenuItem value="date_mismatch">Diferença de Data</MenuItem>
                    <MenuItem value="missing_sale">Venda Não Encontrada</MenuItem>
                    <MenuItem value="missing_transaction">Transação Não Encontrada</MenuItem>
                    <MenuItem value="installment_mismatch">Divergência de Parcelas</MenuItem>
                    <MenuItem value="mdr_variance">Variação de MDR</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={4}>
                <FormControl fullWidth size="small">
                  <InputLabel id="filter-severity-label">Severidade</InputLabel>
                  <Select
                    labelId="filter-severity-label"
                    value={severityFilter}
                    label="Severidade"
                    onChange={(event) => {
                      setSeverityFilter(event.target.value);
                      setPage(1);
                    }}
                  >
                    <MenuItem value="">Todas as Severidades</MenuItem>
                    <MenuItem value="critical">Crítica</MenuItem>
                    <MenuItem value="high">Alta</MenuItem>
                    <MenuItem value="medium">Média</MenuItem>
                    <MenuItem value="low">Baixa</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  size="small"
                  label="Itens por página"
                  type="number"
                  value={pageSize}
                  onChange={(event) => {
                    const nextValue = Number(event.target.value) || 1;
                    setPageSize(Math.min(Math.max(nextValue, 1), 100));
                    setPage(1);
                  }}
                  InputProps={{ inputProps: { min: 1, max: 100 } }}
                />
              </Grid>
            </Grid>
          </Box>
        </CardContent>
      </Card>

      <TabPanel value={tabValue} index={0}>
        {isLoading ? (
          <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
            <CircularProgress />
          </Box>
        ) : (divergencesData?.items.length ?? 0) === 0 ? (
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="h6" color="text.secondary">
                🎉 Nenhuma divergência pendente!
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Todas as divergências foram resolvidas ou não há novas divergências para exibir.
              </Typography>
            </CardContent>
          </Card>
        ) : (
          <Grid container spacing={3}>
            {divergencesData?.items.map((divergence) => (
              <Grid item xs={12} md={6} lg={4} key={divergence.id}>
                <DivergenceCard
                  divergence={divergence}
                  onResolve={handleResolve}
                  onViewDetails={handleViewDetails}
                />
              </Grid>
            ))}
          </Grid>
        )}
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        {isLoading ? (
          <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
            <CircularProgress />
          </Box>
        ) : (divergencesData?.items.length ?? 0) === 0 ? (
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="h6" color="text.secondary">
                📝 Nenhuma divergência resolvida
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                As divergências resolvidas aparecerão aqui.
              </Typography>
            </CardContent>
          </Card>
        ) : (
          <Grid container spacing={3}>
            {divergencesData?.items.map((divergence) => (
              <Grid item xs={12} md={6} lg={4} key={divergence.id}>
                <DivergenceCard
                  divergence={divergence}
                  onResolve={handleResolve}
                  onViewDetails={handleViewDetails}
                />
              </Grid>
            ))}
          </Grid>
        )}
      </TabPanel>

      {divergencesData && divergencesData.total > pageSize && (
        <Box display="flex" justifyContent="center" alignItems="center" mt={3} gap={2}>
          <Button
            variant="outlined"
            disabled={page <= 1}
            onClick={() => setPage((prev) => Math.max(prev - 1, 1))}
          >
            Anterior
          </Button>
          <Typography variant="body2" color="text.secondary">
            Página {page} de {Math.ceil(divergencesData.total / pageSize)}
          </Typography>
          <Button
            variant="outlined"
            disabled={page >= Math.ceil(divergencesData.total / pageSize)}
            onClick={() => setPage((prev) => prev + 1)}
          >
            Próxima
          </Button>
        </Box>
      )}

      <Dialog open={Boolean(selectedDivergence && !resolveDialogOpen)} onClose={() => setSelectedDivergence(null)} maxWidth="sm" fullWidth>
        <DialogTitle>Detalhes da Divergência</DialogTitle>
        <DialogContent dividers>
          {selectedDivergence && (
            <Box display="flex" flexDirection="column" gap={2}>
              <Box display="flex" alignItems="center" gap={1}>
                <Chip label={selectedDivergence.severity.toUpperCase()} color="warning" size="small" />
                <Typography variant="h6">
                  {selectedDivergence.type.replace(/_/g, ' ').toUpperCase()}
                </Typography>
              </Box>
              <Typography variant="body2">
                <strong>Valor em risco:</strong>{' '}
                {new Intl.NumberFormat('pt-BR', {
                  style: 'currency',
                  currency: 'BRL',
                }).format(selectedDivergence.amount_at_risk)}
              </Typography>
              <Typography variant="body2">
                <strong>Detectado em:</strong>{' '}
                {new Date(selectedDivergence.detected_at).toLocaleDateString('pt-BR')}
              </Typography>
              <Typography variant="body2">
                <strong>Notificação enviada:</strong>{' '}
                {selectedDivergence.notified ? 'Sim' : 'Não'}
              </Typography>
              {selectedDivergence.metadata && (
                <Typography
                  variant="body2"
                  component="pre"
                  sx={{ bgcolor: 'background.default', p: 2, borderRadius: 1 }}
                >
                  {JSON.stringify(selectedDivergence.metadata, null, 2)}
                </Typography>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedDivergence(null)}>Fechar</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={resolveDialogOpen} onClose={handleResolveClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          Resolver Divergência
          {selectedDivergence && (
            <Chip
              label={selectedDivergence.type.replace(/_/g, ' ').toUpperCase()}
              color="primary"
              size="small"
              sx={{ ml: 2 }}
            />
          )}
        </DialogTitle>
        <DialogContent>
          {selectedDivergence && (
            <Box mb={2}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                <strong>Valor em Risco:</strong>{' '}
                {new Intl.NumberFormat('pt-BR', {
                  style: 'currency',
                  currency: 'BRL',
                }).format(selectedDivergence.amount_at_risk)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                <strong>Detectado em:</strong>{' '}
                {new Date(selectedDivergence.detected_at).toLocaleDateString('pt-BR')}
              </Typography>
            </Box>
          )}

          <Typography variant="body2" gutterBottom>
            Descreva como esta divergência foi resolvida:
          </Typography>
          <TextField
            autoFocus
            multiline
            rows={4}
            fullWidth
            value={resolutionNotes}
            onChange={(event) => setResolutionNotes(event.target.value)}
            placeholder="Ex: Valor ajustado manualmente, transação encontrada em lote posterior, etc."
            sx={{ mt: 1 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleResolveClose}>Cancelar</Button>
          <Button
            onClick={handleResolveConfirm}
            variant="contained"
            disabled={!resolutionNotes.trim() || resolveDivergence.isPending}
          >
            {resolveDivergence.isPending ? <CircularProgress size={20} /> : 'Confirmar Resolução'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
