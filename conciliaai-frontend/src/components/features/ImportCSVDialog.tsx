import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Alert,
  LinearProgress,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

interface ImportCSVDialogProps {
  open: boolean;
  onClose: () => void;
  onImport: (file: File) => Promise<any>;
  title: string;
  acceptedFormats?: string;
  helperText?: React.ReactNode;
}

export function ImportCSVDialog({
  open,
  onClose,
  onImport,
  title,
  acceptedFormats = '.csv',
  helperText,
}: ImportCSVDialogProps) {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      if (!selectedFile.name.endsWith('.csv')) {
        setError('Por favor, selecione um arquivo CSV válido');
        setFile(null);
      } else {
        setError(null);
        setFile(selectedFile);
      }
    }
  };

  const handleImport = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);

    try {
      await onImport(file);
      handleClose();
    } catch (err: any) {
      setError(err.message || 'Erro ao importar arquivo');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setFile(null);
    setError(null);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>{title}</DialogTitle>
      <DialogContent>
        <Box sx={{ mt: 2 }}>
          <Button
            variant="outlined"
            component="label"
            fullWidth
            startIcon={<CloudUploadIcon />}
            sx={{ mb: 2 }}
          >
            Selecionar Arquivo CSV
            <input
              type="file"
              hidden
              accept={acceptedFormats}
              onChange={handleFileChange}
            />
          </Button>

          {file && (
            <Alert severity="info" sx={{ mb: 2 }}>
              Arquivo selecionado: <strong>{file.name}</strong>
            </Alert>
          )}

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {loading && <LinearProgress sx={{ mb: 2 }} />}

          {helperText ? (
            helperText
          ) : (
            <>
              <Typography variant="body2" color="text.secondary">
                <strong>Formato esperado:</strong> Arquivo CSV com as seguintes colunas:
              </Typography>
              <Typography variant="caption" color="text.secondary" component="pre">
                nsu, amount, sale_date, payment_method, installments, card_brand
              </Typography>
            </>
          )}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={loading}>
          Cancelar
        </Button>
        <Button
          onClick={handleImport}
          variant="contained"
          disabled={!file || loading}
        >
          Importar
        </Button>
      </DialogActions>
    </Dialog>
  );
}
