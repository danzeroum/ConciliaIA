# Plano de Testes de Usabilidade — ConciliaAI Dashboard

## Objetivos do Teste
1. Validar se usuários não técnicos conseguem identificar divergências críticas em até 5 segundos.
2. Medir a taxa de sucesso do fluxo de contestação de 1 clique (meta ≥ 95%).
3. Avaliar a compreensão da linguagem simplificada utilizada nos cards e nos fluxos.

## Participantes
- **Total:** 5 pessoas.  
- **Perfil:** 3 lojistas e-commerce similares à persona Mariana e 2 gestores multi-loja similares à persona Roberto.  
- **Critérios:** Nunca utilizaram plataformas especializadas de reconciliação financeira e possuem baixa ou média familiaridade com termos bancários.

## Cenários e Tarefas

### Tarefa 1 — Descobrir um problema financeiro
- **Cenário:** “Você acabou de abrir o dashboard. Há algum problema financeiro neste mês?”  
- **Objetivo de sucesso:** Identificar o card “Perdido este mês” e verbalizar o valor em menos de 10 segundos.  
- **Métricas:** Tempo na tarefa, taxa de sucesso, confiança percebida.

### Tarefa 2 — Entender uma divergência crítica
- **Cenário:** “Explique o que aconteceu com a venda de R$ 1.200.”  
- **Objetivo de sucesso:** Usar linguagem própria para descrever o problema e o motivo do alerta.  
- **Métricas:** Escala de compreensão (1-5), erros conceituais, necessidade de ajuda.

### Tarefa 3 — Recuperar dinheiro em 1 clique
- **Cenário:** “Tente recuperar os R$ 1.200 que não foram recebidos.”  
- **Objetivo de sucesso:** Completar o fluxo até a confirmação “✅ Pronto!” em menos de 30 segundos.  
- **Métricas:** Número de cliques, taxa de conclusão, tempo, erros críticos.

### Tarefa 4 — Comparar lojas (modo Roberto)
- **Cenário:** “Qual loja está com mais problemas neste mês e por quê?”  
- **Objetivo de sucesso:** Identificar “Loja Sul” e citar o motivo apresentado nos insights.  
- **Métricas:** Tempo, acurácia, clareza da explicação.

## Métricas de Sucesso
```yaml
Quantitativas:
  task_completion_rate: ">= 95%"
  time_on_task_t1: "<= 10s"
  time_on_task_t3: "<= 30s"
  error_rate: "<= 5%"

Qualitativas:
  sus_score: ">= 80"
  satisfaction_rating: ">= 4.5/5"
  willingness_to_use: ">= 90%"
```

## Questionário Pós-Teste
1. Quão fácil foi identificar se havia problemas financeiros? *(1 = muito difícil · 5 = muito fácil)*
2. A linguagem usada no dashboard estava clara? *(1 = incompreensível · 5 = perfeitamente clara)*
3. Você se sentiu confiante para tomar ações? *(1 = nada confiante · 5 = muito confiante)*
4. O que você mais gostou?
5. O que você mudaria?

## Logística e Ferramentas
- **Formato:** Sessões remotas moderadas (Zoom ou Meet) com compartilhamento de tela.  
- **Duração estimada:** 35 minutos por participante.  
- **Ferramentas de registro:** Notion para anotações, Loom para gravação, planilha de métricas no Google Sheets.  
- **Materiais:** Script de moderação, protótipo hospedado (Figma Live Embed ou GitHub Pages), formulário pós-teste.

## Próximos Passos
1. Recrutar participantes com antecedência mínima de 1 semana.  
2. Validar o roteiro de moderação com o time de produto.  
3. Consolidar métricas quantitativas e qualitativas em relatório único.  
4. Priorização de melhorias baseada em impacto (Critical > High > Medium).
