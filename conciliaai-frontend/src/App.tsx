import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { AppLayout } from './components/layout/AppLayout';
import { lightTheme, darkTheme } from './theme/theme';
import { useUIStore } from './store/ui.store';
import Login from './pages/Login/Login';
import Dashboard from './pages/Dashboard/Dashboard';
import { SalesPage } from './pages/Sales/Sales';
import { ReconciliationPage } from './pages/Reconciliation/Reconciliation';
import BankReconciliationPage from './pages/Reconciliation/BankReconciliation';
import BankReconciliationUpload from './pages/BankReconciliation/BankReconciliationUpload';
import { TransactionsPage } from './pages/Transactions/Transactions';
import { DivergencesPage } from './pages/Divergences/Divergences';
import { ReportsPage } from './pages/Reports/Reports';
import CashflowDashboard from './pages/Reports/CashflowDashboard';
import { SettingsPage } from './pages/Settings/Settings';
import AutoImportSettings from './pages/Settings/AutoImportSettings';
import AlertsPage from './pages/Alerts/AlertsPage';
import { NotificationSnackbar } from './components/common/Snackbar/NotificationSnackbar';

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
            <Route path="/login" element={<Login />} />

            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <AppLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="sales" element={<SalesPage />} />
              <Route path="reconciliation" element={<ReconciliationPage />} />
              <Route path="bank-reconciliation" element={<BankReconciliationPage />} />
              <Route path="bank-reconciliation/upload" element={<BankReconciliationUpload />} />
              <Route path="transactions" element={<TransactionsPage />} />
              <Route path="divergences" element={<DivergencesPage />} />
              <Route path="reports" element={<ReportsPage />} />
              <Route path="reports/cashflow" element={<CashflowDashboard />} />
              <Route path="settings" element={<SettingsPage />} />
              <Route path="settings/auto-import" element={<AutoImportSettings />} />
              <Route path="alerts" element={<AlertsPage />} />
            </Route>

            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </BrowserRouter>
        <NotificationSnackbar />
      </ThemeProvider>
    </QueryClientProvider>
  );
}
