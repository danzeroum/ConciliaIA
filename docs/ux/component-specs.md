# Especificações de Componentes — ConciliaAI

> Linguagem de referência: TypeScript + React.

## DivergenceCard
```typescript
export type Severity = 'critical' | 'high' | 'medium' | 'low';
export type Acquirer = 'cielo' | 'rede' | 'stone' | 'getnet' | 'pagseguro';

export interface DivergenceCardProps {
  id: string;
  severity: Severity;
  title: string;
  amount: number;
  description: string;
  daysOpen: number;
  acquirer: Acquirer;
  installmentInfo?: string;
  expectedValue?: number;
  chargedValue?: number;
  onRecover: (id: string) => void;
  onViewDetails?: (id: string) => void;
}
```

### Regras de UX
- Borda esquerda de 4px e badge correspondente à severidade.  
- Valor formatado em Real brasileiro (`Intl.NumberFormat`).  
- Mostrar “há X dias” gerado automaticamente via `formatDistance`.  
- CTA primário sempre visível; secundário opcional.

## RecoverButton
```typescript
export interface RecoverButtonProps {
  amount: number;
  loading?: boolean;
  disabled?: boolean;
  onClick: () => void;
}
```

### Regras de UX
- Texto dinâmico: `Recuperar R$ {amount}` (usar `toLocaleString`).  
- Estado `loading` exibe spinner + label “Processando…”.  
- `aria-label` deve repetir o valor (ex.: “Recuperar 1.200 reais”).  
- Bloquear clique duplo enquanto `loading`.

## SeverityBadge
```typescript
export interface SeverityBadgeProps {
  severity: Severity;
  children?: React.ReactNode;
}
```

### Regras de UX
- Texto uppercase (CRÍTICA, ALTA, MÉDIA, BAIXA).  
- Ícone padrão: 🔴, 🟠, 🟡, 🟣 — pode ser sobrescrito via `children`.  
- Usar tokens `--color-*-bg` e `--color-*` para cores de fundo/borda.

## MetricCard
```typescript
export interface MetricCardProps {
  variant?: 'primary' | 'secondary';
  icon: React.ReactNode;
  label: string;
  value: string;
  meta?: string;
  trend?: 'up' | 'down' | 'neutral';
}
```

### Regras de UX
- Variante `primary` ocupa largura total, tipografia 36px.  
- Variante `secondary` possui espaçamento 24px, valor 28px.  
- Trend `up/down` acrescenta seta e cor (verde/vermelho) com descrição curta.

## Timeline
```typescript
export interface TimelineStep {
  id: string;
  title: string;
  description: string;
  icon?: React.ReactNode;
}

export interface TimelineProps {
  steps: TimelineStep[];
  orientation?: 'vertical' | 'horizontal';
}
```

### Regras de UX
- Default vertical, com ícones enumerados 1️⃣, 2️⃣, 3️⃣.  
- Espaçamento de 16px entre itens; descrição com 13px.  
- Suporte a leitores de tela: renderizar `<ol>` semântico.

## Modal (Dialog)
```typescript
export interface DialogProps {
  isOpen: boolean;
  title: string;
  description?: string;
  onClose: () => void;
  primaryAction: {
    label: string;
    onClick: () => void;
  };
  secondaryAction?: {
    label: string;
    onClick: () => void;
  };
}
```

### Regras de UX
- Utilizar bibliotecas acessíveis (`@reach/dialog` ou `radix-ui`).  
- Foco inicial no título ou no botão primário.  
- Fechar com ESC, clique no overlay ou ação secundária.  
- `aria-live="polite"` para mensagens de sucesso dentro do modal.

## RankingCard (Roberto)
```typescript
export interface RankingCardProps {
  position: number;
  storeName: string;
  accuracy: number; // 0-1
  amountLost: number;
  divergences: number;
  highlight?: boolean;
  onInspect?: () => void;
}
```

### Regras de UX
- Exibir medalhas 🥇/🥈/🥉 para top 3.  
- Quando `highlight` estiver ativo (ex.: loja com alerta), mostrar ícone ⚠️ e CTA “Analisar”.  
- Valores formatados em percentual/Real com tooltip opcional de tendência.
