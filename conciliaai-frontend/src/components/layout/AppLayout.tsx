import React from 'react';
import { Outlet } from 'react-router-dom';
import { Box } from '@mui/material';
import { AppBar } from './AppBar/AppBar';
import { Sidebar } from './Sidebar/Sidebar';
import { useUIStore } from '@/store/ui.store';

const DRAWER_WIDTH = 260;
const APPBAR_HEIGHT = 64;

export function AppLayout() {
  const sidebarOpen = useUIStore((state) => state.sidebarOpen);

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <AppBar />
      <Sidebar />

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          mt: `${APPBAR_HEIGHT}px`,
          ml: sidebarOpen ? `${DRAWER_WIDTH}px` : 0,
          transition: (theme) =>
            theme.transitions.create(['margin'], {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.leavingScreen,
            }),
        }}
      >
        <Outlet />
      </Box>
    </Box>
  );
}
