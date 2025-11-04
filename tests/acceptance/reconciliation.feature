# language: pt
Funcionalidade: Reconciliação Automática de Transações
  Como lojista
  Quero que o sistema reconcilie automaticamente minhas vendas com os recebimentos
  Para economizar tempo e detectar divergências

  Contexto:
    Dado que o sistema está conectado às adquirentes Cielo, Rede e Stone
    E as vendas do POS foram importadas
    E as transações das adquirentes foram coletadas

  # Cenário 1: Match Exato
  Cenário: Reconciliação com match exato (100% confidence)
    Dado que eu tenho 100 vendas no POS do dia "2025-01-18"
    E a Cielo enviou 100 transações do dia "2025-01-18"
    E todas as vendas têm NSU, amount e date idênticos às transações
    Quando o sistema executar reconciliação
    Então deve encontrar 100 matches exatos
    E a taxa de reconciliação deve ser >= 99.5%
    E o tempo de processamento deve ser < 2 segundos
    E a confidence média deve ser 1.00

  # Cenário 2: Fuzzy Match (Amount)
  Cenário: Reconciliação com divergência pequena de valor
    Dado que eu tenho 1 venda:
      | sale_id  | nsu       | amount | date       |
      | SALE-001 | 123456789 | 150.00 | 2025-01-18 |
    E a Cielo registrou 1 transação:
      | transaction_id | nsu       | amount | date       |
      | CIE-TX-001     | 123456789 | 149.75 | 2025-01-18 |
    Quando o sistema executar reconciliação
    Então deve encontrar 1 match fuzzy_amount
    E a confidence deve ser >= 0.90
    E a diferença calculada deve ser R$ 0.25
    E NÃO deve gerar anomalia (dentro da tolerância)

  # Cenário 3: Detecção de Taxa MDR Incorreta
  Cenário: Taxa MDR cobrada acima do esperado
    Dado que eu tenho 1 venda débito Cielo de R$ 1.000,00
    E a taxa esperada é 2.5% = R$ 25,00
    E a Cielo cobrou R$ 35,00 (taxa de 3.5%)
    Quando o sistema detectar a anomalia
    Então deve alertar "Taxa MDR 40% acima do esperado"
    E deve classificar severidade como "CRITICAL"
    E deve calcular valor_recuperavel como R$ 10,00
    E deve sugerir ação "Contestar R$ 10,00 com Cielo"
    E deve aguardar aprovação humana para contestação

  # Cenário 4: Venda sem Transação (Missing Transaction)
  Cenário: Venda sem transação correspondente após D+7
    Dado que eu tenho 1 venda:
      | sale_id  | amount | date       | acquirer |
      | SALE-042 | 500.00 | 2025-01-10 | cielo    |
    E hoje é dia "2025-01-20" (D+10)
    E NÃO existe transação correspondente na Cielo
    E a venda NÃO foi cancelada
    Quando o sistema detectar transação missing
    Então deve alertar "Possível venda não capturada - R$ 500"
    E deve classificar severidade como "HIGH"
    E deve calcular days_elapsed como 10
    E deve sugerir ação "Verificar captura com adquirente"
    E deve enviar notificação email

  # Cenário 5: Chargeback Não Autorizado
  Cenário: Chargeback detectado sem autorização do lojista
    Dado que eu tenho 1 transação Cielo:
      | transaction_id | amount | status     | chargeback_fee |
      | CIE-TX-999     | 800.00 | chargeback | 50.00          |
    E a venda correspondente NÃO foi cancelada no POS
    E eu NÃO autorizei o chargeback
    Quando o sistema detectar chargeback não autorizado
    Então deve alertar "Chargeback não autorizado de R$ 800"
    E deve classificar severidade como "CRITICAL"
    E deve calcular total_loss como R$ 850,00 (800 + 50)
    E deve sugerir "Contestar imediatamente - 30 dias para resposta"
    E deve listar evidências_necessarias:
      | evidencia              |
      | Comprovante de venda   |
      | Nota fiscal            |
      | Comprovante de entrega |

  # Cenário 6: Parcelado - Match Múltiplas Liquidações
  Cenário: Reconciliar venda parcelada com múltiplas liquidações
    Dado que eu tenho 1 venda parcelada:
      | sale_id  | amount  | installments |
      | SALE-100 | 1200.00 | 12           |
    E a Cielo processou como "parcelado loja"
    E enviou 12 transações:
      | installment | amount | expected_date |
      | 1/12        | 100.00 | 2025-02-18    |
      | 2/12        | 100.00 | 2025-03-18    |
      | ...         | ...    | ...           |
      | 12/12       | 100.00 | 2026-01-18    |
    Quando o sistema executar reconciliação
    Então deve criar 12 matches individuais
    E cada match deve ter confidence >= 0.98
    E o match_type deve ser "installment"
    E a soma dos amounts deve ser R$ 1.200,00

  # Cenário 7: Pagamento Atrasado
  Cenário: Pagamento atrasado pela adquirente > 15 dias
    Dado que eu tenho 1 liquidação prevista:
      | settlement_id | expected_date | net_amount | status  |
      | SETT-555      | 2025-01-15    | 950.00     | pending |
    E hoje é "2025-02-01" (17 dias de atraso)
    Quando o sistema detectar settlement delay
    Então deve alertar "Pagamento de R$ 950 atrasado há 17 dias"
    E deve classificar severidade como "HIGH"
    E deve sugerir "Contactar Cielo - solicitar previsão"
    E deve trackear em dashboard de pendências

  # Cenário 8: Performance - Volume Alto
  Cenário: Processar 10k transações em tempo hábil
    Dado que eu tenho 10.000 vendas no POS
    E as adquirentes enviaram 10.000 transações
    Quando o sistema executar reconciliação
    Então deve processar em < 5 minutos
    E a taxa de matching deve ser >= 99.5%
    E o sistema deve permanecer responsivo

  # Cenário 9: Múltiplos Pagamentos (Split Payment)
  Cenário: Venda paga com 2 cartões diferentes
    Dado que eu tenho 1 venda de R$ 500,00
    E o cliente pagou com 2 cartões:
      | card_last_4 | amount | timestamp           |
      | 1234        | 300.00 | 2025-01-18T14:30:15 |
      | 5678        | 200.00 | 2025-01-18T14:30:45 |
    E as 2 transações foram processadas pela Cielo
    Quando o sistema executar reconciliação
    Então deve detectar multiple_payments
    E deve criar 1 match agrupado
    E a confidence deve ser >= 0.85
    E deve marcar requires_human_review como true

  # Cenário 10: Exportação Excel
  Cenário: Exportar relatório de reconciliação
    Dado que a reconciliação foi executada
    E existem 95 matches, 3 divergências e 2 missing
    Quando eu clicar em "Exportar para Excel"
    Então deve gerar arquivo Excel com 3 abas:
      | aba_name    | rows |
      | Matched     | 95   |
      | Divergences | 3    |
      | Summary     | 1    |
    E o arquivo deve ter formatação profissional
    E deve incluir filtros aplicados no dashboard
    E o download deve iniciar em < 3 segundos
