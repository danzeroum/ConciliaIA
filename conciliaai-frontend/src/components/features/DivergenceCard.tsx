import {
  Card,
  CardContent,
  Typography,
  Chip,
  Box,
  Button,
  Divider,
} from '@mui/material';
import WarningIcon from '@mui/icons-material/Warning';
import ErrorIcon from '@mui/icons-material/Error';
import InfoIcon from '@mui/icons-material/Info';
import { Divergence } from '@/api/divergences.api';

interface DivergenceCardProps {
  divergence: Divergence;
  onResolve: (id: string) => void;
  onViewDetails: (id: string) => void;
}

const severityConfig = {
  critical: { color: 'error' as const, icon: ErrorIcon, label: 'Crítico' },
  high: { color: 'error' as const, icon: WarningIcon, label: 'Alto' },
  medium: { color: 'warning' as const, icon: WarningIcon, label: 'Médio' },
  low: { color: 'info' as const, icon: InfoIcon, label: 'Baixo' },
};

export function DivergenceCard({
  divergence,
  onResolve,
  onViewDetails,
}: DivergenceCardProps) {
  const config = severityConfig[divergence.severity];
  const SeverityIcon = config.icon;

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR');
  };

  return (
    <Card
      sx={{
        border: (theme) => `2px solid ${theme.palette[config.color].main}`,
        '&:hover': {
          boxShadow: 3,
        },
      }}
    >
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Box display="flex" alignItems="center" gap={1}>
            <SeverityIcon color={config.color} />
            <Typography variant="h6" component="div">
              {divergence.type.replace(/_/g, ' ').toUpperCase()}
            </Typography>
          </Box>
          <Chip
            label={config.label}
            color={config.color}
            size="small"
          />
        </Box>

        <Typography variant="body2" color="text.secondary" gutterBottom>
          <strong>Valor em Risco:</strong> {formatCurrency(divergence.amount_at_risk)}
        </Typography>

        {divergence.variance_percent && (
          <Typography variant="body2" color="text.secondary" gutterBottom>
            <strong>Variação:</strong> {divergence.variance_percent.toFixed(2)}%
          </Typography>
        )}

        <Typography variant="body2" color="text.secondary" gutterBottom>
          <strong>Detectado em:</strong> {formatDate(divergence.detected_at)}
        </Typography>

        {divergence.resolved_at ? (
          <Chip label="Resolvido" color="success" size="small" sx={{ mt: 1 }} />
        ) : (
          <Chip label="Pendente" color="warning" size="small" sx={{ mt: 1 }} />
        )}

        <Divider sx={{ my: 2 }} />

        <Box display="flex" gap={1}>
          <Button
            size="small"
            variant="outlined"
            onClick={() => onViewDetails(divergence.id)}
          >
            Ver Detalhes
          </Button>
          {!divergence.resolved_at && (
            <Button
              size="small"
              variant="contained"
              onClick={() => onResolve(divergence.id)}
            >
              Resolver
            </Button>
          )}
        </Box>
      </CardContent>
    </Card>
  );
}
