import React from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  flexRender,
  type ColumnDef,
  type SortingState,
  type ColumnFiltersState,
} from '@tanstack/react-table';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TablePagination,
  TextField,
  Box,
  CircularProgress,
  Typography,
} from '@mui/material';

export interface DataTableProps<TData> {
  data: TData[];
  columns: ColumnDef<TData, any>[];
  loading?: boolean;
  onRowClick?: (row: TData) => void;
  pagination?: boolean;
  searchable?: boolean;
  totalRows?: number;
  pageSize?: number;
  currentPage?: number;
  onPageChange?: (page: number) => void;
  onPageSizeChange?: (pageSize: number) => void;
  emptyMessage?: string;
}

export function DataTable<TData>({
  data,
  columns,
  loading = false,
  onRowClick,
  pagination = true,
  searchable = true,
  totalRows,
  pageSize = 50,
  currentPage = 1,
  onPageChange,
  onPageSizeChange,
  emptyMessage = 'Nenhum registro encontrado',
}: DataTableProps<TData>) {
  const [sorting, setSorting] = React.useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>([]);
  const [globalFilter, setGlobalFilter] = React.useState('');
  const [paginationState, setPaginationState] = React.useState({
    pageIndex: Math.max(currentPage - 1, 0),
    pageSize,
  });

  React.useEffect(() => {
    setPaginationState({ pageIndex: Math.max(currentPage - 1, 0), pageSize });
  }, [currentPage, pageSize]);

  const table = useReactTable({
    data,
    columns,
    state: {
      sorting,
      columnFilters,
      globalFilter,
      pagination: paginationState,
    },
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    manualPagination: Boolean(pagination && (onPageChange || totalRows !== undefined)),
    pageCount:
      pagination && totalRows !== undefined
        ? Math.ceil(totalRows / paginationState.pageSize)
        : undefined,
  });

  const handlePageChange = (_: unknown, page: number) => {
    setPaginationState((prev) => ({ ...prev, pageIndex: page }));
    onPageChange?.(page + 1);
  };

  const handlePageSizeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newSize = Number(event.target.value);
    setPaginationState({ pageIndex: 0, pageSize: newSize });
    onPageSizeChange?.(newSize);
  };

  if (loading) {
    return (
      <Paper sx={{ p: 6, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Paper>
    );
  }

  if (!loading && data.length === 0) {
    return (
      <Paper sx={{ p: 6 }}>
        <Typography align="center" color="text.secondary">
          {emptyMessage}
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 2 }}>
      {searchable && (
        <TextField
          value={globalFilter ?? ''}
          onChange={(e) => setGlobalFilter(e.target.value)}
          placeholder="Buscar..."
          fullWidth
          margin="normal"
          size="small"
        />
      )}

      <TableContainer>
        <Table size="small">
          <TableHead>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableCell
                    key={header.id}
                    onClick={header.column.getToggleSortingHandler()}
                    sx={{ cursor: header.column.getCanSort() ? 'pointer' : 'default' }}
                  >
                    <Box display="flex" alignItems="center" gap={0.5}>
                      {flexRender(header.column.columnDef.header, header.getContext())}
                      {header.column.getIsSorted() === 'asc' && '🔼'}
                      {header.column.getIsSorted() === 'desc' && '🔽'}
                    </Box>
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableHead>
          <TableBody>
            {table.getRowModel().rows.map((row) => (
              <TableRow
                key={row.id}
                hover
                onClick={() => onRowClick?.(row.original)}
                sx={{ cursor: onRowClick ? 'pointer' : 'default' }}
              >
                {row.getVisibleCells().map((cell) => (
                  <TableCell key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {pagination && (
        <TablePagination
          component="div"
          count={totalRows ?? table.getFilteredRowModel().rows.length}
          page={paginationState.pageIndex}
          onPageChange={handlePageChange}
          rowsPerPage={paginationState.pageSize}
          onRowsPerPageChange={handlePageSizeChange}
          rowsPerPageOptions={[10, 25, 50, 100]}
        />
      )}
    </Paper>
  );
}
