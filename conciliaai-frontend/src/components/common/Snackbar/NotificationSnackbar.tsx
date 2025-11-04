import { Snackbar, Alert, Slide } from '@mui/material';
import type { SlideProps } from '@mui/material/Slide';
import { useUIStore } from '@/store/ui.store';

const Transition = (props: SlideProps) => <Slide {...props} direction="left" />;

export function NotificationSnackbar() {
  const notifications = useUIStore((state) => state.notifications);
  const removeNotification = useUIStore((state) => state.removeNotification);

  return (
    <>
      {notifications.map((notification) => (
        <Snackbar
          key={notification.id}
          open
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
          autoHideDuration={notification.duration ?? 5000}
          onClose={() => removeNotification(notification.id)}
          TransitionComponent={Transition}
        >
          <Alert
            severity={notification.type}
            variant="filled"
            onClose={() => removeNotification(notification.id)}
            sx={{ width: '100%' }}
          >
            {notification.message}
          </Alert>
        </Snackbar>
      ))}
    </>
  );
}
