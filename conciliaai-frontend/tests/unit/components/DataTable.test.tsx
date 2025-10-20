import React from 'react';
import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import type { ColumnDef } from '@tanstack/react-table';
import { DataTable } from '@/components/common/DataTable/DataTable';

interface RowData {
  id: number;
  name: string;
}

const columns: ColumnDef<RowData>[] = [
  {
    accessorKey: 'name',
    header: 'Nome',
    cell: (info) => info.getValue<string>(),
  },
];

const renderWithTheme = (ui: React.ReactElement) =>
  render(<ThemeProvider theme={createTheme()}>{ui}</ThemeProvider>);

describe('DataTable', () => {
  it('renders rows', () => {
    renderWithTheme(
      <DataTable<RowData> data={[{ id: 1, name: 'Teste' }]} columns={columns} pagination={false} />
    );

    expect(screen.getByText('Teste')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    renderWithTheme(<DataTable<RowData> data={[]} columns={columns} loading pagination={false} />);

    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('shows empty message when no data', () => {
    renderWithTheme(<DataTable<RowData> data={[]} columns={columns} pagination={false} />);

    expect(screen.getByText('Nenhum registro encontrado')).toBeInTheDocument();
  });
});
