# Visão Multi-loja — Roberto

## Objetivo
Permitir que o franqueador identifique rapidamente quais lojas apresentam maior risco financeiro, delegue ações e antecipe problemas.

## Estrutura da Tela
1. **Cabeçalho com seletor de lojas:** dropdown “Todas as lojas” permitindo filtrar por unidade.  
2. **Métrica principal:** card "Total perdido este mês" consolidado.  
3. **Ranking de performance:** lista de cards ordenados por acurácia, com medalhas e alertas.  
4. **Tendências:** gráfico simples de barras comparando perdas por loja (últimos 30 dias).  
5. **Insights acionáveis:** bullets destacando padrões e recomendações (ex.: “89% das perdas estão na adquirente Rede”).

## Interações-chave
- **Delegação:** botão “Analisar” abre modal com opções de atribuição para gerentes e histórico de aprovações.  
- **Limites:** contestações acima de R$ 500 solicitam aprovação de Roberto (badge “Aguardar aprovação”).  
- **Alertas proativos:** notificações e e-mails quando tendência de perdas sobe > 10% semana/semana.

## Componentes Reaproveitados
- `MetricCard` (variante primária).  
- `RankingCard` com suporte a ícone ⚠️ quando `highlight = true`.  
- `SeverityBadge` para sinalizar lojas críticas.  
- `Timeline` adaptada para histórico de ações.

## Conteúdo e Linguagem
- Usar frases como “Loja Sul perdeu R$ 3.456 este mês” em vez de “Variance MDR 18%”.  
- Apresentar recomendações claras: “Revisar credenciais Rede” ou “Conferir vendas parceladas 6x”.  
- Permitir exportar resumo para PDF com histórico auditável.
