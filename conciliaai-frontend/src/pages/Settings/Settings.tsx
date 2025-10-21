import React, { useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  FormControlLabel,
  Grid,
  IconButton,
  List,
  ListItem,
  ListItemSecondaryAction,
  ListItemText,
  MenuItem,
  Paper,
  Switch,
  Tab,
  Tabs,
  TextField,
  Typography,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import { useForm, Controller } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useUIStore } from '@/store/ui.store';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel({ children, value, index, ...other }: TabPanelProps) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`settings-tabpanel-${index}`}
      aria-labelledby={`settings-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const profileSchema = z.object({
  companyName: z.string().min(1, 'Nome da empresa é obrigatório'),
  email: z.string().email('Email inválido'),
  phone: z.string().optional(),
  address: z.string().optional(),
  city: z.string().optional(),
  state: z.string().optional(),
  zipCode: z.string().optional(),
});

const notificationSchema = z.object({
  email: z.boolean(),
  push: z.boolean(),
  divergences: z.boolean(),
  dailyReports: z.boolean(),
  weeklyReports: z.boolean(),
  reconciliationAlerts: z.boolean(),
});

const mockUsers = [
  { id: 1, name: 'João Silva', email: 'joao@empresa.com', role: 'Administrador', status: 'Ativo' },
  { id: 2, name: 'Maria Santos', email: 'maria@empresa.com', role: 'Usuário', status: 'Ativo' },
  { id: 3, name: 'Pedro Costa', email: 'pedro@empresa.com', role: 'Usuário', status: 'Inativo' },
];

type ProfileFormData = z.infer<typeof profileSchema>;
type NotificationFormData = z.infer<typeof notificationSchema>;

export function SettingsPage() {
  const [tabValue, setTabValue] = useState(0);
  const [userDialogOpen, setUserDialogOpen] = useState(false);
  const themeMode = useUIStore((state) => state.theme);
  const setTheme = useUIStore((state) => state.setTheme);
  const language = useUIStore((state) => state.language);
  const setLanguage = useUIStore((state) => state.setLanguage);
  const [darkMode, setDarkMode] = useState(themeMode === 'dark');

  const profileForm = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      companyName: 'Minha Empresa LTDA',
      email: 'contato@minhaempresa.com',
      phone: '(11) 99999-9999',
      address: 'Rua Exemplo, 123',
      city: 'São Paulo',
      state: 'SP',
      zipCode: '01234-567',
    },
  });

  const notificationForm = useForm<NotificationFormData>({
    resolver: zodResolver(notificationSchema),
    defaultValues: {
      email: true,
      push: true,
      divergences: true,
      dailyReports: false,
      weeklyReports: true,
      reconciliationAlerts: true,
    },
  });

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleProfileSubmit = (data: ProfileFormData) => {
    console.info('Profile data:', data);
  };

  const handleNotificationSubmit = (data: NotificationFormData) => {
    console.info('Notification settings:', data);
  };

  const handleAddUser = () => {
    setUserDialogOpen(true);
  };

  const handleDeleteUser = (userId: number) => {
    if (window.confirm('Tem certeza que deseja remover este usuário?')) {
      console.info('Delete user:', userId);
    }
  };

  const toggleDarkMode = () => {
    setDarkMode((prev) => {
      const next = !prev;
      setTheme(next ? 'dark' : 'light');
      return next;
    });
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Configurações
      </Typography>

      <Paper>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="settings tabs">
          <Tab label="Perfil da Empresa" />
          <Tab label="Notificações" />
          <Tab label="Usuários" />
          <Tab label="Preferências" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <form onSubmit={profileForm.handleSubmit(handleProfileSubmit)}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Informações da Empresa
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={12} sm={6}>
                        <Controller
                          name="companyName"
                          control={profileForm.control}
                          render={({ field }) => (
                            <TextField
                              {...field}
                              label="Nome da Empresa"
                              fullWidth
                              error={!!profileForm.formState.errors.companyName}
                              helperText={profileForm.formState.errors.companyName?.message}
                            />
                          )}
                        />
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <Controller
                          name="email"
                          control={profileForm.control}
                          render={({ field }) => (
                            <TextField
                              {...field}
                              label="Email"
                              type="email"
                              fullWidth
                              error={!!profileForm.formState.errors.email}
                              helperText={profileForm.formState.errors.email?.message}
                            />
                          )}
                        />
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <Controller
                          name="phone"
                          control={profileForm.control}
                          render={({ field }) => <TextField {...field} label="Telefone" fullWidth />}
                        />
                      </Grid>
                      <Grid item xs={12}>
                        <Controller
                          name="address"
                          control={profileForm.control}
                          render={({ field }) => <TextField {...field} label="Endereço" fullWidth />}
                        />
                      </Grid>
                      <Grid item xs={12} sm={4}>
                        <Controller
                          name="city"
                          control={profileForm.control}
                          render={({ field }) => <TextField {...field} label="Cidade" fullWidth />}
                        />
                      </Grid>
                      <Grid item xs={12} sm={4}>
                        <Controller
                          name="state"
                          control={profileForm.control}
                          render={({ field }) => <TextField {...field} label="Estado" fullWidth />}
                        />
                      </Grid>
                      <Grid item xs={12} sm={4}>
                        <Controller
                          name="zipCode"
                          control={profileForm.control}
                          render={({ field }) => <TextField {...field} label="CEP" fullWidth />}
                        />
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12}>
                <Box display="flex" justifyContent="flex-end" gap={2}>
                  <Button type="submit" variant="contained">
                    Salvar Alterações
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </form>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <form onSubmit={notificationForm.handleSubmit(handleNotificationSubmit)}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Configurações de Notificação
                    </Typography>

                    <Typography variant="subtitle1" color="text.secondary" gutterBottom sx={{ mt: 2 }}>
                      Canal de Notificação
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={12} sm={6}>
                        <Controller
                          name="email"
                          control={notificationForm.control}
                          render={({ field }) => (
                            <FormControlLabel
                              control={<Switch checked={field.value} onChange={field.onChange} />}
                              label="Notificações por Email"
                            />
                          )}
                        />
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <Controller
                          name="push"
                          control={notificationForm.control}
                          render={({ field }) => (
                            <FormControlLabel
                              control={<Switch checked={field.value} onChange={field.onChange} />}
                              label="Notificações Push"
                            />
                          )}
                        />
                      </Grid>
                    </Grid>

                    <Divider sx={{ my: 3 }} />

                    <Typography variant="subtitle1" color="text.secondary" gutterBottom>
                      Tipos de Notificação
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={12}>
                        <Controller
                          name="divergences"
                          control={notificationForm.control}
                          render={({ field }) => (
                            <FormControlLabel
                              control={<Switch checked={field.value} onChange={field.onChange} />}
                              label="Alertas de Divergências"
                            />
                          )}
                        />
                      </Grid>
                      <Grid item xs={12}>
                        <Controller
                          name="reconciliationAlerts"
                          control={notificationForm.control}
                          render={({ field }) => (
                            <FormControlLabel
                              control={<Switch checked={field.value} onChange={field.onChange} />}
                              label="Alertas de Reconciliação"
                            />
                          )}
                        />
                      </Grid>
                      <Grid item xs={12}>
                        <Controller
                          name="dailyReports"
                          control={notificationForm.control}
                          render={({ field }) => (
                            <FormControlLabel
                              control={<Switch checked={field.value} onChange={field.onChange} />}
                              label="Relatórios Diários"
                            />
                          )}
                        />
                      </Grid>
                      <Grid item xs={12}>
                        <Controller
                          name="weeklyReports"
                          control={notificationForm.control}
                          render={({ field }) => (
                            <FormControlLabel
                              control={<Switch checked={field.value} onChange={field.onChange} />}
                              label="Relatórios Semanais"
                            />
                          )}
                        />
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12}>
                <Box display="flex" justifyContent="flex-end" gap={2}>
                  <Button type="submit" variant="contained">
                    Salvar Configurações
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </form>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">Gerenciamento de Usuários</Typography>
                <Button variant="contained" startIcon={<AddIcon />} onClick={handleAddUser}>
                  Adicionar Usuário
                </Button>
              </Box>

              <Card>
                <CardContent sx={{ p: 0 }}>
                  <List>
                    {mockUsers.map((user) => (
                      <ListItem key={user.id} divider>
                        <ListItemText
                          primary={user.name}
                          secondary={
                            <Box>
                              <Typography variant="body2" color="text.secondary">
                                {user.email}
                              </Typography>
                              <Box display="flex" gap={1} mt={0.5}>
                                <Chip label={user.role} size="small" variant="outlined" />
                                <Chip
                                  label={user.status}
                                  size="small"
                                  color={user.status === 'Ativo' ? 'success' : 'default'}
                                />
                              </Box>
                            </Box>
                          }
                        />
                        <ListItemSecondaryAction>
                          <IconButton edge="end" aria-label="edit" sx={{ mr: 1 }}>
                            <EditIcon />
                          </IconButton>
                          <IconButton
                            edge="end"
                            aria-label="delete"
                            onClick={() => handleDeleteUser(user.id)}
                            disabled={user.role === 'Administrador'}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </ListItemSecondaryAction>
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Preferências do Sistema
                  </Typography>

                  <Grid container spacing={3}>
                    <Grid item xs={12} sm={6}>
                      <FormControlLabel
                        control={<Switch checked={darkMode} onChange={toggleDarkMode} />}
                        label="Modo Escuro"
                      />
                      <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                        Alternar entre tema claro e escuro
                      </Typography>
                    </Grid>

                    <Grid item xs={12} sm={6}>
                      <TextField
                        select
                        label="Idioma"
                        value={language}
                        onChange={(event) => setLanguage(event.target.value as 'pt-BR' | 'en-US')}
                        fullWidth
                      >
                        <MenuItem value="pt-BR">Português (Brasil)</MenuItem>
                        <MenuItem value="en-US">English (US)</MenuItem>
                        <MenuItem value="es-ES">Español</MenuItem>
                      </TextField>
                    </Grid>

                    <Grid item xs={12} sm={6}>
                      <TextField select label="Fuso Horário" defaultValue="America/Sao_Paulo" fullWidth>
                        <MenuItem value="America/Sao_Paulo">America/Sao_Paulo (Brasília)</MenuItem>
                        <MenuItem value="UTC">UTC</MenuItem>
                      </TextField>
                    </Grid>

                    <Grid item xs={12} sm={6}>
                      <TextField select label="Formato de Data" defaultValue="dd/MM/yyyy" fullWidth>
                        <MenuItem value="dd/MM/yyyy">DD/MM/AAAA</MenuItem>
                        <MenuItem value="MM/dd/yyyy">MM/DD/AAAA</MenuItem>
                        <MenuItem value="yyyy-MM-dd">AAAA-MM-DD</MenuItem>
                      </TextField>
                    </Grid>

                    <Grid item xs={12} sm={6}>
                      <TextField select label="Moeda" defaultValue="BRL" fullWidth>
                        <MenuItem value="BRL">Real (R$)</MenuItem>
                        <MenuItem value="USD">Dólar (US$)</MenuItem>
                        <MenuItem value="EUR">Euro (€)</MenuItem>
                      </TextField>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom color="error">
                    Zona de Perigo
                  </Typography>
                  <Alert severity="warning" sx={{ mb: 2 }}>
                    Estas ações são irreversíveis. Proceda com cautela.
                  </Alert>
                  <Box display="flex" gap={2}>
                    <Button variant="outlined" color="error">
                      Exportar Todos os Dados
                    </Button>
                    <Button variant="outlined" color="error">
                      Limpar Dados de Teste
                    </Button>
                    <Button variant="contained" color="error">
                      Excluir Conta
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>
      </Paper>

      <Dialog open={userDialogOpen} onClose={() => setUserDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Adicionar Novo Usuário</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField label="Nome Completo" fullWidth />
            </Grid>
            <Grid item xs={12}>
              <TextField label="Email" type="email" fullWidth />
            </Grid>
            <Grid item xs={12}>
              <TextField select label="Função" fullWidth defaultValue="user">
                <MenuItem value="admin">Administrador</MenuItem>
                <MenuItem value="user">Usuário</MenuItem>
                <MenuItem value="viewer">Visualizador</MenuItem>
              </TextField>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUserDialogOpen(false)}>Cancelar</Button>
          <Button variant="contained" onClick={() => setUserDialogOpen(false)}>
            Adicionar Usuário
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
