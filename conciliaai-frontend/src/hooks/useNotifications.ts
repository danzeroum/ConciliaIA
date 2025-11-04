import { useCallback } from 'react';
import { useUIStore } from '@/store/ui.store';

type NotificationType = 'success' | 'error' | 'warning' | 'info';

interface NotificationPayload {
  type: NotificationType;
  message: string;
  duration?: number;
}

export function useNotifications() {
  const addNotification = useUIStore((state) => state.addNotification);

  const showNotification = useCallback(
    ({ type, message, duration }: NotificationPayload) => {
      addNotification({ type, message, duration });
    },
    [addNotification]
  );

  const showSuccess = useCallback(
    (message: string) => {
      showNotification({ type: 'success', message, duration: 5000 });
    },
    [showNotification]
  );

  const showError = useCallback(
    (message: string) => {
      showNotification({ type: 'error', message, duration: 7000 });
    },
    [showNotification]
  );

  const showWarning = useCallback(
    (message: string) => {
      showNotification({ type: 'warning', message, duration: 6000 });
    },
    [showNotification]
  );

  const showInfo = useCallback(
    (message: string) => {
      showNotification({ type: 'info', message, duration: 5000 });
    },
    [showNotification]
  );

  return {
    showSuccess,
    showError,
    showWarning,
    showInfo,
  };
}
