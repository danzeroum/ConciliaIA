import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import { useSales } from '@/hooks/useSales';
import { validateCSVFile } from '@/utils/validators';

interface ImportSalesModalProps {
  open: boolean;
  onClose: () => void;
}

export function ImportSalesModal({ open, onClose }: ImportSalesModalProps) {
  const inputRef = React.useRef<HTMLInputElement | null>(null);
  const [selectedFile, setSelectedFile] = React.useState<File | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const { importSales, isImporting } = useSales();

  const handleSelectFile = () => {
    inputRef.current?.click();
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    const validation = validateCSVFile(file);
    if (!validation.valid) {
      setError(validation.error ?? 'Arquivo inválido');
      setSelectedFile(null);
      return;
    }

    setError(null);
    setSelectedFile(file);
  };

  const handleImport = () => {
    if (!selectedFile) {
      setError('Selecione um arquivo CSV para importar');
      return;
    }

    importSales(selectedFile, {
      onSuccess: () => {
        setSelectedFile(null);
        onClose();
      },
    });
  };

  const handleClose = () => {
    setSelectedFile(null);
    setError(null);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} fullWidth maxWidth="sm">
      <DialogTitle>Importar Vendas</DialogTitle>
      <DialogContent dividers>
        <input
          ref={inputRef}
          type="file"
          accept=".csv"
          style={{ display: 'none' }}
          onChange={handleFileChange}
        />
        <Box display="flex" flexDirection="column" gap={2}>
          <Typography color="text.secondary">
            Faça upload de um arquivo CSV contendo as vendas.
          </Typography>
          <Button
            variant="outlined"
            startIcon={<UploadFileIcon />}
            onClick={handleSelectFile}
            disabled={isImporting}
          >
            Selecionar arquivo
          </Button>
          {selectedFile && (
            <Typography variant="body2">Arquivo selecionado: {selectedFile.name}</Typography>
          )}
          {error && (
            <Typography variant="body2" color="error">
              {error}
            </Typography>
          )}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} color="inherit" disabled={isImporting}>
          Cancelar
        </Button>
        <Button onClick={handleImport} variant="contained" disabled={isImporting}>
          {isImporting ? 'Importando...' : 'Importar'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
