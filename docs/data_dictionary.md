# Dicionário de dados

## Escopo da V1

A primeira versão do dataset terá:

- 1 identificador técnico sintético;
- 14 variáveis de entrada;
- 1 variável-alvo.

Total: 16 colunas.

Cada linha representa a situação de um cliente ativo em uma data de referência. As variáveis de entrada devem ser calculadas apenas com informações disponíveis até essa data. O alvo `churn_90d` indica se houve cancelamento nos 90 dias seguintes.

## Colunas da V1

| Variável | Papel | Tipo | Origem operacional provável | Janela temporal | Forma | LGPD em uso real | Descrição |
|---|---|---|---|---|---|---|---|
| `customer_id` | identificador técnico | string | cadastro/CRM | snapshot | gerada diretamente | baixo | identificador sintético único, sem vínculo com pessoa real |
| `tenure_months` | entrada | inteiro | cadastro/CRM | snapshot | gerada diretamente | médio | tempo de relacionamento em meses na data de referência |
| `access_technology` | entrada | categórica | cadastro/comercial | snapshot | gerada diretamente | médio | tecnologia principal de acesso, inicialmente `fiber` ou `radio` |
| `download_speed_mbps` | entrada | inteiro | cadastro/comercial | snapshot | gerada diretamente | baixo | velocidade contratada do plano principal em Mbps |
| `monthly_fee` | entrada | numérica | faturamento/comercial | snapshot | gerada diretamente | médio | valor mensal vigente do serviço principal |
| `has_contract_loyalty` | entrada | binária | cadastro/comercial | snapshot | gerada diretamente | médio | indica se o cliente está em período de fidelidade |
| `payment_method` | entrada | categórica | faturamento | snapshot | gerada diretamente | médio | forma principal de pagamento, como boleto, débito automático ou cartão |
| `invoice_overdue_count_90d` | entrada | inteiro | faturamento | últimos 90 dias | calculada | médio | quantidade de faturas que ficaram vencidas no período |
| `max_days_overdue_90d` | entrada | inteiro | faturamento | últimos 90 dias | calculada | médio | maior número de dias de atraso observado no período |
| `had_price_adjustment_90d` | entrada | binária | faturamento/comercial | últimos 90 dias | calculada | médio | indica se houve reajuste recente de preço |
| `support_tickets_90d` | entrada | inteiro | atendimento/help desk | últimos 90 dias | calculada | médio | total de chamados abertos no período |
| `repeat_issue_90d` | entrada | binária | atendimento/help desk | últimos 90 dias | calculada | médio | indica reincidência de problema semelhante em atendimentos recentes |
| `avg_resolution_hours_90d` | entrada | numérica | atendimento/help desk | últimos 90 dias | calculada | médio | tempo médio de resolução dos chamados encerrados no período |
| `outage_count_30d` | entrada | inteiro | monitoramento/NOC | últimos 30 dias | calculada | baixo | quantidade de eventos de indisponibilidade associados ao cliente ou à sua área de atendimento |
| `network_outage_hours_30d` | entrada | numérica | monitoramento/NOC | últimos 30 dias | calculada | baixo | horas acumuladas de indisponibilidade no período |
| `churn_90d` | alvo | binária | rotulagem sintética | próximos 90 dias | gerada diretamente | alto | indica cancelamento nos 90 dias posteriores à data de referência |

## Grupos de variáveis

### Cadastro e contrato

- `tenure_months`
- `access_technology`
- `download_speed_mbps`
- `monthly_fee`
- `has_contract_loyalty`

Esse grupo descreve a relação comercial do cliente com o provedor e ajuda a capturar estágio de relacionamento, tecnologia contratada, preço e barreiras de saída.

### Financeiro

- `payment_method`
- `invoice_overdue_count_90d`
- `max_days_overdue_90d`
- `had_price_adjustment_90d`

Esse bloco representa atrito de cobrança, histórico recente de atraso e possível sensibilidade a reajuste.

### Atendimento

- `support_tickets_90d`
- `repeat_issue_90d`
- `avg_resolution_hours_90d`

Essas variáveis medem volume de problemas, reincidência e eficiência operacional na resolução.

### Qualidade de rede

- `outage_count_30d`
- `network_outage_hours_30d`

Esse grupo resume o impacto de indisponibilidade com métricas simples e plausíveis para a primeira versão.

## Cuidados com vazamento de dados

- Todas as variáveis de entrada devem usar apenas dados disponíveis até a data de referência.
- O alvo `churn_90d` deve considerar somente eventos entre `reference_date + 1` e `reference_date + 90`.
- Não incluir status de cancelamento em andamento, pedido de desligamento, motivo de cancelamento ou qualquer artefato administrativo de saída.
- Não incluir no dataset qualquer score interno usado para gerar `churn_90d`.
- Evitar variáveis compostas que repliquem diretamente a lógica de rotulagem.
- Se houver múltiplos snapshots por cliente em versões futuras, a separação entre treino e teste não deve ser aleatória sem controle temporal ou por cliente.

## Possibilidade para versões futuras

- `region_competition_level`: variável útil para representar pressão competitiva regional, mas que provavelmente dependeria de fonte comercial externa e pode não estar disponível de forma estruturada em uma primeira aplicação real.
