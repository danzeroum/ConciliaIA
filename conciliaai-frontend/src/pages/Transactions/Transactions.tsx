import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  TextField,
  MenuItem,
  Button,
  InputAdornment,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import CloudDownloadIcon from '@mui/icons-material/CloudDownload';
import type { ColumnDef } from '@tanstack/react-table';
import { DataTable } from '@/components/common/DataTable/DataTable';
import { ImportTransactionsModal } from '@/components/features/ImportModal/ImportTransactionsModal';
import { useTransactions } from '@/hooks/useTransactions';
import { formatCurrency, formatDateTime, formatAcquirer } from '@/utils/formatters';
import { ACQUIRERS, DEFAULT_PAGE_SIZE } from '@/utils/constants';
import type { Transaction } from '@/types/api.types';

export function TransactionsPage() {
  const [filters, setFilters] = React.useState({
    startDate: '',
    endDate: '',
    acquirer: '',
    search: '',
    page: 1,
    pageSize: DEFAULT_PAGE_SIZE,
  });
  const [searchInput, setSearchInput] = React.useState('');
  const [importModalOpen, setImportModalOpen] = React.useState(false);

  React.useEffect(() => {
    const handler = window.setTimeout(() => {
      setFilters((prev) => ({ ...prev, search: searchInput, page: 1 }));
    }, 300);

    return () => window.clearTimeout(handler);
  }, [searchInput]);

  const { transactions, totalTransactions, currentPage, pageSize, isLoading } = useTransactions(filters);

  const handleFilterChange = (key: 'startDate' | 'endDate' | 'acquirer', value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value, page: 1 }));
  };

  const handlePageChange = (page: number) => {
    setFilters((prev) => ({ ...prev, page }));
  };

  const handlePageSizeChange = (size: number) => {
    setFilters((prev) => ({ ...prev, pageSize: size, page: 1 }));
  };

  const columns = React.useMemo<ColumnDef<Transaction>[]>(
    () => [
      {
        accessorKey: 'nsu',
        header: 'NSU',
        cell: (info) => info.getValue<string>(),
      },
      {
        accessorKey: 'transaction_date',
        header: 'Data da Transação',
        cell: (info) => formatDateTime(info.getValue<string>()),
      },
      {
        accessorKey: 'acquirer',
        header: 'Adquirente',
        cell: (info) => formatAcquirer(info.getValue<string>()),
      },
      {
        accessorKey: 'amount',
        header: 'Valor Bruto',
        cell: (info) => formatCurrency(info.getValue<string>()),
      },
      {
        accessorKey: 'net_amount',
        header: 'Valor Líquido',
        cell: (info) => formatCurrency(info.getValue<string>()),
      },
      {
        accessorKey: 'card_brand',
        header: 'Bandeira',
        cell: (info) => info.getValue<string>(),
      },
      {
        accessorKey: 'card_last_4',
        header: 'Final Cartão',
        cell: (info) => `•••• ${info.getValue<string>()}`,
      },
      {
        accessorKey: 'status',
        header: 'Status',
        cell: (info) => info.getValue<string>(),
      },
    ],
    []
  );

  return (
    <Box display="flex" flexDirection="column" gap={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h4">Transações</Typography>
        <Button
          variant="contained"
          startIcon={<CloudDownloadIcon />}
          onClick={() => setImportModalOpen(true)}
        >
          Importar da Adquirente
        </Button>
      </Box>

      <Paper sx={{ p: 2 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              label="Data inicial"
              type="date"
              InputLabelProps={{ shrink: true }}
              value={filters.startDate}
              onChange={(event) => handleFilterChange('startDate', event.target.value)}
              size="small"
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              label="Data final"
              type="date"
              InputLabelProps={{ shrink: true }}
              value={filters.endDate}
              onChange={(event) => handleFilterChange('endDate', event.target.value)}
              size="small"
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              select
              label="Adquirente"
              value={filters.acquirer}
              onChange={(event) => handleFilterChange('acquirer', event.target.value)}
              size="small"
            >
              <MenuItem value="">Todos</MenuItem>
              {ACQUIRERS.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              placeholder="Buscar por NSU, bandeira..."
              value={searchInput}
              onChange={(event) => setSearchInput(event.target.value)}
              size="small"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon fontSize="small" />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
        </Grid>
      </Paper>

      <DataTable<Transaction>
        data={transactions}
        columns={columns}
        loading={isLoading}
        pagination
        totalRows={totalTransactions}
        currentPage={currentPage}
        pageSize={pageSize}
        onPageChange={handlePageChange}
        onPageSizeChange={handlePageSizeChange}
        searchable={false}
      />

      <ImportTransactionsModal open={importModalOpen} onClose={() => setImportModalOpen(false)} />
    </Box>
  );
}
