import type { PaymentMethod, SaleStatus, Acquirer } from '@/types/api.types';

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

export function formatStatus(status: string): string {
  const statusMap: Record<SaleStatus | string, string> = {
    matched: 'Conciliado',
    unmatched: 'Não Conciliado',
    pending: 'Pendente',
  };

  return statusMap[status] ?? status;
}

export function formatPaymentMethod(method: string): string {
  const methodMap: Record<PaymentMethod | string, string> = {
    credit_card: 'Cartão de Crédito',
    debit_card: 'Cartão de Débito',
    pix: 'PIX',
    boleto: 'Boleto',
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
