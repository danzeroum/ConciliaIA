import type { ReactElement } from 'react';
import { render, screen } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material';
import { describe, expect, it } from 'vitest';
import { AccuracyTrendChart } from '@/components/charts/AccuracyTrendChart';

const mockData = [
  { date: '2024-01-01', value: 95.5 },
  { date: '2024-01-02', value: 96.2 },
  { date: '2024-01-03', value: 97.1 },
];

const theme = createTheme();

const renderWithTheme = (ui: ReactElement) =>
  render(<ThemeProvider theme={theme}>{ui}</ThemeProvider>);

describe('AccuracyTrendChart', () => {
  it('renders the chart with the provided title', () => {
    renderWithTheme(<AccuracyTrendChart data={mockData} title="Test Accuracy" />);

    expect(screen.getByText('Test Accuracy')).toBeInTheDocument();
  });

  it('renders without a title when none is provided', () => {
    renderWithTheme(<AccuracyTrendChart data={mockData} />);

    expect(screen.queryByText('Test Accuracy')).not.toBeInTheDocument();
  });

  it('renders without crashing', () => {
    const { container } = renderWithTheme(<AccuracyTrendChart data={mockData} />);

    expect(container.firstChild).not.toBeNull();
  });
});
