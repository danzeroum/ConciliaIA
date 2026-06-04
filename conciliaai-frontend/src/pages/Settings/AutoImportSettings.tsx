import { useEffect, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  FormControlLabel,
  MenuItem,
  Select,
  Switch,
  TextField,
  Typography,
} from '@mui/material';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';

import { apiClient } from '@/api/axios-config';

interface ScheduleResponse {
  id: string;
  schedule_type: string;
  time_of_day: string;
  days_to_import: number;
  is_active: boolean;
}

const AutoImportSettings = () => {
  const [enabled, setEnabled] = useState(false);
  const [apiToken, setApiToken] = useState('');
  const [scheduleType, setScheduleType] = useState('daily');
  const [timeOfDay, setTimeOfDay] = useState('03:00');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [scheduleId, setScheduleId] = useState<string | null>(null);

  useEffect(() => {
    const loadSchedule = async () => {
      try {
        const response = await apiClient.get<ScheduleResponse[]>('/api/v1/auto-import/schedule');
        if (response.data.length) {
          const schedule = response.data[0];
          setEnabled(true);
          setScheduleType(schedule.schedule_type);
          setTimeOfDay(schedule.time_of_day);
          setScheduleId(schedule.id);
        }
      } catch (error) {
        console.warn('Não foi possível carregar o agendamento atual', error);
      }
    };

    loadSchedule();
  }, []);

  const handleToggle = async (checked: boolean) => {
    setEnabled(checked);
    if (!checked) {
      setMessage('');
    }
  };

  const handleSave = async () => {
    setLoading(true);
    setMessage('');
    try {
      if (!enabled) {
        await apiClient.delete('/api/v1/auto-import/schedule');
        setMessage('Importação automática desativada.');
        setScheduleId(null);
        return;
      }

      const payload = {
        api_token: apiToken,
        schedule_type: scheduleType,
        time_of_day: timeOfDay,
        days_to_import: 1,
        credential_hint: apiToken ? `${apiToken.slice(0, 4)}…` : undefined,
      };

      if (scheduleId) {
        await apiClient.put(`/api/v1/auto-import/schedule/${scheduleId}`, payload);
        setMessage('✅ Importação automática atualizada!');
      } else {
        const response = await apiClient.post<ScheduleResponse>('/api/v1/auto-import/schedule', payload);
        if (response.data) {
          setScheduleId(response.data.id);
          setMessage('✅ Importação automática configurada com sucesso!');
        }
      }
    } catch (error: any) {
      const detail = error.response?.data?.detail || 'Não foi possível salvar as configurações.';
      setMessage(`Erro: ${detail}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 640, mx: 'auto', py: 4 }}>
      <Typography variant="h4" gutterBottom>
        Importação Automática Cielo
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Configure o ConciliaAI para buscar seus arquivos do Cielo automaticamente todos os dias.
      </Typography>

      <Card>
        <CardContent>
          <FormControlLabel
            control={<Switch checked={enabled} onChange={(e) => handleToggle(e.target.checked)} />}
            label={
              <Box>
                <Typography variant="subtitle1">{enabled ? 'Ativado' : 'Desativado'}</Typography>
                <Typography variant="caption" color="text.secondary">
                  {enabled
                    ? 'O sistema importará relatórios automaticamente no horário escolhido.'
                    : 'Ative para importar relatórios automaticamente.'}
                </Typography>
              </Box>
            }
          />

          {enabled && (
            <Box sx={{ mt: 3, display: 'flex', flexDirection: 'column', gap: 3 }}>
              <TextField
                label="Token da API Cielo"
                type="password"
                fullWidth
                value={apiToken}
                onChange={(event) => setApiToken(event.target.value)}
                helperText="Token obtido em Cielo Conciliador → Integrações"
                required
              />

              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  Frequência
                </Typography>
                <Select
                  value={scheduleType}
                  onChange={(event) => setScheduleType(event.target.value)}
                  fullWidth
                >
                  <MenuItem value="daily">Diariamente</MenuItem>
                  <MenuItem value="weekly">Semanalmente (segunda-feira)</MenuItem>
                  <MenuItem value="monthly">Mensalmente (dia 1)</MenuItem>
                </Select>
              </Box>

              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  Horário
                </Typography>
                <TextField
                  type="time"
                  value={timeOfDay}
                  onChange={(event) => setTimeOfDay(event.target.value)}
                  InputProps={{
                    startAdornment: <AccessTimeIcon sx={{ mr: 1, color: 'action.active' }} />,
                  }}
                  helperText="Recomendamos horários de baixa movimentação (ex: 03:00)."
                  fullWidth
                />
              </Box>

              <Alert icon={<CheckCircleIcon />} severity="info">
                O ConciliaAI enviará um alerta apenas se ocorrer algum erro na importação automática.
              </Alert>
            </Box>
          )}

          {message && (
            <Alert severity={message.startsWith('Erro') ? 'error' : 'success'} sx={{ mt: 3 }}>
              {message}
            </Alert>
          )}

          <Button
            variant="contained"
            fullWidth
            sx={{ mt: 3 }}
            onClick={handleSave}
            disabled={loading || (enabled && !apiToken)}
          >
            {loading ? 'Salvando...' : 'Salvar Configurações'}
          </Button>
        </CardContent>
      </Card>
    </Box>
  );
};

export default AutoImportSettings;
