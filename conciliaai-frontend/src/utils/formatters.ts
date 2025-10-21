import type { PaymentMethod, MatchStatus, Acquirer } from '@/types/api.types';

export function formatCurrency(value: string | number): string {
  const numValue = Number(value);
  if (Number.isNaN(numValue)) {
    return String(value);
  }

  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(numValue);
}

export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  if (Number.isNaN(date.getTime())) {
    return dateString;
  }
  return date.toLocaleDateString('pt-BR');
}

export function formatDateTime(dateString: string): string {
  const date = new Date(dateString);
  if (Number.isNaN(date.getTime())) {
    return dateString;
  }
  return date.toLocaleString('pt-BR');
}

export function formatPercentage(value: string | number): string {
  const numValue = Number(value);
  if (Number.isNaN(numValue)) {
    return String(value);
  }

  return new Intl.NumberFormat('pt-BR', {
    style: 'percent',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(numValue);
}

export function formatNSU(nsu: string): string {
  return nsu;
}

export function formatMatchStatus(status: MatchStatus | boolean | string): string {
  if (typeof status === 'boolean') {
    return status ? 'Conciliado' : 'Não Conciliado';
  }

  const normalized = status as MatchStatus;
  const statusMap: Record<MatchStatus, string> = {
    matched: 'Conciliado',
    unmatched: 'Não Conciliado',
  };

  return statusMap[normalized] ?? String(status);
}

export function formatPaymentMethod(method: string): string {
  const methodMap: Record<PaymentMethod | string, string> = {
    credit: 'Crédito',
    debit: 'Débito',
    pix: 'PIX',
    voucher: 'Voucher',
  };

  return methodMap[method] ?? method;
}

export function formatAcquirer(acquirer: string): string {
  const acquirerMap: Record<Acquirer | string, string> = {
    cielo: 'Cielo',
    rede: 'Rede',
    stone: 'Stone',
  };

  return acquirerMap[acquirer] ?? acquirer;
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  const size = bytes / Math.pow(k, i);
  return `${parseFloat(size.toFixed(2))} ${sizes[i]}`;
}
