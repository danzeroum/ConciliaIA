#!/bin/bash
set -e

echo "🎨 ConciliaAI Frontend Setup"
echo "============================"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 20 LTS first."
    exit 1
fi

echo "✅ Node.js $(node -v) found"

# Check if pnpm is installed
if ! command -v pnpm &> /dev/null; then
    echo "📦 Installing pnpm..."
    npm install -g pnpm
fi

echo "✅ pnpm $(pnpm -v) found"

# Create frontend directory
echo ""
echo "📁 Creating frontend directory..."
mkdir -p frontend
cd frontend

# Initialize Vite project
echo ""
echo "⚡ Initializing Vite + React + TypeScript..."
pnpm create vite . --template react-ts

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pnpm install

# Install MUI and other core libraries
echo ""
echo "🎨 Installing UI libraries..."
pnpm add @mui/material @mui/icons-material @emotion/react @emotion/styled

# Install routing
echo ""
echo "🗺️  Installing routing..."
pnpm add react-router-dom

# Install state management
echo ""
echo "🗄️  Installing state management..."
pnpm add zustand @tanstack/react-query

# Install forms and validation
echo ""
echo "📝 Installing forms..."
pnpm add react-hook-form @hookform/resolvers zod

# Install utilities
echo ""
echo "🛠️  Installing utilities..."
pnpm add axios date-fns recharts @tanstack/react-table

# Install dev dependencies
echo ""
echo "🔧 Installing dev dependencies..."
pnpm add -D @types/node vitest @testing-library/react @testing-library/jest-dom jsdom

# Create folder structure
echo ""
echo "📂 Creating folder structure..."
mkdir -p src/{components,pages,store,api,hooks,utils,types,styles}
mkdir -p src/components/{common,layout,features}
mkdir -p src/pages/{auth,dashboard,sales,transactions,reports}

# Create .env file
echo ""
echo "🔐 Creating .env file..."
cat > .env.local << 'ENV'
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=ConciliaAI
VITE_APP_VERSION=1.0.0
ENV

# Create basic API client
echo ""
echo "🌐 Creating API client..."
cat > src/api/client.ts << 'CLIENT'
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
CLIENT

# Create auth service
echo ""
echo "🔐 Creating auth service..."
cat > src/api/auth.ts << 'AUTH'
import apiClient from './client';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export const authService = {
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const { data } = await apiClient.post('/auth/login', credentials);
    return data;
  },

  async logout() {
    await apiClient.post('/auth/logout');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
};
AUTH

# Create Login page
echo ""
echo "🔑 Creating Login page..."
cat > src/pages/auth/Login.tsx << 'LOGIN'
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  Container,
  Alert,
} from '@mui/material';
import { authService } from '../../api/auth';

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await authService.login({ email, password });
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Email ou senha inválidos');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Paper elevation={3} sx={{ p: 4, width: '100%' }}>
          <Typography variant="h4" component="h1" gutterBottom align="center">
            ConciliaAI
          </Typography>
          <Typography variant="body2" color="text.secondary" align="center" sx={{ mb: 3 }}>
            Sistema de Reconciliação Financeira
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <TextField
              label="Email"
              type="email"
              fullWidth
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              sx={{ mb: 2 }}
              autoFocus
            />

            <TextField
              label="Senha"
              type="password"
              fullWidth
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              sx={{ mb: 3 }}
            />

            <Button
              type="submit"
              variant="contained"
              fullWidth
              size="large"
              disabled={loading}
            >
              {loading ? 'Entrando...' : 'Entrar'}
            </Button>
          </form>

          <Box sx={{ mt: 2, textAlign: 'center' }}>
            <Typography variant="caption" color="text.secondary">
              Use: test@example.com / SecurePassword123!
            </Typography>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
}
LOGIN

# Create Dashboard page
echo ""
echo "📊 Creating Dashboard page..."
cat > src/pages/dashboard/Dashboard.tsx << 'DASHBOARD'
import { Box, Typography, Container, Paper, Grid } from '@mui/material';

export default function Dashboard() {
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6">Total de Vendas</Typography>
            <Typography variant="h4">R$ 0,00</Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6">Transações</Typography>
            <Typography variant="h4">0</Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6">Divergências</Typography>
            <Typography variant="h4">0</Typography>
          </Paper>
        </Grid>
      </Grid>

      <Box sx={{ mt: 3 }}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Bem-vindo ao ConciliaAI MVP
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Sistema de reconciliação financeira com IA
          </Typography>
        </Paper>
      </Box>
    </Container>
  );
}
DASHBOARD

# Update App.tsx with routing
echo ""
echo "🗺️  Setting up routing..."
cat > src/App.tsx << 'APP'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import Login from './pages/auth/Login';
import Dashboard from './pages/dashboard/Dashboard';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
  },
});

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('access_token');
  return token ? <>{children}</> : <Navigate to="/login" replace />;
}

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
APP

# Update vite.config.ts with proxy
echo ""
echo "⚙️  Configuring Vite proxy..."
cat > vite.config.ts << 'VITE'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/auth': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
VITE

# Cleanup: return to repository root
echo ""
cd ..

echo "✅ Frontend setup complete!"
echo ""
echo "🚀 Next steps:"
echo "   1. cd frontend"
echo "   2. pnpm dev"
echo "   3. Open http://localhost:3000"
echo "   4. Login with: test@example.com / SecurePassword123!"
echo ""
