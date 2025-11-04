import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  TextField,
  Grid,
  MenuItem,
  Chip,
  IconButton,
  Tooltip,
  Stack,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import VisibilityIcon from '@mui/icons-material/Visibility';
import DeleteIcon from '@mui/icons-material/Delete';
import type { ColumnDef } from '@tanstack/react-table';
import { DataTable } from '@/components/common/DataTable/DataTable';
import {
  useTransactions,
  useDeleteTransaction,
  useImportTransactions,
  useExportTransactions,
} from '@/hooks/useTransactions';
import { ImportCSVDialog } from '@/components/features/ImportCSVDialog';
import { TransactionDetail } from '@/components/features/TransactionDetail';
import { formatCurrency, formatDate, formatMatchStatus } from '@/utils/formatters';
import { ACQUIRERS, MATCH_STATUS_OPTIONS, DEFAULT_PAGE_SIZE } from '@/utils/constants';
import { type Transaction } from '@/api/transactions.api';
import { ConfirmDialog } from '@/components/common/ConfirmDialog/ConfirmDialog';

export function TransactionsPage() {
  const [filters, setFilters] = React.useState({
    startDate: '',
    endDate: '',
    acquirer: '',
    matched: '' as '' | 'true' | 'false',
    nsu: '',
    page: 1,
    pageSize: DEFAULT_PAGE_SIZE,
  });
  const [importDialogOpen, setImportDialogOpen] = React.useState(false);
  const [detailOpen, setDetailOpen] = React.useState(false);
  const [selectedTransaction, setSelectedTransaction] = React.useState<Transaction | null>(null);
  const [confirmDeleteOpen, setConfirmDeleteOpen] = React.useState(false);

  const { data, isLoading } = useTransactions({
    start_date: filters.startDate || undefined,
    end_date: filters.endDate || undefined,
    acquirer: filters.acquirer || undefined,
    matched:
      filters.matched === '' ? undefined : (filters.matched === 'true' ? true : false),
    nsu: filters.nsu || undefined,
    page: filters.page,
    page_size: filters.pageSize,
  });

  const deleteTransaction = useDeleteTransaction();
  const importTransactions = useImportTransactions();
  const exportTransactions = useExportTransactions();

  const handleFilterChange = (key: keyof typeof filters, value: string | number) => {
    setFilters((prev) => ({ ...prev, [key]: value, page: 1 }));
  };

  const handlePageChange = (page: number) => setFilters((prev) => ({ ...prev, page }));
  const handlePageSizeChange = (pageSize: number) =>
    setFilters((prev) => ({ ...prev, pageSize, page: 1 }));

  const handleViewTransaction = (transaction: Transaction) => {
    setSelectedTransaction(transaction);
    setDetailOpen(true);
  };

  const handleDelete = (transaction: Transaction) => {
    setSelectedTransaction(transaction);
    setConfirmDeleteOpen(true);
  };

  const handleConfirmDelete = () => {
    if (!selectedTransaction) return;

    deleteTransaction.mutate(selectedTransaction.id, {
      onSuccess: () => setConfirmDeleteOpen(false),
    });
  };

  const handleExport = () => {
    exportTransactions.mutate({
      start_date: filters.startDate || undefined,
      end_date: filters.endDate || undefined,
    });
  };

  const columns = React.useMemo<ColumnDef<Transaction>[]>(
    () => [
      {
        accessorKey: 'nsu',
        header: 'NSU',
      },
      {
        accessorKey: 'acquirer',
        header: 'Adquirente',
        cell: (info) => info.getValue<string>().toUpperCase(),
      },
      {
        accessorKey: 'transaction_date',
        header: 'Data Transação',
        cell: (info) => formatDate(info.getValue<string>()),
      },
      {
        accessorKey: 'settlement_date',
        header: 'Data Liquidação',
        cell: (info) => {
          const value = info.getValue<string | null>();
          return value ? formatDate(value) : '-';
        },
      },
      {
        accessorKey: 'amount',
        header: 'Valor',
        cell: (info) => formatCurrency(info.getValue<number>()),
      },
      {
        accessorKey: 'matched',
        header: 'Status',
        cell: (info) => (
          <Chip
            label={formatMatchStatus(info.getValue<boolean>())}
            color={info.getValue<boolean>() ? 'success' : 'warning'}
            size="small"
          />
        ),
      },
      {
        accessorKey: 'installments',
        header: 'Parcelas',
        cell: (info) => info.getValue<number>() ?? '-',
      },
      {
        accessorKey: 'card_brand',
        header: 'Bandeira',
        cell: (info) => info.getValue<string>() || '-',
      },
      {
        id: 'actions',
        header: 'Ações',
        cell: (info) => {
          const transaction = info.row.original;
          return (
            <Stack direction="row" spacing={1}>
              <Tooltip title="Visualizar">
                <IconButton size="small" onClick={() => handleViewTransaction(transaction)}>
                  <VisibilityIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Excluir">
                <IconButton
                  size="small"
                  color="error"
                  onClick={() => handleDelete(transaction)}
                >
                  <DeleteIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Stack>
          );
        },
      },
    ],
    []
  );

  const rows = data?.items ?? [];
  const totalRows = data?.total ?? 0;

  return (
    <Box display="flex" flexDirection="column" gap={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h4">Transações</Typography>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1}>
          <Button
            variant="outlined"
            startIcon={<CloudUploadIcon />}
            onClick={() => setImportDialogOpen(true)}
          >
            Importar CSV
          </Button>
          <Button
            variant="outlined"
            startIcon={<FileDownloadIcon />}
            onClick={handleExport}
            disabled={exportTransactions.isPending}
          >
            Exportar
          </Button>
        </Stack>
      </Box>

      <Paper sx={{ p: 2 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
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
          <Grid item xs={12} sm={6} md={3}>
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
          <Grid item xs={12} sm={6} md={3}>
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
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              select
              label="Status"
              value={filters.matched}
              onChange={(event) => handleFilterChange('matched', event.target.value)}
              size="small"
            >
              {MATCH_STATUS_OPTIONS.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              label="Buscar por NSU"
              value={filters.nsu}
              onChange={(event) => handleFilterChange('nsu', event.target.value)}
              size="small"
            />
          </Grid>
        </Grid>
      </Paper>

      <DataTable<Transaction>
        data={rows}
        columns={columns}
        loading={isLoading}
        pagination
        searchable={false}
        totalRows={totalRows}
        pageSize={filters.pageSize}
        currentPage={filters.page}
        onPageChange={handlePageChange}
        onPageSizeChange={handlePageSizeChange}
        emptyMessage="Nenhuma transação encontrada"
      />

      <TransactionDetail
        open={detailOpen}
        transaction={selectedTransaction}
        onClose={() => setDetailOpen(false)}
      />

      <ConfirmDialog
        open={confirmDeleteOpen}
        onCancel={() => setConfirmDeleteOpen(false)}
        title="Excluir transação"
        message={`Deseja realmente excluir a transação ${selectedTransaction?.nsu ?? ''}?`}
        onConfirm={handleConfirmDelete}
        cancelLabel="Cancelar"
        confirmLabel="Excluir"
        loading={deleteTransaction.isPending}
      />

      <ImportCSVDialog
        open={importDialogOpen}
        onClose={() => setImportDialogOpen(false)}
        onImport={(file) => importTransactions.mutateAsync(file)}
        title="Importar Transações"
        helperText={
          <Typography variant="body2" color="text.secondary">
            Faça o upload de um arquivo CSV contendo as colunas: nsu, acquirer, amount,
            transaction_date, settlement_date, card_brand, installments.
          </Typography>
        }
      />
    </Box>
  );
}
