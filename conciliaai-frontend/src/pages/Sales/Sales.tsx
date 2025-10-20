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
  InputAdornment,
  IconButton,
  Tooltip,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import SearchIcon from '@mui/icons-material/Search';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import FileUploadIcon from '@mui/icons-material/FileUpload';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import type { ColumnDef } from '@tanstack/react-table';
import { DataTable } from '@/components/common/DataTable/DataTable';
import { CreateSaleModal } from '@/components/features/SaleModal/CreateSaleModal';
import { EditSaleModal } from '@/components/features/SaleModal/EditSaleModal';
import { ConfirmDialog } from '@/components/common/ConfirmDialog/ConfirmDialog';
import { ImportSalesModal } from '@/components/features/ImportModal/ImportSalesModal';
import { useSales } from '@/hooks/useSales';
import { formatCurrency, formatDate, formatPaymentMethod, formatStatus } from '@/utils/formatters';
import { STATUS_OPTIONS, DEFAULT_PAGE_SIZE } from '@/utils/constants';
import type { Sale } from '@/types/api.types';

export function SalesPage() {
  const [filters, setFilters] = React.useState({
    startDate: '',
    endDate: '',
    status: '' as '' | Sale['status'],
    search: '',
    page: 1,
    pageSize: DEFAULT_PAGE_SIZE,
  });
  const [searchInput, setSearchInput] = React.useState('');
  const [createModalOpen, setCreateModalOpen] = React.useState(false);
  const [editModalOpen, setEditModalOpen] = React.useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = React.useState(false);
  const [importModalOpen, setImportModalOpen] = React.useState(false);
  const [selectedSale, setSelectedSale] = React.useState<Sale | null>(null);

  React.useEffect(() => {
    const handler = window.setTimeout(() => {
      setFilters((prev) => ({ ...prev, search: searchInput, page: 1 }));
    }, 300);

    return () => window.clearTimeout(handler);
  }, [searchInput]);

  const { sales, totalSales, currentPage, pageSize, isLoading, deleteSale, isDeleting, exportSales } =
    useSales(filters);

  const handleFilterChange = (key: 'startDate' | 'endDate' | 'status', value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value, page: 1 }));
  };

  const handlePageChange = (page: number) => {
    setFilters((prev) => ({ ...prev, page }));
  };

  const handlePageSizeChange = (size: number) => {
    setFilters((prev) => ({ ...prev, pageSize: size, page: 1 }));
  };

  const handleEdit = (sale: Sale) => {
    setSelectedSale(sale);
    setEditModalOpen(true);
  };

  const handleDelete = (sale: Sale) => {
    setSelectedSale(sale);
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = () => {
    if (!selectedSale) return;

    deleteSale(selectedSale.id, {
      onSuccess: () => {
        setDeleteDialogOpen(false);
        setSelectedSale(null);
      },
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
        accessorKey: 'amount',
        header: 'Valor',
        cell: (info) => formatCurrency(info.getValue<string>()),
      },
      {
        accessorKey: 'date',
        header: 'Data',
        cell: (info) => formatDate(info.getValue<string>()),
      },
      {
        accessorKey: 'payment_method',
        header: 'Método',
        cell: (info) => formatPaymentMethod(info.getValue<string>()),
      },
      {
        accessorKey: 'status',
        header: 'Status',
        cell: (info) => {
          const statusValue = info.getValue<Sale['status']>();
          const statusOption = STATUS_OPTIONS.find((option) => option.value === statusValue);

          return statusOption ? (
            <Chip label={statusOption.label} color={statusOption.color} size="small" />
          ) : (
            <Chip label={formatStatus(statusValue)} size="small" />
          );
        },
      },
      {
        id: 'actions',
        header: 'Ações',
        cell: (info) => {
          const sale = info.row.original;
          return (
            <Box display="flex" gap={1}>
              <Tooltip title="Editar">
                <IconButton size="small" onClick={() => handleEdit(sale)}>
                  <EditIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Excluir">
                <IconButton size="small" color="error" onClick={() => handleDelete(sale)}>
                  <DeleteIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
          );
        },
      },
    ],
    []
  );

  return (
    <Box display="flex" flexDirection="column" gap={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h4">Vendas</Typography>
        <Box display="flex" gap={1}>
          <Button variant="outlined" startIcon={<FileUploadIcon />} onClick={() => setImportModalOpen(true)}>
            Importar
          </Button>
          <Button variant="outlined" startIcon={<FileDownloadIcon />} onClick={exportSales}>
            Exportar
          </Button>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => setCreateModalOpen(true)}>
            Nova Venda
          </Button>
        </Box>
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
              label="Status"
              value={filters.status}
              onChange={(event) => handleFilterChange('status', event.target.value)}
              size="small"
            >
              <MenuItem value="">Todos</MenuItem>
              {STATUS_OPTIONS.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              placeholder="Buscar por NSU..."
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

      <DataTable<Sale>
        data={sales}
        columns={columns}
        loading={isLoading}
        pagination
        totalRows={totalSales}
        currentPage={currentPage}
        pageSize={pageSize}
        onPageChange={handlePageChange}
        onPageSizeChange={handlePageSizeChange}
        searchable={false}
      />

      <CreateSaleModal open={createModalOpen} onClose={() => setCreateModalOpen(false)} />
      <EditSaleModal
        open={editModalOpen}
        sale={selectedSale}
        onClose={() => {
          setEditModalOpen(false);
          setSelectedSale(null);
        }}
      />
      <ConfirmDialog
        open={deleteDialogOpen}
        title="Excluir venda"
        message={selectedSale ? `Tem certeza que deseja excluir a venda ${selectedSale.nsu}?` : ''}
        onConfirm={handleConfirmDelete}
        onCancel={() => {
          setDeleteDialogOpen(false);
          setSelectedSale(null);
        }}
        loading={isDeleting}
        confirmLabel="Excluir"
      />
      <ImportSalesModal open={importModalOpen} onClose={() => setImportModalOpen(false)} />
    </Box>
  );
}
