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
import AddIcon from '@mui/icons-material/Add';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import type { ColumnDef } from '@tanstack/react-table';
import { DataTable } from '@/components/common/DataTable/DataTable';
import {
  useSales,
  useCreateSale,
  useUpdateSale,
  useDeleteSale,
  useImportSales,
  useExportSales,
} from '@/hooks/useSales';
import { ImportCSVDialog } from '@/components/features/ImportCSVDialog';
import { SaleFormDialog, type SaleFormData } from '@/components/features/SaleFormDialog';
import { ConfirmDialog } from '@/components/common/ConfirmDialog/ConfirmDialog';
import { formatCurrency, formatDate, formatPaymentMethod, formatMatchStatus } from '@/utils/formatters';
import { PAYMENT_METHODS, MATCH_STATUS_OPTIONS, DEFAULT_PAGE_SIZE } from '@/utils/constants';
import { type Sale } from '@/api/sales.api';

export function SalesPage() {
  const [filters, setFilters] = React.useState({
    startDate: '',
    endDate: '',
    paymentMethod: '',
    matched: '' as '' | 'true' | 'false',
    nsu: '',
    page: 1,
    pageSize: DEFAULT_PAGE_SIZE,
  });
  const [selectedSale, setSelectedSale] = React.useState<Sale | null>(null);
  const [saleFormOpen, setSaleFormOpen] = React.useState(false);
  const [saleFormMode, setSaleFormMode] = React.useState<'create' | 'edit'>('create');
  const [confirmDeleteOpen, setConfirmDeleteOpen] = React.useState(false);
  const [importDialogOpen, setImportDialogOpen] = React.useState(false);

  const { data, isLoading } = useSales({
    start_date: filters.startDate || undefined,
    end_date: filters.endDate || undefined,
    payment_method: filters.paymentMethod || undefined,
    matched:
      filters.matched === '' ? undefined : (filters.matched === 'true' ? true : false),
    nsu: filters.nsu || undefined,
    page: filters.page,
    page_size: filters.pageSize,
  });

  const createSale = useCreateSale();
  const updateSale = useUpdateSale();
  const deleteSale = useDeleteSale();
  const importSales = useImportSales();
  const exportSales = useExportSales();

  const handleFilterChange = (key: keyof typeof filters, value: string | number) => {
    setFilters((prev) => ({ ...prev, [key]: value, page: 1 }));
  };

  const handlePageChange = (page: number) => {
    setFilters((prev) => ({ ...prev, page }));
  };

  const handlePageSizeChange = (pageSize: number) => {
    setFilters((prev) => ({ ...prev, pageSize, page: 1 }));
  };

  const handleCreateSale = () => {
    setSelectedSale(null);
    setSaleFormMode('create');
    setSaleFormOpen(true);
  };

  const handleEditSale = (sale: Sale) => {
    setSelectedSale(sale);
    setSaleFormMode('edit');
    setSaleFormOpen(true);
  };

  const handleDeleteSale = (sale: Sale) => {
    setSelectedSale(sale);
    setConfirmDeleteOpen(true);
  };

  const handleConfirmDelete = () => {
    if (!selectedSale) return;

    deleteSale.mutate(selectedSale.id, {
      onSuccess: () => setConfirmDeleteOpen(false),
    });
  };

  const handleSubmitSale = (formData: SaleFormData) => {
    if (saleFormMode === 'create') {
      createSale.mutate(formData);
    } else if (selectedSale) {
      updateSale.mutate({ id: selectedSale.id, data: formData });
    }
  };

  const handleExport = () => {
    exportSales.mutate({
      start_date: filters.startDate || undefined,
      end_date: filters.endDate || undefined,
    });
  };

  const columns = React.useMemo<ColumnDef<Sale>[]>(
    () => [
      {
        accessorKey: 'nsu',
        header: 'NSU',
        cell: (info) => info.getValue<string>(),
      },
      {
        accessorKey: 'sale_date',
        header: 'Data',
        cell: (info) => formatDate(info.getValue<string>()),
      },
      {
        accessorKey: 'amount',
        header: 'Valor',
        cell: (info) => formatCurrency(info.getValue<number>()),
      },
      {
        accessorKey: 'payment_method',
        header: 'Método',
        cell: (info) => formatPaymentMethod(info.getValue<string>()),
      },
      {
        accessorKey: 'installments',
        header: 'Parcelas',
        cell: (info) => info.getValue<number>() ?? '-',
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
        accessorKey: 'card_brand',
        header: 'Bandeira',
        cell: (info) => info.getValue<string>() || '-',
      },
      {
        id: 'actions',
        header: 'Ações',
        cell: (info) => {
          const sale = info.row.original;
          return (
            <Stack direction="row" spacing={1}>
              <Tooltip title="Editar">
                <IconButton size="small" onClick={() => handleEditSale(sale)}>
                  <EditIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Excluir">
                <IconButton
                  size="small"
                  color="error"
                  onClick={() => handleDeleteSale(sale)}
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

  const selectedSaleInitialData = selectedSale
    ? {
        nsu: selectedSale.nsu,
        amount: selectedSale.amount,
        sale_date: selectedSale.sale_date?.split('T')[0] ?? selectedSale.sale_date,
        payment_method: selectedSale.payment_method,
        installments: selectedSale.installments ?? 1,
        card_brand: selectedSale.card_brand ?? '',
        authorization_code: selectedSale.authorization_code ?? '',
      }
    : undefined;

  return (
    <Box display="flex" flexDirection="column" gap={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h4">Vendas</Typography>
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
            disabled={exportSales.isPending}
          >
            Exportar
          </Button>
          <Button variant="contained" startIcon={<AddIcon />} onClick={handleCreateSale}>
            Nova Venda
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
              label="Método de pagamento"
              value={filters.paymentMethod}
              onChange={(event) => handleFilterChange('paymentMethod', event.target.value)}
              size="small"
            >
              <MenuItem value="">Todos</MenuItem>
              {PAYMENT_METHODS.map((option) => (
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

      <DataTable<Sale>
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
        emptyMessage="Nenhuma venda encontrada"
      />

      <SaleFormDialog
        open={saleFormOpen}
        onClose={() => setSaleFormOpen(false)}
        onSubmit={handleSubmitSale}
        initialData={selectedSaleInitialData}
        mode={saleFormMode}
      />

      <ConfirmDialog
        open={confirmDeleteOpen}
        onCancel={() => setConfirmDeleteOpen(false)}
        title="Excluir venda"
        message={`Deseja realmente excluir a venda ${selectedSale?.nsu ?? ''}?`}
        onConfirm={handleConfirmDelete}
        cancelLabel="Cancelar"
        confirmLabel="Excluir"
        loading={deleteSale.isPending}
      />

      <ImportCSVDialog
        open={importDialogOpen}
        onClose={() => setImportDialogOpen(false)}
        onImport={(file) => importSales.mutateAsync(file)}
        title="Importar Vendas"
      />
    </Box>
  );
}
