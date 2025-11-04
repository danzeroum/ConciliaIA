import { describe, expect, it } from 'vitest';
import {
  formatCurrency,
  formatDate,
  formatDateTime,
  formatPercentage,
  formatMatchStatus,
  formatPaymentMethod,
  formatAcquirer,
  formatFileSize,
} from '@/utils/formatters';

describe('formatters', () => {
  it('formats currency values', () => {
    expect(formatCurrency(1234.56)).toBe('R$\u00a01.234,56');
  });

  it('returns original value when currency is invalid', () => {
    expect(formatCurrency('abc')).toBe('abc');
  });

  it('formats dates', () => {
    expect(formatDate('2024-01-15')).toBe('15/01/2024');
  });

  it('formats date time', () => {
    const result = formatDateTime('2024-01-15T12:34:56Z');
    expect(result).toContain('15/01/2024');
  });

  it('formats percentage values', () => {
    const result = formatPercentage(0.1234);
    expect(result).toContain('12,34');
    expect(result).toContain('%');
  });

  it('formats sale status', () => {
    expect(formatMatchStatus('matched')).toBe('Conciliado');
    expect(formatMatchStatus('other')).toBe('other');
  });

  it('formats payment method', () => {
    expect(formatPaymentMethod('pix')).toBe('PIX');
  });

  it('formats acquirer', () => {
    expect(formatAcquirer('cielo')).toBe('Cielo');
  });

  it('formats file size', () => {
    expect(formatFileSize(1024)).toBe('1 KB');
  });
});
