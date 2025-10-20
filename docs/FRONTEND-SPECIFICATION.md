# 🎨 ConciliaAI v7.0 - Frontend Specification

**Project:** ConciliaAI Frontend  
**Version:** 1.0.0  
**Technology Stack:** React 18 + TypeScript + Vite  
**Target:** Modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)  
**Prepared by:** BuildToValue v7.0  
**Date:** 2025-10-19

---

## 📋 Table of Contents

1. [Overview](#-overview)
2. [Technology Stack](#️-technology-stack)
3. [Architecture](#-architecture)
4. [UI/UX Design](#-uiux-design)
5. [Core Features](#-core-features)
6. [Component Structure](#-component-structure)
7. [State Management](#-state-management)
8. [API Integration](#-api-integration)
9. [Authentication Flow](#-authentication-flow)
10. [Routing](#-routing)
11. [Performance](#-performance)
12. [Deployment](#-deployment)
13. [Development Plan](#-development-plan)

---

## 🎯 Overview

### Project Goals

Desenvolver uma interface web moderna, responsiva e intuitiva para o sistema de reconciliação financeira ConciliaAI, permitindo que usuários:

- Visualizem vendas e transações
- Executem reconciliações
- Analisem divergências
- Gerenciem resoluções
- Visualizem relatórios e dashboards
- Configurem integrações com adquirentes

### Target Users

- **Analistas Financeiros** - Reconciliação diária
- **Gestores Financeiros** - Análise e aprovações
- **Controllers** - Relatórios e métricas
- **Administradores** - Configuração do sistema

### Key Requirements

- ✅ Responsivo (Desktop, Tablet, Mobile)
- ✅ Performance (< 2s load time)
- ✅ Acessibilidade (WCAG 2.1 AA)
- ✅ Internacionalização (PT-BR, EN-US)
- ✅ Dark Mode
- ✅ Real-time updates
- ✅ Offline support (progressive)

---

## 🛠️ Technology Stack

### Core Technologies
```json
{
  "framework": "React 18.2+",
  "language": "TypeScript 5.0+",
  "build": "Vite 5.0+",
  "package_manager": "pnpm 8.0+",
  "node_version": "20 LTS"
}
```

### Essential Libraries
```json
{
  "ui_framework": "Material-UI (MUI) 5.14+",
  "routing": "React Router 6.16+",
  "state_management": "Zustand 4.4+",
  "data_fetching": "TanStack Query (React Query) 5.0+",
  "forms": "React Hook Form 7.47+",
  "validation": "Zod 3.22+",
  "charts": "Recharts 2.8+",
  "tables": "TanStack Table 8.10+",
  "dates": "date-fns 2.30+",
  "api_client": "Axios 1.5+",
  "i18n": "react-i18next 13.3+"
}
```

### Development Tools
```json
{
  "linting": "ESLint 8.50+",
  "formatting": "Prettier 3.0+",
  "testing": "Vitest 0.34+ + Testing Library",
  "e2e": "Playwright 1.39+",
  "documentation": "Storybook 7.4+",
  "type_checking": "TypeScript strict mode"
}
```

---

## 🏗️ Architecture

### Project Structure
```
conciliaai-frontend/
├── public/
│   ├── favicon.ico
│   └── manifest.json
├── src/
│   ├── api/                    # API clients
│   │   ├── axios-config.ts
│   │   ├── auth.api.ts
│   │   ├── reconciliation.api.ts
│   │   ├── sales.api.ts
│   │   ├── transactions.api.ts
│   │   └── divergences.api.ts
│   ├── assets/                 # Static assets
│   │   ├── images/
│   │   ├── icons/
│   │   └── fonts/
│   ├── components/             # Reusable components
│   │   ├── common/
│   │   │   ├── Button/
│   │   │   ├── Card/
│   │   │   ├── DataTable/
│   │   │   ├── Modal/
│   │   │   └── ...
│   │   ├── layout/
│   │   │   ├── AppBar/
│   │   │   ├── Sidebar/
│   │   │   ├── Footer/
│   │   │   └── PageLayout/
│   │   └── features/
│   │       ├── SalesList/
│   │       ├── TransactionsList/
│   │       ├── MatchesTable/
│   │       ├── DivergenceCard/
│   │       └── ...
│   ├── hooks/                  # Custom hooks
│   │   ├── useAuth.ts
│   │   ├── useReconciliation.ts
│   │   ├── useSales.ts
│   │   ├── useNotifications.ts
│   │   └── ...
│   ├── pages/                  # Page components
│   │   ├── Login/
│   │   ├── Dashboard/
│   │   ├── Sales/
│   │   ├── Transactions/
│   │   ├── Reconciliation/
│   │   ├── Divergences/
│   │   ├── Reports/
│   │   └── Settings/
│   ├── store/                  # State management
│   │   ├── auth.store.ts
│   │   ├── reconciliation.store.ts
│   │   └── ui.store.ts
│   ├── types/                  # TypeScript types
│   │   ├── api.types.ts
│   │   ├── domain.types.ts
│   │   └── ui.types.ts
│   ├── utils/                  # Utility functions
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   ├── helpers.ts
│   │   └── constants.ts
│   ├── theme/                  # MUI theme
│   │   ├── theme.ts
│   │   ├── colors.ts
│   │   └── typography.ts
│   ├── i18n/                   # Internationalization
│   │   ├── en-US.json
│   │   └── pt-BR.json
│   ├── App.tsx
│   ├── main.tsx
│   └── vite-env.d.ts
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── .storybook/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── vitest.config.ts
├── playwright.config.ts
├── .eslintrc.json
├── .prettierrc
└── README.md
```

### Clean Architecture Layers
```
┌──────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                    │
│  ┌────────────────────────────────────────────────────┐  │
│  │  React Components (Pages + Features)              │  │
│  │  • Login, Dashboard, Reconciliation, etc.         │  │
│  └────────────────────────────────────────────────────┘  │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                      │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Custom Hooks (Business Logic)                     │  │
│  │  • useAuth, useReconciliation, useSales            │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │  State Management (Zustand)                        │  │
│  │  • Auth Store, Reconciliation Store, UI Store      │  │
│  └────────────────────────────────────────────────────┘  │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│                  INFRASTRUCTURE LAYER                    │
│  ┌────────────────────────────────────────────────────┐  │
│  │  API Clients (Axios)                               │  │
│  │  • HTTP requests to backend                        │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │  React Query (Data Fetching & Caching)             │  │
│  │  • Queries, Mutations, Cache management            │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

---

## 🎨 UI/UX Design

### Design System

#### Color Palette
```typescript
// Primary Colors
const colors = {
  primary: {
    main: '#1976d2',      // Blue (confidence, trust)
    light: '#42a5f5',
    dark: '#1565c0',
    contrastText: '#ffffff',
  },
  secondary: {
    main: '#9c27b0',      // Purple (creativity)
    light: '#ba68c8',
    dark: '#7b1fa2',
    contrastText: '#ffffff',
  },
  success: {
    main: '#2e7d32',      // Green (matches)
    light: '#4caf50',
    dark: '#1b5e20',
  },
  error: {
    main: '#d32f2f',      // Red (divergences)
    light: '#ef5350',
    dark: '#c62828',
  },
  warning: {
    main: '#ed6c02',      // Orange (warnings)
    light: '#ff9800',
    dark: '#e65100',
  },
  info: {
    main: '#0288d1',      // Light blue (info)
    light: '#03a9f4',
    dark: '#01579b',
  },
  grey: {
    50: '#fafafa',
    100: '#f5f5f5',
    200: '#eeeeee',
    300: '#e0e0e0',
    400: '#bdbdbd',
    500: '#9e9e9e',
    600: '#757575',
    700: '#616161',
    800: '#424242',
    900: '#212121',
  },
};
```

#### Typography
```typescript
const typography = {
  fontFamily: "'Inter', 'Roboto', 'Arial', sans-serif",
  h1: {
    fontSize: '2.5rem',    // 40px
    fontWeight: 700,
    lineHeight: 1.2,
  },
  h2: {
    fontSize: '2rem',      // 32px
    fontWeight: 600,
    lineHeight: 1.3,
  },
  h3: {
    fontSize: '1.75rem',   // 28px
    fontWeight: 600,
    lineHeight: 1.4,
  },
  h4: {
    fontSize: '1.5rem',    // 24px
    fontWeight: 600,
    lineHeight: 1.4,
  },
  h5: {
    fontSize: '1.25rem',   // 20px
    fontWeight: 500,
    lineHeight: 1.5,
  },
  h6: {
    fontSize: '1rem',      // 16px
    fontWeight: 500,
    lineHeight: 1.5,
  },
  body1: {
    fontSize: '1rem',      // 16px
    fontWeight: 400,
    lineHeight: 1.5,
  },
  body2: {
    fontSize: '0.875rem',  // 14px
    fontWeight: 400,
    lineHeight: 1.43,
  },
  button: {
    fontSize: '0.875rem',
    fontWeight: 500,
    textTransform: 'none',
  },
  caption: {
    fontSize: '0.75rem',   // 12px
    fontWeight: 400,
    lineHeight: 1.66,
  },
};
```

#### Spacing & Layout
```typescript
const spacing = {
  xs: '4px',
  sm: '8px',
  md: '16px',
  lg: '24px',
  xl: '32px',
  xxl: '48px',
};

const breakpoints = {
  xs: 0,      // Mobile
  sm: 600,    // Tablet
  md: 900,    // Small laptop
  lg: 1200,   // Desktop
  xl: 1536,   // Large desktop
};
```

### Component Patterns

#### Button Variants
```tsx
// Primary action
<Button variant="contained" color="primary">
  Reconciliar
</Button>

// Secondary action
<Button variant="outlined" color="primary">
  Cancelar
</Button>

// Tertiary action
<Button variant="text" color="primary">
  Ver Detalhes
</Button>

// Danger action
<Button variant="contained" color="error">
  Excluir
</Button>
```

#### Status Badges
```tsx
// Match status
<Chip label="Matched" color="success" size="small" />
<Chip label="Unmatched" color="error" size="small" />
<Chip label="Pending" color="warning" size="small" />

// Divergence severity
<Chip label="Critical" color="error" icon={<ErrorIcon />} />
<Chip label="High" color="warning" icon={<WarningIcon />} />
<Chip label="Medium" color="info" icon={<InfoIcon />} />
<Chip label="Low" color="default" />
```

---

## 🎯 Core Features

### 1. Dashboard

**Purpose:** Overview de reconciliações e métricas principais

**Components:**
- KPI Cards (Accuracy, Total Matches, Pending Divergences)
- Recent Reconciliations Timeline
- Accuracy Trend Chart (last 30 days)
- Top Divergences by Type
- Quick Actions (Start Reconciliation, View Reports)

**Mock:**
```
┌─────────────────────────────────────────────────────────────┐
│  Dashboard                                    🔔 👤 Settings │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Accuracy │  │  Total   │  │ Pending  │  │ Resolved │  │
│  │  99.5%   │  │ Matches  │  │  Diverg. │  │  Today   │  │
│  │  ▲ 0.2%  │  │  1,234   │  │    12    │  │    45    │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Accuracy Trend (Last 30 days)                      │   │
│  │                                                      │   │
│  │  100% ┤                           ╭─────╮           │   │
│  │   99% ┤         ╭────╮        ╭───╯     ╰──╮        │   │
│  │   98% ┤    ╭────╯    ╰────╭───╯            ╰───     │   │
│  │   97% ┼────╯               │                         │   │
│  │       └────────────────────────────────────────────  │   │
│  │        01/10  08/10  15/10  22/10  29/10            │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────┐  ┌───────────────────┐   │
│  │  Top Divergences            │  │  Quick Actions    │   │
│  │  • Missing Transaction: 8   │  │  ┌──────────────┐ │   │
│  │  • Duplicate: 2             │  │  │ Reconciliar  │ │   │
│  │  • MDR Variance: 1          │  │  └──────────────┘ │   │
│  │  • Amount Mismatch: 1       │  │  ┌──────────────┐ │   │
│  └─────────────────────────────┘  │  │ Ver Relatór. │ │   │
│                                    │  └──────────────┘ │   │
│                                    └───────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 2. Reconciliation

**Purpose:** Executar e acompanhar reconciliações

**Components:**
- Date Range Picker
- Acquirer Filter (Cielo, Rede, Stone)
- Start Reconciliation Button
- Progress Indicator
- Results Table (Matches, Unmatched Sales, Unmatched Transactions)
- Export Button (CSV, Excel, PDF)

**Flow:**
```
1. Selecionar Data Range
2. [Opcional] Filtrar Adquirente
3. Clicar "Reconciliar"
4. Ver Progresso (Loading spinner)
5. Ver Resultados (Matches + Divergences)
6. [Opcional] Exportar Resultados
```

### 3. Sales Management

**Purpose:** Visualizar e gerenciar vendas do ERP/POS

**Components:**
- Search & Filter Toolbar
- Sales Data Table (NSU, Amount, Date, Method, Status)
- Bulk Actions (Import, Export, Delete)
- Sale Detail Modal
- Import Sales Button (CSV, Excel)

**Table Columns:**
- NSU
- Valor
- Data
- Método de Pagamento
- Status (Matched/Unmatched)
- Ações (View, Edit, Delete)

### 4. Transactions Management

**Purpose:** Visualizar transações dos adquirentes

**Components:**
- Search & Filter Toolbar
- Acquirer Filter (Cielo, Rede, Stone)
- Transactions Data Table
- Transaction Detail Modal
- Import from Acquirer Button

**Table Columns:**
- NSU
- Adquirente
- Valor
- Data
- Bandeira
- MDR
- Status
- Ações

### 5. Divergences Management

**Purpose:** Analisar e resolver divergências

**Components:**
- Severity Filter (Critical, High, Medium, Low)
- Type Filter (6 types)
- Status Filter (Open, Resolved, Ignored)
- Divergences List (Cards or Table)
- Divergence Detail Panel
- Resolution Form
- Suggested Actions

**Divergence Card:**
```
┌─────────────────────────────────────────────────────┐
│ 🔴 CRITICAL - Missing Transaction                   │
├─────────────────────────────────────────────────────┤
│ Sale: NSU-123456 | R$ 150.00 | 2025-01-15           │
│ Transaction: Not found                              │
│                                                     │
│ Detected: 2025-01-22 (D+7 alert)                    │
│                                                     │
│ Suggested Actions:                                  │
│  • Contact acquirer (Cielo)                         │
│  • Verify if transaction was canceled               │
│  • Check for chargeback                             │
│                                                     │
│ [Resolver] [Ignorar] [Ver Detalhes]                 │
└─────────────────────────────────────────────────────┘
```

### 6. Reports

**Purpose:** Visualizar relatórios e analytics

**Components:**
- Report Type Selector
- Date Range Picker
- Charts (Bar, Line, Pie)
- Export Button (PDF, Excel)

**Report Types:**
- Accuracy Report (over time)
- Divergence Analysis (by type, severity)
- Acquirer Performance
- Settlement Analysis
- MDR Variance Report

### 7. Settings

**Purpose:** Configurar sistema e integrações

**Sections:**
- **Profile** - Nome, Email, Senha
- **Tenant** - Info da empresa
- **Acquirers** - Configurar credenciais (Cielo, Rede, Stone)
- **Notifications** - Email, Slack, Push
- **Appearance** - Dark Mode, Language
- **Users** - Gestão de usuários (Admin only)

---

## 🧩 Component Structure

### Example: DataTable Component
```tsx
// src/components/common/DataTable/DataTable.tsx

import React from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  flexRender,
} from '@tanstack/react-table';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TablePagination,
  TextField,
  Box,
} from '@mui/material';

interface DataTableProps<T> {
  data: T[];
  columns: ColumnDef<T>[];
  loading?: boolean;
  onRowClick?: (row: T) => void;
  pagination?: boolean;
  searchable?: boolean;
}

export function DataTable<T>({
  data,
  columns,
  loading = false,
  onRowClick,
  pagination = true,
  searchable = true,
}: DataTableProps<T>) {
  const [globalFilter, setGlobalFilter] = React.useState('');

  const table = useReactTable({
    data,
    columns,
    state: {
      globalFilter,
    },
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
  });

  return (
    <Box>
      {searchable && (
        <TextField
          value={globalFilter ?? ''}
          onChange={(e) => setGlobalFilter(e.target.value)}
          placeholder="Buscar..."
          fullWidth
          margin="normal"
        />
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableCell key={header.id}>
                    {flexRender(
                      header.column.columnDef.header,
                      header.getContext()
                    )}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableHead>
          <TableBody>
            {table.getRowModel().rows.map((row) => (
              <TableRow
                key={row.id}
                hover
                onClick={() => onRowClick?.(row.original)}
                sx={{ cursor: onRowClick ? 'pointer' : 'default' }}
              >
                {row.getVisibleCells().map((cell) => (
                  <TableCell key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {pagination && (
        <TablePagination
          component="div"
          count={table.getFilteredRowModel().rows.length}
          page={table.getState().pagination.pageIndex}
          onPageChange={(_, page) => table.setPageIndex(page)}
          rowsPerPage={table.getState().pagination.pageSize}
          onRowsPerPageChange={(e) => table.setPageSize(Number(e.target.value))}
        />
      )}
    </Box>
  );
}
```

---

## 🗄️ State Management

### Zustand Stores

#### Auth Store
```typescript
// src/store/auth.store.ts

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  name: string;
  roles: string[];
  tenantId: string;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;

  // Actions
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshAccessToken: () => Promise<void>;
  updateUser: (user: Partial<User>) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,

      login: async (email, password) => {
        const response = await authApi.login(email, password);
        set({
          user: response.user,
          accessToken: response.accessToken,
          refreshToken: response.refreshToken,
          isAuthenticated: true,
        });
      },

      logout: () => {
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        });
      },

      refreshAccessToken: async () => {
        const { refreshToken } = get();
        if (!refreshToken) throw new Error('No refresh token');

        const response = await authApi.refresh(refreshToken);
        set({
          accessToken: response.accessToken,
          refreshToken: response.refreshToken,
        });
      },

      updateUser: (userData) => {
        set((state) => ({
          user: state.user ? { ...state.user, ...userData } : null,
        }));
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
```

#### UI Store
```typescript
// src/store/ui.store.ts

import { create } from 'zustand';

interface Notification {
  id: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
}

interface UIState {
  sidebarOpen: boolean;
  theme: 'light' | 'dark';
  language: 'pt-BR' | 'en-US';
  notifications: Notification[];

  // Actions
  toggleSidebar: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
  setLanguage: (lang: 'pt-BR' | 'en-US') => void;
  addNotification: (notification: Omit<Notification, 'id'>) => void;
  removeNotification: (id: string) => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: true,
  theme: 'light',
  language: 'pt-BR',
  notifications: [],

  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),

  setTheme: (theme) => set({ theme }),

  setLanguage: (language) => set({ language }),

  addNotification: (notification) =>
    set((state) => ({
      notifications: [
        ...state.notifications,
        { ...notification, id: crypto.randomUUID() },
      ],
    })),

  removeNotification: (id) =>
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    })),
}));
```

---

## 🔌 API Integration

### Axios Configuration
```typescript
// src/api/axios-config.ts

import axios from 'axios';
import { useAuthStore } from '../store/auth.store';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://api.conciliaai.com';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add auth token
apiClient.interceptors.request.use(
  (config) => {
    const { accessToken } = useAuthStore.getState();
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - Handle 401 and refresh token
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        await useAuthStore.getState().refreshAccessToken();
        const { accessToken } = useAuthStore.getState();
        originalRequest.headers.Authorization = `Bearer ${accessToken}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        useAuthStore.getState().logout();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);
```

### API Client Examples
```typescript
// src/api/reconciliation.api.ts

import { apiClient } from './axios-config';
import type { ReconciliationRequest, ReconciliationResult } from '../types/api.types';

export const reconciliationApi = {
  // Execute reconciliation
  reconcile: async (data: ReconciliationRequest): Promise<ReconciliationResult> => {
    const response = await apiClient.post('/api/reconcile', data);
    return response.data;
  },

  // Get matches
  getMatches: async (params: {
    startDate?: string;
    endDate?: string;
    page?: number;
    pageSize?: number;
  }) => {
    const response = await apiClient.get('/api/matches', { params });
    return response.data;
  },

  // Get match by ID
  getMatchById: async (id: string) => {
    const response = await apiClient.get(`/api/matches/${id}`);
    return response.data;
  },
};

// src/api/divergences.api.ts

import { apiClient } from './axios-config';
import type { Divergence, ResolveDivergenceRequest } from '../types/api.types';

export const divergencesApi = {
  // Get divergences
  getDivergences: async (params: {
    type?: string;
    severity?: string;
    status?: string;
    page?: number;
    pageSize?: number;
  }) => {
    const response = await apiClient.get('/api/divergences', { params });
    return response.data;
  },

  // Get divergence by ID
  getDivergenceById: async (id: string): Promise<Divergence> => {
    const response = await apiClient.get(`/api/divergences/${id}`);
    return response.data;
  },

  // Resolve divergence
  resolveDivergence: async (id: string, data: ResolveDivergenceRequest) => {
    const response = await apiClient.patch(`/api/divergences/${id}/resolve`, data);
    return response.data;
  },
};

// src/api/sales.api.ts

import { apiClient } from './axios-config';
import type { Sale, CreateSaleRequest } from '../types/api.types';

export const salesApi = {
  // Get sales
  getSales: async (params: {
    startDate?: string;
    endDate?: string;
    status?: string;
    page?: number;
    pageSize?: number;
  }) => {
    const response = await apiClient.get('/api/sales', { params });
    return response.data;
  },

  // Get sale by ID
  getSaleById: async (id: string): Promise<Sale> => {
    const response = await apiClient.get(`/api/sales/${id}`);
    return response.data;
  },

  // Create sale
  createSale: async (data: CreateSaleRequest): Promise<Sale> => {
    const response = await apiClient.post('/api/sales', data);
    return response.data;
  },

  // Update sale
  updateSale: async (id: string, data: Partial<Sale>): Promise<Sale> => {
    const response = await apiClient.put(`/api/sales/${id}`, data);
    return response.data;
  },

  // Delete sale
  deleteSale: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/sales/${id}`);
  },

  // Import sales from CSV
  importSales: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post('/api/sales/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
};
```

### React Query Integration
```typescript
// src/hooks/useReconciliation.ts

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { reconciliationApi } from '../api/reconciliation.api';
import { useNotifications } from './useNotifications';
import type { ReconciliationRequest } from '../types/api.types';

export function useReconciliation() {
  const queryClient = useQueryClient();
  const { showSuccess, showError } = useNotifications();

  // Execute reconciliation mutation
  const reconcileMutation = useMutation({
    mutationFn: (data: ReconciliationRequest) => reconciliationApi.reconcile(data),
    onSuccess: (data) => {
      showSuccess(`Reconciliação concluída! ${data.matched_count} matches encontrados.`);

      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ['matches'] });
      queryClient.invalidateQueries({ queryKey: ['divergences'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
    },
    onError: (error) => {
      showError('Erro ao executar reconciliação. Tente novamente.');
      console.error('Reconciliation error:', error);
    },
  });

  return {
    reconcile: reconcileMutation.mutate,
    isReconciling: reconcileMutation.isPending,
    reconciliationResult: reconcileMutation.data,
    reconciliationError: reconcileMutation.error,
  };
}

// src/hooks/useSales.ts

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { salesApi } from '../api/sales.api';
import { useNotifications } from './useNotifications';

export function useSales(params?: {
  startDate?: string;
  endDate?: string;
  status?: string;
  page?: number;
  pageSize?: number;
}) {
  const queryClient = useQueryClient();
  const { showSuccess, showError } = useNotifications();

  // Fetch sales query
  const salesQuery = useQuery({
    queryKey: ['sales', params],
    queryFn: () => salesApi.getSales(params || {}),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Create sale mutation
  const createSaleMutation = useMutation({
    mutationFn: salesApi.createSale,
    onSuccess: () => {
      showSuccess('Venda criada com sucesso!');
      queryClient.invalidateQueries({ queryKey: ['sales'] });
    },
    onError: () => {
      showError('Erro ao criar venda.');
    },
  });

  // Delete sale mutation
  const deleteSaleMutation = useMutation({
    mutationFn: salesApi.deleteSale,
    onSuccess: () => {
      showSuccess('Venda excluída com sucesso!');
      queryClient.invalidateQueries({ queryKey: ['sales'] });
    },
    onError: () => {
      showError('Erro ao excluir venda.');
    },
  });

  // Import sales mutation
  const importSalesMutation = useMutation({
    mutationFn: salesApi.importSales,
    onSuccess: (data) => {
      showSuccess(`${data.imported} vendas importadas com sucesso!`);
      queryClient.invalidateQueries({ queryKey: ['sales'] });
    },
    onError: () => {
      showError('Erro ao importar vendas.');
    },
  });

  return {
    sales: salesQuery.data?.results || [],
    totalSales: salesQuery.data?.total || 0,
    isLoading: salesQuery.isLoading,
    isError: salesQuery.isError,
    error: salesQuery.error,

    createSale: createSaleMutation.mutate,
    deleteSale: deleteSaleMutation.mutate,
    importSales: importSalesMutation.mutate,

    isCreating: createSaleMutation.isPending,
    isDeleting: deleteSaleMutation.isPending,
    isImporting: importSalesMutation.isPending,
  };
}

// src/hooks/useDivergences.ts

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { divergencesApi } from '../api/divergences.api';
import { useNotifications } from './useNotifications';

export function useDivergences(params?: {
  type?: string;
  severity?: string;
  status?: string;
  page?: number;
  pageSize?: number;
}) {
  const queryClient = useQueryClient();
  const { showSuccess, showError } = useNotifications();

  // Fetch divergences query
  const divergencesQuery = useQuery({
    queryKey: ['divergences', params],
    queryFn: () => divergencesApi.getDivergences(params || {}),
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  // Resolve divergence mutation
  const resolveMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      divergencesApi.resolveDivergence(id, data),
    onSuccess: () => {
      showSuccess('Divergência resolvida com sucesso!');
      queryClient.invalidateQueries({ queryKey: ['divergences'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
    },
    onError: () => {
      showError('Erro ao resolver divergência.');
    },
  });

  return {
    divergences: divergencesQuery.data?.results || [],
    totalDivergences: divergencesQuery.data?.total || 0,
    isLoading: divergencesQuery.isLoading,
    isError: divergencesQuery.isError,

    resolveDivergence: resolveMutation.mutate,
    isResolving: resolveMutation.isPending,
  };
}
```

---

## 🔐 Authentication Flow

### Login Page
```tsx
// src/pages/Login/Login.tsx

import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Card,
  CardContent,
  TextField,
  Typography,
  Alert,
} from '@mui/material';
import { useAuthStore } from '../../store/auth.store';

const loginSchema = z.object({
  email: z.string().email('Email inválido'),
  password: z.string().min(8, 'Senha deve ter no mínimo 8 caracteres'),
});

type LoginFormData = z.infer<typeof loginSchema>;

export function LoginPage() {
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);
  const [error, setError] = React.useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    try {
      setError(null);
      await login(data.email, data.password);
      navigate('/dashboard');
    } catch (err) {
      setError('Email ou senha inválidos');
    }
  };

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        bgcolor: 'background.default',
      }}
    >
      <Card sx={{ maxWidth: 400, width: '100%', mx: 2 }}>
        <CardContent sx={{ p: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom textAlign="center">
            ConciliaAI
          </Typography>

          <Typography variant="body2" color="text.secondary" textAlign="center" mb={3}>
            Sistema de Reconciliação Financeira
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit(onSubmit)}>
            <TextField
              {...register('email')}
              label="Email"
              type="email"
              fullWidth
              margin="normal"
              error={!!errors.email}
              helperText={errors.email?.message}
            />

            <TextField
              {...register('password')}
              label="Senha"
              type="password"
              fullWidth
              margin="normal"
              error={!!errors.password}
              helperText={errors.password?.message}
            />

            <Button
              type="submit"
              variant="contained"
              fullWidth
              size="large"
              sx={{ mt: 3 }}
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Entrando...' : 'Entrar'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </Box>
  );
}
```

### Protected Route
```tsx
// src/components/auth/ProtectedRoute.tsx

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/auth.store';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRoles?: string[];
}

export function ProtectedRoute({ children, requiredRoles }: ProtectedRouteProps) {
  const location = useLocation();
  const { isAuthenticated, user } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requiredRoles && user) {
    const hasRequiredRole = requiredRoles.some((role) =>
      user.roles.includes(role)
    );

    if (!hasRequiredRole) {
      return <Navigate to="/unauthorized" replace />;
    }
  }

  return <>{children}</>;
}
```

---

## 🗺️ Routing

### Routes Configuration
```tsx
// src/App.tsx

import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

import { theme } from './theme/theme';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { AppLayout } from './components/layout/AppLayout';

// Pages
import { LoginPage } from './pages/Login/Login';
import { DashboardPage } from './pages/Dashboard/Dashboard';
import { SalesPage } from './pages/Sales/Sales';
import { TransactionsPage } from './pages/Transactions/Transactions';
import { ReconciliationPage } from './pages/Reconciliation/Reconciliation';
import { DivergencesPage } from './pages/Divergences/Divergences';
import { ReportsPage } from './pages/Reports/Reports';
import { SettingsPage } from './pages/Settings/Settings';
import { NotFoundPage } from './pages/NotFound/NotFound';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <BrowserRouter>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<LoginPage />} />

            {/* Protected routes */}
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
              <Route path="transactions" element={<TransactionsPage />} />
              <Route path="reconciliation" element={<ReconciliationPage />} />
              <Route path="divergences" element={<DivergencesPage />} />
              <Route path="reports" element={<ReportsPage />} />
              <Route path="settings" element={<SettingsPage />} />
            </Route>

            {/* 404 */}
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
```

---

## ⚡ Performance

### Code Splitting
```tsx
// Lazy load pages
const DashboardPage = React.lazy(() => import('./pages/Dashboard/Dashboard'));
const SalesPage = React.lazy(() => import('./pages/Sales/Sales'));
const TransactionsPage = React.lazy(() => import('./pages/Transactions/Transactions'));

// Wrap with Suspense
<Route
  path="dashboard"
  element={
    <Suspense fallback={<LoadingSpinner />}>
      <DashboardPage />
    </Suspense>
  }
/>
```

### Virtualization for Large Lists
```tsx
// src/components/features/VirtualizedTable.tsx

import { useVirtualizer } from '@tanstack/react-virtual';

export function VirtualizedTable({ data, columns }: { data: any[]; columns: any[] }) {
  const parentRef = React.useRef<HTMLDivElement>(null);

  const rowVirtualizer = useVirtualizer({
    count: data.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50, // Row height
    overscan: 10,
  });

  return (
    <div ref={parentRef} style={{ height: '600px', overflow: 'auto' }}>
      <div style={{ height: `${rowVirtualizer.getTotalSize()}px`, position: 'relative' }}>
        {rowVirtualizer.getVirtualItems().map((virtualRow) => (
          <div
            key={virtualRow.index}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualRow.size}px`,
              transform: `translateY(${virtualRow.start}px)`,
            }}
          >
            {/* Row content */}
            {data[virtualRow.index].name}
          </div>
        ))}
      </div>
    </div>
  );
}
```

### Memoization
```tsx
// Memoize expensive calculations
const expensiveValue = React.useMemo(
  () => calculateExpensiveValue(data),
  [data]
);

// Memoize callbacks
const handleClick = React.useCallback(
  (id: string) => {
    console.log('Clicked:', id);
  },
  []
);

// Memoize components
const MemoizedComponent = React.memo(ExpensiveComponent);
```

### Performance Budget

| Metric | Target | Tools |
| ------ | ------ | ----- |
| First Contentful Paint (FCP) | < 1.5s | Lighthouse |
| Largest Contentful Paint (LCP) | < 2.5s | Lighthouse |
| Time to Interactive (TTI) | < 3.5s | Lighthouse |
| Total Blocking Time (TBT) | < 300ms | Lighthouse |
| Cumulative Layout Shift (CLS) | < 0.1 | Lighthouse |
| Bundle Size (Initial) | < 200KB (gzipped) | Webpack Bundle Analyzer |

---

## 🚀 Deployment

### Build Configuration
```typescript
// vite.config.ts

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig({
  plugins: [
    react(),
    visualizer({ open: true, gzipSize: true }),
  ],
  build: {
    target: 'es2020',
    minify: 'terser',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'mui-vendor': ['@mui/material', '@mui/icons-material'],
          'query-vendor': ['@tanstack/react-query', '@tanstack/react-table'],
        },
      },
    },
    chunkSizeWarningLimit: 500,
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
```

### Environment Variables
```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=ConciliaAI
VITE_APP_VERSION=1.0.0

# .env.production
VITE_API_BASE_URL=https://api.conciliaai.com
VITE_APP_NAME=ConciliaAI
VITE_APP_VERSION=1.0.0
VITE_SENTRY_DSN=https://xxx@sentry.io/xxx
```

### Docker Configuration
```dockerfile
# Dockerfile

# Stage 1: Build
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install --frozen-lockfile

COPY . .
RUN pnpm build

# Stage 2: Production
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

```nginx
# nginx.conf

server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    # Compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

### CI/CD Pipeline
```yaml
# .github/workflows/frontend-deploy.yml

name: Frontend Deploy

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install pnpm
        run: npm install -g pnpm

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Lint
        run: pnpm lint

      - name: Type check
        run: pnpm type-check

      - name: Unit tests
        run: pnpm test:unit

      - name: Build
        run: pnpm build

      - name: E2E tests
        run: pnpm test:e2e

  deploy-staging:
    needs: test
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Build Docker image
        run: docker build -t conciliaai/frontend:staging .

      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push conciliaai/frontend:staging

      - name: Deploy to staging
        run: |
          kubectl set image deployment/frontend-staging frontend=conciliaai/frontend:staging -n conciliaai-staging

  deploy-production:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Build Docker image
        run: docker build -t conciliaai/frontend:latest .

      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push conciliaai/frontend:latest

      - name: Deploy to production
        run: |
          kubectl set image deployment/frontend-prod frontend=conciliaai/frontend:latest -n conciliaai-prod
```

---

## 📅 Development Plan

### Phase 1: Setup & Foundation (Week 1-2)

**Tasks:**

- Project setup (Vite + React + TypeScript)
- Install dependencies (MUI, React Query, Zustand, etc.)
- Configure ESLint, Prettier, TypeScript
- Setup folder structure
- Create theme (colors, typography, spacing)
- Configure routing
- Setup state management stores
- Configure API client (Axios)
- Setup React Query
- Create base layout components
- Setup i18n
- Create Storybook

**Deliverables:**

- Project scaffolding complete
- Development environment ready
- Base components library

**Effort:** 40 horas

---

### Phase 2: Authentication & Core Layout (Week 3)

**Tasks:**

- Implement Login page
- Implement Auth store (Zustand)
- Implement Protected Route component
- Implement AppBar component
- Implement Sidebar component
- Implement Footer component
- Implement PageLayout component
- Implement user menu
- Implement logout functionality
- Add JWT token refresh logic

**Deliverables:**

- Complete authentication flow
- Responsive app layout
- User session management

**Effort:** 24 horas

---

### Phase 3: Dashboard (Week 4)

**Tasks:**

- Create Dashboard page
- Implement KPI Cards component
- Implement Accuracy Trend Chart (Recharts)
- Implement Recent Reconciliations Timeline
- Implement Top Divergences widget
- Implement Quick Actions panel
- Connect to /api/stats endpoint
- Add real-time updates (polling)
- Add loading states
- Add error handling

**Deliverables:**

- Functional dashboard with metrics
- Charts and visualizations
- Real-time data updates

**Effort:** 32 horas

---

### Phase 4: Sales Management (Week 5)

**Tasks:**

- Create Sales page
- Implement Sales Data Table (TanStack Table)
- Implement Search & Filter toolbar
- Implement Sale Detail Modal
- Implement Create Sale form (React Hook Form + Zod)
- Implement Edit Sale form
- Implement Delete confirmation dialog
- Implement Import Sales from CSV
- Implement Export Sales to CSV/Excel
- Connect to /api/sales endpoints
- Add pagination
- Add sorting
- Add bulk actions

**Deliverables:**

- Complete sales CRUD
- Import/Export functionality
- Advanced table features

**Effort:** 32 horas

---

### Phase 5: Transactions Management (Week 6)

**Tasks:**

- Create Transactions page
- Implement Transactions Data Table
- Implement Acquirer filter (Cielo, Rede, Stone)
- Implement Transaction Detail Modal
- Implement Import from Acquirer button
- Connect to /api/transactions endpoints
- Add pagination & sorting
- Add search functionality
- Implement loading states
- Add error handling

**Deliverables:**

- Transaction viewing interface
- Acquirer filtering
- Import functionality

**Effort:** 24 horas

---

### Phase 6: Reconciliation (Week 7)

**Tasks:**

- Create Reconciliation page
- Implement Date Range Picker
- Implement Acquirer Filter
- Implement Start Reconciliation button
- Implement Progress Indicator (animated)
- Implement Results display
- Implement Matches Table
- Implement Unmatched Sales/Transactions lists
- Implement Export Results button
- Connect to /api/reconcile endpoint
- Add real-time progress updates
- Add success/error notifications

**Deliverables:**

- Functional reconciliation flow
- Progress tracking
- Results visualization

**Effort:** 32 horas

---

### Phase 7: Divergences Management (Week 8-9)

**Tasks:**

- Create Divergences page
- Implement Severity filter (Critical, High, Medium, Low)
- Implement Type filter (6 types)
- Implement Status filter (Open, Resolved, Ignored)
- Implement Divergence Cards/List
- Implement Divergence Detail Panel
- Implement Resolution Form
- Implement Suggested Actions display
- Connect to /api/divergences endpoints
- Implement Resolve Divergence mutation
- Add real-time updates
- Add notifications

**Deliverables:**

- Divergence viewing interface
- Advanced filtering
- Resolution workflow

**Effort:** 40 horas

---

### Phase 8: Reports (Week 10)

**Tasks:**

- Create Reports page
- Implement Report Type Selector
- Implement Accuracy Report (chart + table)
- Implement Divergence Analysis Report
- Implement Acquirer Performance Report
- Implement Settlement Analysis Report
- Implement MDR Variance Report
- Implement Export to PDF/Excel
- Connect to /api/reports endpoints
- Add date range filtering
- Add print functionality

**Deliverables:**

- 5 report types
- Export functionality
- Print support

**Effort:** 32 horas

---

### Phase 9: Settings (Week 11)

**Tasks:**

- Create Settings page
- Implement Profile section
- Implement Tenant Info section
- Implement Acquirers Configuration section
- Implement Notifications Settings
- Implement Appearance Settings (Dark Mode)
- Implement Language Settings
- Implement Users Management (Admin only)
- Connect to /api/settings endpoints
- Add form validation
- Add save/cancel functionality

**Deliverables:**

- Complete settings interface
- User preferences
- Admin features

**Effort:** 24 horas

---

### Phase 10: Testing & Polish (Week 12-13)

**Tasks:**

- Write unit tests (Vitest + Testing Library)
- Write E2E tests (Playwright)
- Test all user flows
- Test responsive design (mobile, tablet, desktop)
- Test accessibility (WCAG 2.1 AA)
- Performance optimization
- Bundle size optimization
- Fix bugs
- Add loading skeletons
- Improve error messages
- Add tooltips and help text
- Refine animations
- Documentation (Storybook)

**Deliverables:**

- 80%+ test coverage
- All user flows tested
- Performance optimized
- Production-ready

**Effort:** 56 horas

---

### Phase 11: Deployment & Monitoring (Week 14)

**Tasks:**

- Setup Docker
- Setup Nginx
- Configure CI/CD (GitHub Actions)
- Deploy to staging
- End-to-end testing on staging
- Setup monitoring (Sentry)
- Setup analytics (Google Analytics / Plausible)
- Configure CDN (CloudFlare)
- Performance monitoring
- Deploy to production
- Create deployment documentation
- Training documentation
- User guide

**Deliverables:**

- Staging environment live
- Production deployment
- Monitoring configured
- Documentation complete

**Effort:** 24 horas

---

## 📊 Summary - Development Plan

### Total Effort Breakdown

| Phase | Tasks | Duration | Effort |
| ----- | ----- | -------- | ------ |
| **Phase 1** | Setup & Foundation | 2 weeks | 40h |
| **Phase 2** | Authentication & Layout | 1 week | 24h |
| **Phase 3** | Dashboard | 1 week | 32h |
| **Phase 4** | Sales Management | 1 week | 32h |
| **Phase 5** | Transactions | 1 week | 24h |
| **Phase 6** | Reconciliation | 1 week | 32h |
| **Phase 7** | Divergences | 2 weeks | 40h |
| **Phase 8** | Reports | 1 week | 32h |
| **Phase 9** | Settings | 1 week | 24h |
| **Phase 10** | Testing & Polish | 2 weeks | 56h |
| **Phase 11** | Deployment | 1 week | 24h |
| **TOTAL** | **14 weeks** | **~3.5 months** | **360 hours** |

### Team Recommendation

**Ideal Team:**

- 1x Frontend Tech Lead (full-time)
- 2x Frontend Developers (full-time)
- 1x UI/UX Designer (part-time)
- 1x QA Engineer (part-time)

**Timeline with Team:**

- With 2 developers: ~8-10 weeks
- With 1 developer: ~14-16 weeks

---

## 🧪 Testing Strategy

### Unit Tests (Vitest + Testing Library)
```typescript
// src/components/common/Button/Button.test.tsx

import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Button } from './Button';

describe('Button', () => {
  it('renders with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('is disabled when loading', () => {
    render(<Button loading>Click me</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('shows loading spinner when loading', () => {
    render(<Button loading>Click me</Button>);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });
});
```

### Integration Tests
```typescript
// src/pages/Sales/Sales.test.tsx

import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { SalesPage } from './Sales';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
  },
});

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>
    {children}
  </QueryClientProvider>
);

describe('SalesPage', () => {
  it('loads and displays sales', async () => {
    render(<SalesPage />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText('NSU-123456')).toBeInTheDocument();
      expect(screen.getByText('R$ 100,00')).toBeInTheDocument();
    });
  });

  it('filters sales by date range', async () => {
    render(<SalesPage />, { wrapper });

    // Interact with date picker
    // Verify filtered results
  });

  it('creates a new sale', async () => {
    render(<SalesPage />, { wrapper });

    // Click "Nova Venda" button
    // Fill form
    // Submit
    // Verify success message
  });
});
```

### E2E Tests (Playwright)
```typescript
// tests/e2e/reconciliation.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Reconciliation Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('http://localhost:3000/login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');
  });

  test('execute reconciliation successfully', async ({ page }) => {
    // Navigate to Reconciliation
    await page.goto('http://localhost:3000/reconciliation');

    // Select date range
    await page.click('input[name="startDate"]');
    await page.click('button[aria-label="Jan 1, 2025"]');
    await page.click('input[name="endDate"]');
    await page.click('button[aria-label="Jan 31, 2025"]');

    // Start reconciliation
    await page.click('button:has-text("Reconciliar")');

    // Wait for progress
    await expect(page.locator('text=Reconciliando...')).toBeVisible();

    // Wait for results
    await expect(page.locator('text=Reconciliação concluída')).toBeVisible({
      timeout: 30000,
    });

    // Verify results table
    await expect(page.locator('table')).toBeVisible();
    await expect(page.locator('text=Matches:')).toBeVisible();
  });

  test('handles reconciliation errors', async ({ page }) => {
    // Mock API error
    await page.route('**/api/reconcile', (route) =>
      route.fulfill({
        status: 500,
        body: JSON.stringify({ error: 'Internal Server Error' }),
      })
    );

    await page.goto('http://localhost:3000/reconciliation');
    await page.click('button:has-text("Reconciliar")');

    // Verify error message
    await expect(page.locator('text=Erro ao executar reconciliação')).toBeVisible();
  });
});

test.describe('Divergence Resolution', () => {
  test('resolve a divergence', async ({ page }) => {
    await page.goto('http://localhost:3000/login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');

    // Navigate to Divergences
    await page.goto('http://localhost:3000/divergences');

    // Click on a divergence card
    await page.click('.divergence-card:first-child');

    // Open resolution form
    await page.click('button:has-text("Resolver")');

    // Fill resolution form
    await page.selectOption('select[name="resolution"]', 'manual_adjustment');
    await page.fill('textarea[name="notes"]', 'Resolved manually');

    // Submit
    await page.click('button:has-text("Confirmar")');

    // Verify success
    await expect(page.locator('text=Divergência resolvida')).toBeVisible();
  });
});
```

### Test Coverage Goals

| Category | Target Coverage |
|----------|----------------|
| Statements | ≥ 80% |
| Branches | ≥ 75% |
| Functions | ≥ 80% |
| Lines | ≥ 80% |

### Test Execution
```bash
# Unit tests
pnpm test:unit

# Unit tests with coverage
pnpm test:unit --coverage

# Integration tests
pnpm test:integration

# E2E tests
pnpm test:e2e

# E2E tests headed (with browser UI)
pnpm test:e2e --headed

# All tests
pnpm test:all
```
