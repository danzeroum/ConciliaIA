import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  TextField,
  InputAdornment,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import SearchIcon from '@mui/icons-material/Search';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import FileUploadIcon from '@mui/icons-material/FileUpload';

export function SalesPage() {
  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Vendas</Typography>

        <Box display="flex" gap={1}>
          <Button variant="outlined" startIcon={<FileUploadIcon />}>
            Importar
          </Button>
          <Button variant="outlined" startIcon={<FileDownloadIcon />}>
            Exportar
          </Button>
          <Button variant="contained" startIcon={<AddIcon />}>
            Nova Venda
          </Button>
        </Box>
      </Box>

      <Paper sx={{ p: 2, mb: 2 }}>
        <TextField
          fullWidth
          placeholder="Buscar por NSU, valor, data..."
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
      </Paper>

      <Paper sx={{ p: 3 }}>
        <Box
          sx={{
            height: 400,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'text.secondary',
          }}
        >
          <Typography>Tabela de Vendas será implementada aqui</Typography>
        </Box>
      </Paper>
    </Box>
  );
}
