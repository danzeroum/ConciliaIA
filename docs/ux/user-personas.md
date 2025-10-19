# Personas - ConciliaAI

## Mariana — Dona de E-commerce

- **Idade:** 34 anos  
- **Negócio:** Loja D2C de cosméticos  
- **Faturamento mensal:** R$ 120.000  
- **Conhecimento técnico:** Baixo  
- **Tempo disponível para finanças:** 2h/semana

### Contexto e Comportamentos
- Administra uma operação enxuta e costuma fazer a reconciliação sozinha.
- Fica sobrecarregada com planilhas extensas e relatórios técnicos.
- Acessa o dashboard principalmente pelo celular em pequenos blocos de tempo.

### Jobs-to-be-Done
1. **Descobrir rapidamente se está perdendo dinheiro.**  
   - Quer saber em até 5 segundos se existe algum problema, quanto representa e qual ação tomar.
2. **Entender divergências sem jargões financeiros.**  
   - Prefere descrições em linguagem simples como “Venda não apareceu” ou “Taxa cobrada a mais”.
3. **Recuperar valores em 1 clique.**  
   - Procura ações diretas com templates prontos de contestação e confirmação imediata.

### Frustrações Atuais
- Planilhas com dezenas de colunas difíceis de interpretar.
- Gráficos genéricos que não indicam claramente o que fazer.
- Fluxos com muitos passos até executar uma contestação.

### Principais Necessidades de UX
- Hierarquia visual clara com números grandes e linguagem natural.
- CTAs verdes evidentes, com feedback imediato após o clique.
- Conteúdo progressivo: visão geral → divergências → detalhes opcionais.

---

## Roberto — Franqueador Multi-Loja

- **Idade:** 48 anos  
- **Função:** Gestor de rede com 8 franquias de açaí  
- **Faturamento mensal consolidado:** R$ 600.000  
- **Conhecimento técnico:** Médio  
- **Tempo disponível para análise:** 30 min/dia

### Contexto e Comportamentos
- Analisa indicadores diariamente no desktop e delega tarefas aos gerentes.
- Precisa acompanhar cada loja separadamente e no consolidado.
- Valoriza histórico auditável e controles de aprovação.

### Jobs-to-be-Done
1. **Visualizar rapidamente quais lojas estão com mais perdas.**  
   - Compara desempenho e quer identificar padrões de divergências por adquirente.
2. **Delegar ações mantendo o controle.**  
   - Gerentes podem tratar divergências menores, mas Roberto aprova recuperações acima de R$ 500.
3. **Antecipar problemas antes que impactem o caixa.**  
   - Busca alertas proativos, tendências de perdas e score de confiabilidade por adquirente.

### Frustrações Atuais
- Sistemas diferentes por loja e dados não consolidados.
- Falta de visibilidade sobre quem tomou cada ação e quando.
- Descobre divergências com meses de atraso.

### Principais Necessidades de UX
- Dashboard consolidado com ranking de performance por loja.
- Filtros rápidos por severidade, adquirente e período.
- Alertas e insights que priorizem atenção e recomendem próximos passos.

---

## Implicações para o Design

- **Linguagem natural:** evitar siglas como NSU, MDR ou settlement sem explicação.
- **Progressive disclosure:** nível 1 com números críticos, nível 2 com cards de divergência, nível 3 com detalhes técnicos colapsados.
- **Ações claras:** CTA “Recuperar agora” destacado para Mariana; opções de delegação e histórico para Roberto.
- **Mobile-first:** fluxo otimizado para telas pequenas, com desktop expandindo os mesmos componentes.
