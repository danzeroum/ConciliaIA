import { describe, expect, it } from 'vitest';
import { saleSchema, validateCSVFile, validateDateRange } from '@/utils/validators';

describe('validators', () => {
  it('validates sale schema with valid data', () => {
    const data = saleSchema.parse({
      nsu: 'ABC123',
      amount: '100.00',
      date: '2024-01-01',
      payment_method: 'pix',
    });
    expect(data.nsu).toBe('ABC123');
  });

  it('rejects invalid sale schema', () => {
    expect(() =>
      saleSchema.parse({ nsu: '', amount: '0', date: '', payment_method: '' })
    ).toThrow();
  });

  it('validates csv files', () => {
    const file = new File(['content'], 'sales.csv', { type: 'text/csv' });
    expect(validateCSVFile(file).valid).toBe(true);
  });

  it('rejects invalid csv extension', () => {
    const file = new File(['content'], 'sales.txt', { type: 'text/plain' });
    expect(validateCSVFile(file).valid).toBe(false);
  });

  it('validates date range', () => {
    expect(validateDateRange('2024-01-01', '2024-01-31').valid).toBe(true);
  });

  it('rejects inverted date range', () => {
    expect(validateDateRange('2024-02-01', '2024-01-31').valid).toBe(false);
  });
});
