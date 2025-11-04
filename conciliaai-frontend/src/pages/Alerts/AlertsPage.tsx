import { useEffect, useState } from 'react';
import { Alert, Box, Card, CardContent, Chip, CircularProgress, Typography } from '@mui/material';
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive';

import { apiClient } from '../../services/api';

interface AlertItem {
  type: string;
  severity: string;
  title: string;
  message: string;
  reference_id?: string;
}

const severityColor: Record<string, 'default' | 'primary' | 'error' | 'warning' | 'success'> = {
  critical: 'error',
  high: 'warning',
  medium: 'primary',
  low: 'default',
};

const AlertsPage = () => {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchAlerts = async () => {
      setLoading(true);
      setError('');
      try {
        const response = await apiClient.get<AlertItem[]>('/alerts/proactive');
        setAlerts(response.data);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Não foi possível carregar os alertas.');
      } finally {
        setLoading(false);
      }
    };

    fetchAlerts();
  }, []);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Alertas Proativos
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Centralize avisos importantes: chargebacks, pagamentos atrasados e ações sugeridas.
      </Typography>

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {error && <Alert severity="error">{error}</Alert>}

      {!loading && alerts.length === 0 && !error && (
        <Alert severity="success">Tudo certo! Nenhum alerta pendente no momento.</Alert>
      )}

      <Box sx={{ display: 'grid', gap: 2, mt: 2 }}>
        {alerts.map((alert) => (
          <Card key={`${alert.type}-${alert.reference_id || alert.title}`}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1, gap: 1 }}>
                <NotificationsActiveIcon color="warning" />
                <Typography variant="h6">{alert.title}</Typography>
                <Chip
                  label={alert.severity.toUpperCase()}
                  color={severityColor[alert.severity] || 'default'}
                  size="small"
                />
              </Box>
              <Typography variant="body1" gutterBottom>
                {alert.message}
              </Typography>
              {alert.reference_id && (
                <Typography variant="caption" color="text.secondary">
                  Referência: {alert.reference_id}
                </Typography>
              )}
            </CardContent>
          </Card>
        ))}
      </Box>
    </Box>
  );
};

export default AlertsPage;
