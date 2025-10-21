import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  TextField,
  Button,
} from '@mui/material';
import { useUIStore } from '@/store/ui.store';

export function SettingsPage() {
  const theme = useUIStore((state) => state.theme);
  const setTheme = useUIStore((state) => state.setTheme);
  const language = useUIStore((state) => state.language);
  const setLanguage = useUIStore((state) => state.setLanguage);
  const [webhookUrl, setWebhookUrl] = React.useState('');
  const [dailyDigest, setDailyDigest] = React.useState(true);

  const handleThemeToggle = (_: unknown, checked: boolean) => {
    setTheme(checked ? 'dark' : 'light');
  };

  const handleSaveIntegrations = () => {
    // Future: persist webhook/digest settings via API
    console.info('Saving integrations', { webhookUrl, dailyDigest });
  };

  return (
    <Box display="flex" flexDirection="column" gap={3}>
      <Typography variant="h4">Configurações</Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Preferências de interface
            </Typography>
            <FormControlLabel
              control={<Switch checked={theme === 'dark'} onChange={handleThemeToggle} />}
              label="Modo escuro"
            />

            <FormControl fullWidth sx={{ mt: 2 }}>
              <InputLabel id="language-select">Idioma</InputLabel>
              <Select
                labelId="language-select"
                label="Idioma"
                value={language}
                onChange={(event) => setLanguage(event.target.value as 'pt-BR' | 'en-US')}
              >
                <MenuItem value="pt-BR">Português (Brasil)</MenuItem>
                <MenuItem value="en-US">Inglês</MenuItem>
              </Select>
            </FormControl>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Integrações e alertas
            </Typography>
            <TextField
              label="URL do webhook para notificações"
              fullWidth
              value={webhookUrl}
              onChange={(event) => setWebhookUrl(event.target.value)}
              placeholder="https://exemplo.com/webhook"
              sx={{ mb: 2 }}
            />

            <FormControlLabel
              control={<Switch checked={dailyDigest} onChange={(_, checked) => setDailyDigest(checked)} />}
              label="Receber resumo diário por e-mail"
            />

            <Button variant="contained" sx={{ mt: 2 }} onClick={handleSaveIntegrations}>
              Salvar integrações
            </Button>
          </Paper>
        </Grid>
      </Grid>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Auditoria
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Consulte o time de suporte para habilitar logs avançados e auditorias de reconciliação em
          tempo real. Esses recursos ajudam a rastrear alterações críticas e a garantir conformidade
          regulatória.
        </Typography>
      </Paper>
    </Box>
  );
}
