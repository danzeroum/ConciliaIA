import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { AppLayout } from './components/layout/AppLayout';
import { lightTheme, darkTheme } from './theme/theme';
import { useUIStore } from './store/ui.store';
import { LoginPage } from './pages/Login/Login';
import { DashboardPage } from './pages/Dashboard/Dashboard';
import { SalesPage } from './pages/Sales/Sales';
import { ReconciliationPage } from './pages/Reconciliation/Reconciliation';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000,
    },
  },
});

export function App() {
  const theme = useUIStore((state) => state.theme);

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme === 'light' ? lightTheme : darkTheme}>
        <CssBaseline />
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />

            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <AppLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<DashboardPage />} />
              <Route path="sales" element={<SalesPage />} />
              <Route path="reconciliation" element={<ReconciliationPage />} />
              <Route path="transactions" element={<div>Transações (em desenvolvimento)</div>} />
              <Route path="divergences" element={<div>Divergências (em desenvolvimento)</div>} />
              <Route path="reports" element={<div>Relatórios (em desenvolvimento)</div>} />
              <Route path="settings" element={<div>Configurações (em desenvolvimento)</div>} />
            </Route>

            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
