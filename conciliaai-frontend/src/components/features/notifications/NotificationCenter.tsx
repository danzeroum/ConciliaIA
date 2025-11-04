import { type MouseEvent, useCallback, useEffect, useState } from 'react';
import {
  Badge,
  Box,
  Chip,
  Divider,
  IconButton,
  ListItemText,
  Menu,
  MenuItem,
  Typography,
} from '@mui/material';
import NotificationsIcon from '@mui/icons-material/Notifications';

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

const priorityChipColor: Record<NotificationItem['priority'], 'default' | 'info' | 'warning' | 'error'> = {
  info: 'default',
  low: 'default',
  medium: 'info',
  high: 'warning',
  critical: 'error',
};

export function NotificationCenter() {
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState<number>(0);

  const isOpen = Boolean(anchorEl);

  const loadNotifications = useCallback(async () => {
    try {
      const [listResponse, countResponse] = await Promise.all([
        apiClient.get<{ notifications: NotificationItem[] }>('/api/v1/notifications', {
          params: { unread_only: true },
        }),
        apiClient.get<{ unread_count: number }>('/api/v1/notifications/unread-count'),
      ]);

      setNotifications(listResponse.data.notifications);
      setUnreadCount(countResponse.data.unread_count);
    } catch (error) {
      console.error('Erro ao carregar notificações', error);
    }
  }, []);

  useEffect(() => {
    loadNotifications();

    const interval = window.setInterval(loadNotifications, 60_000);
    return () => window.clearInterval(interval);
  }, [loadNotifications]);

  const handleMenuOpen = (event: MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleNotificationClick = async (notification: NotificationItem) => {
    try {
      await apiClient.post(`/api/v1/notifications/${notification.id}/mark-read`);

      setNotifications((prev) => prev.filter((item) => item.id !== notification.id));
      setUnreadCount((prev) => Math.max(0, prev - 1));

      if (notification.action_url) {
        window.location.href = notification.action_url;
      }
    } catch (error) {
      console.error('Erro ao marcar notificação como lida', error);
    } finally {
      handleMenuClose();
    }
  };

  return (
    <>
      <IconButton color="inherit" onClick={handleMenuOpen} aria-label="Notificações">
        <Badge badgeContent={unreadCount} color="error" max={99}>
          <NotificationsIcon />
        </Badge>
      </IconButton>

      <Menu anchorEl={anchorEl} open={isOpen} onClose={handleMenuClose} PaperProps={{ sx: { width: 360, maxHeight: 420 } }}>
        <Box sx={{ p: 2 }}>
          <Typography variant="h6">Notificações</Typography>
        </Box>

        <Divider />

        {notifications.length === 0 ? (
          <Box sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Nenhuma notificação nova
            </Typography>
          </Box>
        ) : (
          notifications.map((notification) => {
            const chipColor = priorityChipColor[notification.priority];
            const borderColor = chipColor === 'default' ? 'transparent' : `${chipColor}.main`;

            return (
            <MenuItem
              key={notification.id}
              onClick={() => handleNotificationClick(notification)}
              sx={{
                py: 2,
                borderLeft: 3,
                borderColor,
                '&:hover': { bgcolor: 'action.hover' },
              }}
            >
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                    <Typography variant="subtitle2">{notification.title}</Typography>
                    <Chip
                      label={notification.priority.toUpperCase()}
                      size="small"
                      color={chipColor}
                    />
                  </Box>
                }
                secondary={
                  <Typography variant="body2" color="text.secondary" noWrap>
                    {notification.message}
                  </Typography>
                }
              />
            </MenuItem>
            );
          })
        )}

        <Divider />

        <MenuItem
          onClick={() => {
            window.location.href = '/notifications';
            handleMenuClose();
          }}
        >
          <Typography variant="body2" color="primary" sx={{ width: '100%', textAlign: 'center' }}>
            Ver todas
          </Typography>
        </MenuItem>
      </Menu>
    </>
  );
}

export default NotificationCenter;
