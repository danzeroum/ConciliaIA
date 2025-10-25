# ADR-003: Parser Rede TORC para Captura Off-line

## Status
Proposto

## Contexto
Estabelecimentos com vendas recorrentes precisam enviar arquivos TORC (Transmissão Off-line Recorrente) para a Rede processar débitos mensais. O ConciliaAI não possuía parser específico para este layout CSV rígido, impossibilitando a conciliação dessas operações.

## Decisão
Implementar o `RedeTORCParser`, herdando de `BaseAcquirerParser`, responsável por validar a estrutura do arquivo, mapear bandeiras suportadas e normalizar os resumos de vendas para o modelo canônico da plataforma. Erros estruturais rejeitam o arquivo inteiro conforme o manual TORC v2.00.

## Consequências
+ Suporte a vendas recorrentes de débito e modalidade "Compre e Saque" via TORC.
+ Validações rígidas evitam inconsistências financeiras.
- Maior complexidade de manutenção devido aos múltiplos tipos de registros.
- Dependência das VANs homologadas para o tráfego seguro dos arquivos.

## Referências
- Manual do Desenvolvedor Captura Off-line TORC v2.00
- https://www.userede.com.br/documentos
