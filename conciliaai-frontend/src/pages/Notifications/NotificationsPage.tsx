import { useCallback, useEffect, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Stack,
  Typography,
} from '@mui/material';

import { apiClient } from '@/api/axios-config';

interface NotificationItem {
  id: string;
  title: string;
  message: string;
  priority: 'info' | 'low' | 'medium' | 'high' | 'critical';
  action_url: string | null;
  is_read: boolean;
  created_at: string;
}

const priorityColor: Record<NotificationItem['priority'], 'default' | 'primary' | 'warning' | 'error'> = {
  info: 'default',
  low: 'default',
  medium: 'primary',
  high: 'warning',
  critical: 'error',
};

const priorityLabel: Record<NotificationItem['priority'], string> = {
  info: 'Informativo',
  low: 'Baixo',
  medium: 'Médio',
  high: 'Alto',
  critical: 'Crítico',
};

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  const loadNotifications = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const response = await apiClient.get<{ notifications: NotificationItem[] }>('/api/v1/notifications');
      setNotifications(response.data.notifications);
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? 'Não foi possível carregar as notificações.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadNotifications();
  }, [loadNotifications]);

  const handleMarkAsRead = async (notification: NotificationItem) => {
    try {
      await apiClient.post(`/api/v1/notifications/${notification.id}/mark-read`);
      setNotifications((prev) =>
        prev.map((item) => (item.id === notification.id ? { ...item, is_read: true } : item)),
      );
    } catch (err) {
      console.error('Erro ao marcar notificação como lida', err);
    }
  };

  return (
    <Box>
      <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 3 }}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Centro de Notificações
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Receba apenas o que importa: atrasos, quedas de venda e chargebacks em linguagem natural.
          </Typography>
        </Box>
      </Stack>

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 6 }}>
          <CircularProgress />
        </Box>
      )}

      {error && !loading && <Alert severity="error">{error}</Alert>}

      {!loading && !error && notifications.length === 0 && (
        <Alert severity="success">Tudo certo! Nenhuma notificação pendente no momento.</Alert>
      )}

      <Stack spacing={2} sx={{ mt: 2 }}>
        {notifications.map((notification) => {
          const createdAt = new Date(notification.created_at).toLocaleString('pt-BR', {
            day: '2-digit',
            month: 'short',
            hour: '2-digit',
            minute: '2-digit',
          });

          return (
            <Card key={notification.id} variant={notification.is_read ? 'outlined' : undefined}>
              <CardContent>
                <Stack direction="row" justifyContent="space-between" alignItems="flex-start" spacing={2}>
                  <Box sx={{ flex: 1 }}>
                    <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                      <Typography variant="h6">{notification.title}</Typography>
                      <Chip
                        size="small"
                        color={priorityColor[notification.priority]}
                        label={priorityLabel[notification.priority]}
                      />
                    </Stack>
                    <Typography variant="body1" sx={{ mb: 1 }}>
                      {notification.message}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {createdAt}
                    </Typography>
                  </Box>

                  <Stack spacing={1} alignItems="flex-end">
                    {!notification.is_read && (
                      <Button size="small" onClick={() => handleMarkAsRead(notification)}>
                        Marcar como lida
                      </Button>
                    )}
                    {notification.action_url && (
                      <Button
                        size="small"
                        variant="contained"
                        color="primary"
                        href={notification.action_url}
                      >
                        Ver detalhes
                      </Button>
                    )}
                  </Stack>
                </Stack>
              </CardContent>
            </Card>
          );
        })}
      </Stack>
    </Box>
  );
}
