import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  ListSubheader,
  Toolbar,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import ReceiptIcon from '@mui/icons-material/Receipt';
import CompareArrowsIcon from '@mui/icons-material/CompareArrows';
import WarningIcon from '@mui/icons-material/Warning';
import AssessmentIcon from '@mui/icons-material/Assessment';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import SettingsIcon from '@mui/icons-material/Settings';
import CloudDownloadIcon from '@mui/icons-material/CloudDownload';
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import { useNavigate, useLocation } from 'react-router-dom';
import { useUIStore } from '@/store/ui.store';

const DRAWER_WIDTH = 260;

interface MenuItem {
  text: string;
  icon: React.ReactElement;
  path: string;
}

interface MenuGroup {
  subheader: string;
  items: MenuItem[];
}

// Grouped navigation: related destinations are clustered under a section label
// so the sidebar scans quickly as the number of pages grows. "Fluxo de Caixa"
// now has its own wallet icon (it previously reused the Reports icon).
const menuGroups: MenuGroup[] = [
  {
    subheader: 'Visão Geral',
    items: [{ text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' }],
  },
  {
    subheader: 'Conciliação',
    items: [
      { text: 'Vendas', icon: <ShoppingCartIcon />, path: '/sales' },
      { text: 'Transações', icon: <ReceiptIcon />, path: '/transactions' },
      { text: 'Reconciliação', icon: <CompareArrowsIcon />, path: '/reconciliation' },
      { text: 'Pagamentos Bancários', icon: <AccountBalanceIcon />, path: '/bank-reconciliation' },
      { text: 'Divergências', icon: <WarningIcon />, path: '/divergences' },
    ],
  },
  {
    subheader: 'Análises',
    items: [
      { text: 'Relatórios', icon: <AssessmentIcon />, path: '/reports' },
      { text: 'Fluxo de Caixa', icon: <AccountBalanceWalletIcon />, path: '/reports/cashflow' },
    ],
  },
  {
    subheader: 'Configuração',
    items: [
      { text: 'Alertas', icon: <NotificationsActiveIcon />, path: '/alerts' },
      { text: 'Configurações', icon: <SettingsIcon />, path: '/settings' },
      { text: 'Importação Cielo', icon: <CloudDownloadIcon />, path: '/settings/auto-import' },
    ],
  },
];

export function Sidebar() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const location = useLocation();

  const { sidebarOpen, setSidebarOpen } = useUIStore();

  const handleItemClick = (path: string) => {
    navigate(path);
    if (isMobile) {
      setSidebarOpen(false);
    }
  };

  const drawer = (
    <>
      <Toolbar />
      <List component="nav" aria-label="Navegação principal">
        {menuGroups.map((group) => (
          <li key={group.subheader}>
            <ul style={{ padding: 0, listStyle: 'none' }}>
              <ListSubheader disableSticky>{group.subheader}</ListSubheader>
              {group.items.map((item) => (
                <ListItem key={item.path} disablePadding>
                  <ListItemButton
                    selected={location.pathname === item.path}
                    onClick={() => handleItemClick(item.path)}
                    aria-label={item.text}
                    aria-current={location.pathname === item.path ? 'page' : undefined}
                  >
                    <ListItemIcon>{item.icon}</ListItemIcon>
                    <ListItemText primary={item.text} />
                  </ListItemButton>
                </ListItem>
              ))}
            </ul>
          </li>
        ))}
      </List>
    </>
  );

  return (
    <Drawer
      variant={isMobile ? 'temporary' : 'persistent'}
      open={sidebarOpen}
      onClose={() => setSidebarOpen(false)}
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: DRAWER_WIDTH,
          boxSizing: 'border-box',
        },
      }}
    >
      {drawer}
    </Drawer>
  );
}
