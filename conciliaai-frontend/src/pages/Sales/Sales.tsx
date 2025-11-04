import React, { useMemo, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
  IconButton,
  MenuItem,
  Paper,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import UploadIcon from '@mui/icons-material/Upload';
import DownloadIcon from '@mui/icons-material/Download';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import VisibilityIcon from '@mui/icons-material/Visibility';
import type { ColumnDef } from '@tanstack/react-table';
import { DataTable } from '@/components/common/DataTable/DataTable';
import { ImportCSVDialog } from '@/components/features/ImportCSVDialog';
import { PDFExport } from '@/components/features/PDFExport';
import { SaleFormDialog } from '@/components/features/SaleFormDialog';
import { useExportSalesExcel } from '@/hooks/useExport';
import {
  useCreateSale,
  useDeleteSale,
  useExportSales,
  useImportSales,
  useSales,
  useUpdateSale,
} from '@/hooks/useSales';
import type { Sale } from '@/api/sales.api';

interface FiltersState {
  start_date: string;
  end_date: string;
  payment_method: string;
  matched: '' | 'true' | 'false';
  nsu: string;
}

export function SalesPage() {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  const [filters, setFilters] = useState<FiltersState>({
    start_date: '',
    end_date: '',
    payment_method: '',
    matched: '',
    nsu: '',
  });
  const [importDialogOpen, setImportDialogOpen] = useState(false);
  const [formDialogOpen, setFormDialogOpen] = useState(false);
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);
  const [formMode, setFormMode] = useState<'create' | 'edit'>('create');
  const [selectedSale, setSelectedSale] = useState<Sale | null>(null);

  const matchedFilter = filters.matched === '' ? undefined : filters.matched === 'true';

  const { data: salesData, isLoading, error } = useSales({
    start_date: filters.start_date || undefined,
    end_date: filters.end_date || undefined,
    payment_method: filters.payment_method || undefined,
    matched: matchedFilter,
    nsu: filters.nsu || undefined,
    page,
    page_size: pageSize,
  });

  const createSale = useCreateSale();
  const updateSale = useUpdateSale();
  const deleteSale = useDeleteSale();
  const importSales = useImportSales();
  const exportSales = useExportSales();
  const exportSalesExcel = useExportSalesExcel();

  const handleFilterChange = (field: keyof FiltersState, value: string) => {
    setFilters((prev) => ({ ...prev, [field]: value }));
    setPage(1);
  };

  const handleCreate = () => {
    setFormMode('create');
    setSelectedSale(null);
    setFormDialogOpen(true);
  };

  const handleEdit = (sale: Sale) => {
    setFormMode('edit');
    setSelectedSale(sale);
    setFormDialogOpen(true);
  };

  const handleDelete = async (id: string) => {
    const confirmed = window.confirm('Tem certeza que deseja excluir esta venda?');
    if (!confirmed) return;

    try {
      await deleteSale.mutateAsync(id);
    } catch (mutationError) {
      console.error('Erro ao excluir venda', mutationError);
    }
  };

  const handleFormSubmit = async (data: any) => {
    try {
      if (formMode === 'create') {
        await createSale.mutateAsync(data);
      } else if (selectedSale) {
        await updateSale.mutateAsync({ id: selectedSale.id, data });
      }
      setFormDialogOpen(false);
      setSelectedSale(null);
    } catch (mutationError) {
      console.error('Erro ao salvar venda', mutationError);
    }
  };

  const handleViewDetails = (sale: Sale) => {
    setSelectedSale(sale);
    setDetailDialogOpen(true);
  };

  const handleImport = async (file: File) => {
    await importSales.mutateAsync(file);
  };

  const handleExport = async () => {
    try {
      await exportSales.mutateAsync({
        start_date: filters.start_date || undefined,
        end_date: filters.end_date || undefined,
      });
    } catch (mutationError) {
      console.error('Erro ao exportar vendas', mutationError);
    }
  };

  const handleClearFilters = () => {
    setFilters({ start_date: '', end_date: '', payment_method: '', matched: '', nsu: '' });
    setPage(1);
  };

  const columns: ColumnDef<Sale>[] = useMemo(
    () => [
      {
        accessorKey: 'nsu',
        header: 'NSU',
        cell: (info) => (
          <Typography variant="body2" fontWeight="medium">
            {info.getValue<string>()}
          </Typography>
        ),
      },
      {
        accessorKey: 'amount',
        header: 'Valor',
        cell: (info) =>
          new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL',
          }).format(info.getValue<number>()),
      },
      {
        accessorKey: 'sale_date',
        header: 'Data',
        cell: (info) => new Date(info.getValue<string>()).toLocaleDateString('pt-BR'),
      },
      {
        accessorKey: 'payment_method',
        header: 'Método',
        cell: (info) => {
          const value = info.getValue<string>();
          const methods: Record<string, string> = {
            credit: 'Crédito',
            debit: 'Débito',
            pix: 'PIX',
            voucher: 'Voucher',
          };
          return methods[value] ?? value;
        },
      },
      {
        accessorKey: 'installments',
        header: 'Parcelas',
        cell: (info) => `${info.getValue<number>()}x`,
      },
      {
        accessorKey: 'card_brand',
        header: 'Bandeira',
        cell: (info) => info.getValue<string>() || '-',
      },
      {
        accessorKey: 'matched',
        header: 'Status',
        cell: (info) => {
          const matched = info.getValue<boolean>();
          return (
            <Chip
              label={matched ? 'Reconciliado' : 'Pendente'}
              color={matched ? 'success' : 'warning'}
              size="small"
              variant={matched ? 'filled' : 'outlined'}
            />
          );
        },
      },
      {
        id: 'actions',
        header: 'Ações',
        cell: ({ row }) => (
          <Box display="flex" gap={0.5}>
            <Tooltip title="Ver Detalhes">
              <IconButton size="small" onClick={() => handleViewDetails(row.original)}>
                <VisibilityIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            <Tooltip title="Editar">
              <IconButton size="small" onClick={() => handleEdit(row.original)}>
                <EditIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            <Tooltip title="Excluir">
              <IconButton size="small" color="error" onClick={() => handleDelete(row.original.id)}>
                <DeleteIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
        ),
      },
    ],
    []
  );

  const activeFiltersCount = Object.values(filters).filter((value) => value !== '').length;

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Vendas</Typography>
        <Box display="flex" gap={1} alignItems="center">
          <Button variant="outlined" startIcon={<UploadIcon />} onClick={() => setImportDialogOpen(true)}>
            Importar CSV
          </Button>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={handleExport}
            disabled={exportSales.isPending}
          >
            {exportSales.isPending ? <CircularProgress size={20} /> : 'Exportar CSV'}
          </Button>
          <Button
            variant="outlined"
            startIcon={exportSalesExcel.isPending ? <CircularProgress size={20} /> : <DownloadIcon />}
            onClick={() =>
              exportSalesExcel.mutate({
                start_date: filters.start_date || undefined,
                end_date: filters.end_date || undefined,
              })
            }
            disabled={exportSalesExcel.isPending}
          >
            {exportSalesExcel.isPending ? 'Exportando...' : 'Excel'}
          </Button>
          <PDFExport targetElementId="sales-export-table" filename="vendas" />
          <Button variant="contained" startIcon={<AddIcon />} onClick={handleCreate}>
            Nova Venda
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          Erro ao carregar vendas: {error instanceof Error ? error.message : 'Erro desconhecido'}
        </Alert>
      )}

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" gap={2} alignItems="flex-end" flexWrap="wrap">
            <TextField
              label="Data Inicial"
              type="date"
              value={filters.start_date}
              onChange={(event) => handleFilterChange('start_date', event.target.value)}
              InputLabelProps={{ shrink: true }}
              sx={{ minWidth: 150 }}
            />
            <TextField
              label="Data Final"
              type="date"
              value={filters.end_date}
              onChange={(event) => handleFilterChange('end_date', event.target.value)}
              InputLabelProps={{ shrink: true }}
              sx={{ minWidth: 150 }}
            />
            <TextField
              select
              label="Método Pagamento"
              value={filters.payment_method}
              onChange={(event) => handleFilterChange('payment_method', event.target.value)}
              sx={{ minWidth: 150 }}
            >
              <MenuItem value="">Todos</MenuItem>
              <MenuItem value="credit">Crédito</MenuItem>
              <MenuItem value="debit">Débito</MenuItem>
              <MenuItem value="pix">PIX</MenuItem>
              <MenuItem value="voucher">Voucher</MenuItem>
            </TextField>
            <TextField
              select
              label="Status"
              value={filters.matched}
              onChange={(event) => handleFilterChange('matched', event.target.value)}
              sx={{ minWidth: 150 }}
            >
              <MenuItem value="">Todos</MenuItem>
              <MenuItem value="true">Reconciliados</MenuItem>
              <MenuItem value="false">Pendentes</MenuItem>
            </TextField>
            <TextField
              label="Filtrar por NSU"
              value={filters.nsu}
              onChange={(event) => handleFilterChange('nsu', event.target.value)}
              placeholder="Digite o NSU..."
              sx={{ minWidth: 200 }}
            />
            {activeFiltersCount > 0 && (
              <Button variant="text" onClick={handleClearFilters} color="inherit">
                Limpar ({activeFiltersCount})
              </Button>
            )}
          </Box>
        </CardContent>
      </Card>

      <Box id="sales-export-table">
        <DataTable
          columns={columns}
          data={salesData?.items || []}
          loading={isLoading}
          pagination
          searchable={false}
          totalRows={salesData?.total || 0}
          pageSize={pageSize}
          currentPage={page}
          onPageChange={setPage}
          onPageSizeChange={(size) => {
            setPageSize(size);
            setPage(1);
          }}
          emptyMessage="Nenhuma venda encontrada"
        />
      </Box>

      <ImportCSVDialog
        open={importDialogOpen}
        onClose={() => setImportDialogOpen(false)}
        onImport={handleImport}
        title="Importar Vendas"
      />

      <SaleFormDialog
        open={formDialogOpen}
        onClose={() => {
          setFormDialogOpen(false);
          setSelectedSale(null);
        }}
        onSubmit={handleFormSubmit}
        initialData={selectedSale || undefined}
        mode={formMode}
      />

      <Dialog open={detailDialogOpen} onClose={() => setDetailDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Detalhes da Venda
          {selectedSale?.matched && <Chip label="Reconciliado" color="success" size="small" sx={{ ml: 2 }} />}
        </DialogTitle>
        <DialogContent>
          {selectedSale && (
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  NSU
                </Typography>
                <Typography variant="body1" fontWeight="medium">
                  {selectedSale.nsu}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  Valor
                </Typography>
                <Typography variant="body1" fontWeight="medium">
                  {new Intl.NumberFormat('pt-BR', {
                    style: 'currency',
                    currency: 'BRL',
                  }).format(selectedSale.amount)}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  Data da Venda
                </Typography>
                <Typography variant="body1">
                  {new Date(selectedSale.sale_date).toLocaleDateString('pt-BR')}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  Método de Pagamento
                </Typography>
                <Typography variant="body1">
                  {selectedSale.payment_method === 'credit'
                    ? 'Crédito'
                    : selectedSale.payment_method === 'debit'
                    ? 'Débito'
                    : selectedSale.payment_method === 'pix'
                    ? 'PIX'
                    : selectedSale.payment_method}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  Parcelas
                </Typography>
                <Typography variant="body1">{selectedSale.installments}x</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  Bandeira
                </Typography>
                <Typography variant="body1">{selectedSale.card_brand || 'N/A'}</Typography>
              </Grid>
              {selectedSale.authorization_code && (
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">
                    Código de Autorização
                  </Typography>
                  <Typography variant="body1">{selectedSale.authorization_code}</Typography>
                </Grid>
              )}
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  Criado em
                </Typography>
                <Typography variant="body1">
                  {new Date(selectedSale.created_at).toLocaleString('pt-BR')}
                </Typography>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailDialogOpen(false)}>Fechar</Button>
          {selectedSale && (
            <Button
              variant="contained"
              onClick={() => {
                setDetailDialogOpen(false);
                handleEdit(selectedSale);
              }}
            >
              Editar
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
}
