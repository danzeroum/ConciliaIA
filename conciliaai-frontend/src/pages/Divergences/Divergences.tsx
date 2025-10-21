import React from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  TextField,
  MenuItem,
  Pagination,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Chip,
} from '@mui/material';
import { useDivergences, useResolveDivergence } from '@/hooks/useDivergences';
import { DivergenceCard } from '@/components/features/DivergenceCard';
import type { Divergence } from '@/api/divergences.api';
import { formatCurrency, formatDateTime } from '@/utils/formatters';

const SEVERITY_OPTIONS = [
  { value: '', label: 'Todas' },
  { value: 'critical', label: 'Crítico' },
  { value: 'high', label: 'Alto' },
  { value: 'medium', label: 'Médio' },
  { value: 'low', label: 'Baixo' },
];

const STATUS_OPTIONS = [
  { value: 'open', label: 'Abertas' },
  { value: 'resolved', label: 'Resolvidas' },
  { value: 'ignored', label: 'Ignoradas' },
];

export function DivergencesPage() {
  const [filters, setFilters] = React.useState({
    severity: '',
    status: 'open' as 'open' | 'resolved' | 'ignored',
    page: 1,
    pageSize: 6,
  });
  const [selectedDivergence, setSelectedDivergence] = React.useState<Divergence | null>(null);
  const [resolutionDialogOpen, setResolutionDialogOpen] = React.useState(false);
  const [resolutionNotes, setResolutionNotes] = React.useState('');
  const resolveDivergence = useResolveDivergence();

  const closeResolutionDialog = () => {
    setResolutionDialogOpen(false);
    setSelectedDivergence(null);
    setResolutionNotes('');
  };

  const { data, isLoading } = useDivergences({
    severity: filters.severity || undefined,
    status: filters.status,
    page: filters.page,
    page_size: filters.pageSize,
  });

  const handlePageChange = (_: unknown, page: number) => {
    setFilters((prev) => ({ ...prev, page }));
  };

  const handleResolve = (id: string) => {
    const divergence = data?.items.find((item) => item.id === id) ?? null;
    setSelectedDivergence(divergence);
    setResolutionNotes('');
    setResolutionDialogOpen(true);
  };

  const handleConfirmResolve = () => {
    if (!selectedDivergence) return;

    resolveDivergence.mutate(
      {
        id: selectedDivergence.id,
        data: {
          resolution: resolutionNotes || 'Resolvido manualmente',
          notes: resolutionNotes || undefined,
        },
      },
      {
        onSuccess: closeResolutionDialog,
      }
    );
  };

  const handleViewDetails = (id: string) => {
    const divergence = data?.items.find((item) => item.id === id) ?? null;
    setSelectedDivergence(divergence);
  };

  const handleCloseDetails = () => setSelectedDivergence(null);

  const divergences = data?.items ?? [];

  return (
    <Box display="flex" flexDirection="column" gap={3}>
      <Typography variant="h4">Divergências</Typography>

      <Paper sx={{ p: 2 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={4}>
            <TextField
              fullWidth
              select
              label="Severidade"
              value={filters.severity}
              onChange={(event) => setFilters((prev) => ({ ...prev, severity: event.target.value, page: 1 }))}
              size="small"
            >
              {SEVERITY_OPTIONS.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <TextField
              fullWidth
              select
              label="Status"
              value={filters.status}
              onChange={(event) =>
                setFilters((prev) => ({ ...prev, status: event.target.value as typeof prev.status, page: 1 }))
              }
              size="small"
            >
              {STATUS_OPTIONS.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
        </Grid>
      </Paper>

      {isLoading ? (
        <Paper sx={{ p: 6 }}>
          <Typography align="center" color="text.secondary">
            Carregando divergências...
          </Typography>
        </Paper>
      ) : divergences.length === 0 ? (
        <Paper sx={{ p: 6 }}>
          <Typography align="center" color="text.secondary">
            Nenhuma divergência encontrada com os filtros selecionados.
          </Typography>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {divergences.map((divergence) => (
            <Grid item xs={12} md={6} key={divergence.id}>
              <DivergenceCard
                divergence={divergence}
                onResolve={handleResolve}
                onViewDetails={handleViewDetails}
              />
            </Grid>
          ))}
        </Grid>
      )}

      {data && data.total_pages > 1 && (
        <Box display="flex" justifyContent="center">
          <Pagination
            count={data.total_pages}
            page={filters.page}
            onChange={handlePageChange}
            color="primary"
          />
        </Box>
      )}

      {/* Details Dialog */}
      <Dialog open={Boolean(selectedDivergence && !resolutionDialogOpen)} onClose={handleCloseDetails} maxWidth="sm" fullWidth>
        <DialogTitle>Detalhes da Divergência</DialogTitle>
        <DialogContent dividers>
          {selectedDivergence ? (
            <Box display="flex" flexDirection="column" gap={2}>
              <Box display="flex" alignItems="center" gap={1}>
                <Chip label={selectedDivergence.severity.toUpperCase()} color="warning" size="small" />
                <Typography variant="h6">
                  {selectedDivergence.type.replace(/_/g, ' ').toUpperCase()}
                </Typography>
              </Box>
              <Typography variant="body2">
                <strong>Valor em risco:</strong> {formatCurrency(selectedDivergence.amount_at_risk)}
              </Typography>
              <Typography variant="body2">
                <strong>Detectado em:</strong> {formatDateTime(selectedDivergence.detected_at)}
              </Typography>
              <Typography variant="body2">
                <strong>Notificação enviada:</strong> {selectedDivergence.notified ? 'Sim' : 'Não'}
              </Typography>
              {selectedDivergence.metadata && (
                <Typography variant="body2" component="pre" sx={{ bgcolor: 'background.default', p: 2 }}>
                  {JSON.stringify(selectedDivergence.metadata, null, 2)}
                </Typography>
              )}
            </Box>
          ) : null}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDetails}>Fechar</Button>
        </DialogActions>
      </Dialog>

      {/* Resolve Dialog */}
      <Dialog open={resolutionDialogOpen} onClose={closeResolutionDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Resolver divergência</DialogTitle>
        <DialogContent dividers>
          <Typography variant="body2" color="text.secondary" paragraph>
            Descreva como a divergência foi resolvida. Essa informação ficará registrada no histórico.
          </Typography>
          <TextField
            label="Descrição da resolução"
            fullWidth
            multiline
            minRows={3}
            value={resolutionNotes}
            onChange={(event) => setResolutionNotes(event.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={closeResolutionDialog}>Cancelar</Button>
          <Button
            variant="contained"
            onClick={handleConfirmResolve}
            disabled={resolveDivergence.isPending}
          >
            Resolver
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
