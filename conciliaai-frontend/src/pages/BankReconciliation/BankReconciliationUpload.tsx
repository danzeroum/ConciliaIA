import { useRef, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  LinearProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Typography,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import { useNavigate } from 'react-router-dom';

import { apiClient } from '@/api/axios-config';

interface ReconciliationResult {
  summary_message: string;
  total_transactions: number;
  matched_count: number;
  unmatched_count: number;
  total_matched_amount: number;
  matches: Array<{
    bank_transaction_id: string;
    acquirer_transaction_id: string;
    amount: number;
    confidence: number;
    description: string;
  }>;
}

export function BankReconciliationUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<ReconciliationResult | null>(null);
  const [error, setError] = useState('');
  const inputRef = useRef<HTMLInputElement | null>(null);
  const navigate = useNavigate();

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (!selectedFile) {
      return;
    }

    if (!selectedFile.name.toLowerCase().endsWith('.ofx')) {
      setError('Apenas arquivos OFX são aceitos');
      event.target.value = '';
      setFile(null);
      return;
    }

    setFile(selectedFile);
    setResult(null);
    setError('');
  };

  const handleUpload = async () => {
    if (!file) {
      return;
    }

    setUploading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await apiClient.post<ReconciliationResult>(
        '/bank-reconciliation/upload-ofx',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      setResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao processar o arquivo OFX.');
    } finally {
      setUploading(false);
    }
  };

  const resetForm = () => {
    setResult(null);
    setFile(null);
    setError('');
    if (inputRef.current) {
      inputRef.current.value = '';
    }
  };

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 2,
    }).format(value);

  return (
    <Box sx={{ maxWidth: 840, mx: 'auto', py: 4 }}>
      <Typography variant="h4" gutterBottom>
        Conciliação Bancária
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Faça upload do extrato bancário (OFX) para confirmar automaticamente os pagamentos
        recebidos.
      </Typography>

      {!result && (
        <Card>
          <CardContent>
            <Box
              sx={{
                border: '2px dashed',
                borderColor: file ? 'primary.main' : 'grey.300',
                borderRadius: 2,
                p: 4,
                textAlign: 'center',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                '&:hover': {
                  borderColor: 'primary.main',
                  bgcolor: 'action.hover',
                },
              }}
              onClick={() => inputRef.current?.click()}
            >
              <input
                ref={inputRef}
                id="ofx-upload-input"
                type="file"
                accept=".ofx"
                hidden
                onChange={handleFileChange}
              />

              <CloudUploadIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />

              <Typography variant="h6" gutterBottom>
                {file ? file.name : 'Clique ou arraste o arquivo OFX aqui'}
              </Typography>

              <Typography variant="body2" color="text.secondary">
                Formatos aceitos: .ofx (extrato bancário)
              </Typography>
            </Box>

            {uploading && (
              <Box sx={{ mt: 3 }}>
                <LinearProgress />
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1, textAlign: 'center' }}>
                  Processando e conciliando transações...
                </Typography>
              </Box>
            )}

            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error}
              </Alert>
            )}

            <Button
              fullWidth
              variant="contained"
              size="large"
              onClick={handleUpload}
              disabled={!file || uploading}
              sx={{ mt: 3 }}
            >
              {uploading ? 'Processando...' : 'Iniciar Conciliação'}
            </Button>

            <Box sx={{ mt: 3, p: 2, bgcolor: 'info.lighter', borderRadius: 1 }}>
              <Typography variant="body2" color="text.secondary">
                💡 <strong>Como obter o arquivo OFX:</strong>
                <br />1. Acesse seu internet banking
                <br />2. Vá em Extratos → Exportar
                <br />3. Escolha formato OFX (Money)
                <br />4. Faça download e envie aqui
              </Typography>
            </Box>
          </CardContent>
        </Card>
      )}

      {result && (
        <Card>
          <CardContent>
            <Box sx={{ textAlign: 'center', py: 4 }}>
              {result.unmatched_count === 0 ? (
                <CheckCircleIcon sx={{ fontSize: 64, color: 'success.main', mb: 2 }} />
              ) : (
                <WarningIcon sx={{ fontSize: 64, color: 'warning.main', mb: 2 }} />
              )}

              <Typography variant="h5" gutterBottom>
                {result.summary_message}
              </Typography>

              <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center', gap: 6 }}>
                <Box>
                  <Typography variant="h3" color="success.main">
                    {result.matched_count}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    pagamentos confirmados
                  </Typography>
                </Box>

                {result.unmatched_count > 0 && (
                  <Box>
                    <Typography variant="h3" color="warning.main">
                      {result.unmatched_count}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      precisam revisão
                    </Typography>
                  </Box>
                )}
              </Box>

              <Box sx={{ mt: 3, p: 3, bgcolor: 'success.lighter', borderRadius: 2 }}>
                <Typography variant="body1" fontWeight="medium">
                  Total confirmado: {formatCurrency(result.total_matched_amount)}
                </Typography>
              </Box>

              <Box sx={{ mt: 4, display: 'flex', gap: 2 }}>
                <Button variant="contained" fullWidth onClick={() => navigate('/reconciliation')}>
                  Ver transações conciliadas
                </Button>
                <Button variant="outlined" fullWidth onClick={resetForm}>
                  Nova conciliação
                </Button>
              </Box>
            </Box>
          </CardContent>
        </Card>
      )}

      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" gutterBottom>
          Dúvidas frequentes
        </Typography>
        <List dense>
          <ListItem>
            <ListItemIcon>
              <CheckCircleIcon color="primary" />
            </ListItemIcon>
            <ListItemText
              primary="Meu banco não oferece OFX. E agora?"
              secondary="Entre em contato conosco para adicionar suporte ao formato do seu banco."
            />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <CheckCircleIcon color="primary" />
            </ListItemIcon>
            <ListItemText
              primary="É seguro enviar meu extrato?"
              secondary="Sim! O arquivo é processado e descartado imediatamente. Apenas os matches são salvos."
            />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <CheckCircleIcon color="primary" />
            </ListItemIcon>
            <ListItemText
              primary="E se houver transações não conciliadas?"
              secondary="Você pode revisar manualmente na tela de conciliação e fazer o match correto."
            />
          </ListItem>
        </List>
      </Box>
    </Box>
  );
}

export default BankReconciliationUpload;
