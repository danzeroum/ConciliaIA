import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Button,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import SyncIcon from '@mui/icons-material/Sync';
import AssessmentIcon from '@mui/icons-material/Assessment';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import { ImportCSVDialog } from '@/components/features/ImportCSVDialog';
import { useImportSales } from '@/hooks/useSales';
import { useImportTransactions, useImportTransactionsEDI } from '@/hooks/useTransactions';
import { useKPIs } from '@/hooks/useStats';
import { formatCurrency } from '@/utils/formatters';

export function ReconciliationPage() {
  const [importSalesOpen, setImportSalesOpen] = React.useState(false);
  const [importTransactionsOpen, setImportTransactionsOpen] = React.useState(false);
  const [importEDIOpen, setImportEDIOpen] = React.useState(false);
  const importSales = useImportSales();
  const importTransactions = useImportTransactions();
  const importEDI = useImportTransactionsEDI();
  const { data: kpis } = useKPIs(7);

  return (
    <Box display="flex" flexDirection="column" gap={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h4">Reconciliação</Typography>
        <Button
          variant="contained"
          startIcon={<SyncIcon />}
          onClick={() => window.open('/api/v1/reconciliation/run', '_blank')}
        >
          Executar Reconciliação
        </Button>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Etapas recomendadas
            </Typography>
            <List>
              <ListItem disablePadding sx={{ mb: 2 }}>
                <ListItemIcon>
                  <CloudUploadIcon color="primary" />
                </ListItemIcon>
                <ListItemText
                  primary="Importe o arquivo de vendas"
                  secondary="Utilize o layout padrão do ConciliaAI para acelerar a reconciliação."
                />
                <Button size="small" onClick={() => setImportSalesOpen(true)}>
                  Importar
                </Button>
              </ListItem>

              <ListItem disablePadding sx={{ mb: 2 }}>
                <ListItemIcon>
                  <CloudUploadIcon color="secondary" />
                </ListItemIcon>
                <ListItemText
                  primary="Importe arquivo de transações"
                  secondary="CSV ou EDI (Rede, Cielo, Stone)"
                />
                <Button
                  size="small"
                  onClick={() => setImportTransactionsOpen(true)}
                  sx={{ mr: 1 }}
                >
                  CSV
                </Button>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => setImportEDIOpen(true)}
                >
                  EDI
                </Button>
              </ListItem>

              <ListItem disablePadding>
                <ListItemIcon>
                  <AssessmentIcon color="success" />
                </ListItemIcon>
                <ListItemText
                  primary="Revise divergências e gere relatórios"
                  secondary="Acompanhe a evolução da conciliação e exporte dados para auditoria."
                />
                <Button size="small" onClick={() => (window.location.href = '/divergences')}>
                  Ver divergências
                </Button>
              </ListItem>
            </List>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Status da conciliação (últimos 7 dias)
            </Typography>
            {kpis ? (
              <List>
                <ListItem disablePadding sx={{ mb: 2 }}>
                  <ListItemIcon>
                    <CheckCircleIcon color="success" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Total conciliado"
                    secondary={formatCurrency(kpis.total_amount_reconciled)}
                  />
                </ListItem>
                <ListItem disablePadding sx={{ mb: 2 }}>
                  <ListItemIcon>
                    <CheckCircleIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Matches"
                    secondary={`${kpis.total_matches.toLocaleString('pt-BR')} registros`}
                  />
                </ListItem>
                <ListItem disablePadding>
                  <ListItemIcon>
                    <WarningIcon color="warning" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Divergências pendentes"
                    secondary={`${kpis.pending_divergences} itens aguardando revisão`}
                  />
                </ListItem>
              </List>
            ) : (
              <Typography color="text.secondary">
                Carregando métricas de conciliação...
              </Typography>
            )}
          </Paper>
        </Grid>
      </Grid>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Orientações rápidas
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Após importar os arquivos de vendas e transações, clique em "Executar Reconciliação" para
          que o ConciliaAI aplique as regras de matching. Em seguida, revise as divergências
          identificadas e marque as resolvidas para manter sua operação atualizada.
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Para uma análise aprofundada, utilize a área de relatórios e exporte os dados conciliados
          em formatos compatíveis com seu ERP ou planilhas.
        </Typography>
      </Paper>

      <ImportCSVDialog
        open={importSalesOpen}
        onClose={() => setImportSalesOpen(false)}
        onImport={(file) => importSales.mutateAsync(file)}
        title="Importar Vendas"
      />

      <ImportCSVDialog
        open={importTransactionsOpen}
        onClose={() => setImportTransactionsOpen(false)}
        onImport={(file) => importTransactions.mutateAsync(file)}
        title="Importar Transações (CSV)"
        helperText={
          <Typography variant="body2" color="text.secondary">
            Aceitamos arquivos CSV com as colunas: nsu, acquirer, amount, transaction_date,
            settlement_date, card_brand, installments.
          </Typography>
        }
      />

      <ImportCSVDialog
        open={importEDIOpen}
        onClose={() => setImportEDIOpen(false)}
        onImport={(file) => importEDI.mutateAsync({ file, acquirer: 'rede' })}
        title="Importar Transações (EDI)"
        acceptedFormats=".txt,.edi"
        allowEDI
        helperText={
          <Typography variant="body2" color="text.secondary">
            Envie o arquivo EDI diretamente da Rede (formato EEVC .txt). Não é necessário converter
            para CSV.
          </Typography>
        }
      />
    </Box>
  );
}
