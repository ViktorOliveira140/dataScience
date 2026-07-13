# Dicionário de dados

## Escopo da V1

A primeira versão do dataset terá:

- 1 identificador técnico sintético;
- 14 variáveis de entrada;
- 1 variável-alvo.

Total: 16 colunas.

Cada linha representa a situação de um cliente ativo em uma data de referência. As variáveis de entrada devem ser calculadas apenas com informações disponíveis até essa data. O alvo `churn_90d` indica se houve cancelamento voluntário solicitado pelo cliente nos 90 dias seguintes.

A prevalência de faturas vencidas no dataset é uma hipótese sintética para demonstração, próxima de 25% na geração padrão. Ela não deve ser apresentada como taxa real da empresa.

## Colunas da V1

| Variável | Papel | Tipo | Origem operacional provável | Janela temporal | Forma | LGPD em uso real | Descrição |
|---|---|---|---|---|---|---|---|
| `customer_id` | identificador técnico | string | cadastro/CRM | snapshot | gerada diretamente | baixo | identificador sintético único, sem vínculo com pessoa real |
| `tenure_months` | entrada | inteiro | cadastro/CRM | snapshot | gerada diretamente | médio | tempo de relacionamento em meses na data de referência |
| `access_technology` | entrada | categórica | cadastro/comercial | snapshot | gerada diretamente | médio | tecnologia principal de acesso, inicialmente `fiber` ou `radio` |
| `download_speed_mbps` | entrada | inteiro | cadastro/comercial | snapshot | gerada diretamente | baixo | velocidade contratada do plano principal em Mbps |
| `monthly_fee` | entrada | numérica | faturamento/comercial | snapshot | gerada diretamente | médio | valor mensal vigente do serviço principal |
| `has_contract_loyalty` | entrada | binária | cadastro/comercial | snapshot | gerada diretamente | médio | indica se o cliente está em período de fidelidade |
| `overdue_invoice_count` | entrada | inteiro | faturamento/cobrança | snapshot | calculada | médio | quantidade de faturas vencidas e ainda não pagas na data de referência |
| `oldest_overdue_days` | entrada | inteiro | faturamento/cobrança | snapshot | calculada | médio | dias de atraso da fatura vencida mais antiga; zero quando não há fatura vencida ou quando `overdue_invoice_count` é zero; pode ultrapassar 60 dias porque a dívida permanece após expiração do boleto |
| `active_agreement_installment_amount` | entrada | numérica | cobrança/acordos | snapshot | calculada | médio | valor da parcela de acordo adicionada à cobrança recorrente; zero quando não há acordo ativo |
| `had_price_adjustment_90d` | entrada | binária | faturamento/comercial | últimos 90 dias | calculada | médio | indica se houve reajuste recente de preço |
| `support_tickets_90d` | entrada | inteiro | atendimento/help desk | últimos 90 dias | calculada | médio | total de chamados abertos no período |
| `repeat_issue_90d` | entrada | binária | atendimento/help desk | últimos 90 dias | calculada | médio | indica reincidência de problema semelhante em atendimentos recentes |
| `avg_resolution_hours_90d` | entrada | numérica | atendimento/help desk | últimos 90 dias | calculada | médio | tempo médio de resolução dos chamados encerrados no período |
| `outage_count_30d` | entrada | inteiro | monitoramento/NOC | últimos 30 dias | calculada | baixo | quantidade de eventos de indisponibilidade associados ao cliente ou à sua área de atendimento |
| `network_outage_hours_30d` | entrada | numérica | monitoramento/NOC | últimos 30 dias | calculada | baixo | horas acumuladas de indisponibilidade no período |
| `churn_90d` | alvo | binária | rotulagem sintética | próximos 90 dias | gerada diretamente | alto | indica cancelamento voluntário definitivo solicitado pelo cliente nos 90 dias posteriores à data de referência |

## Grupos de variáveis

### Cadastro e contrato

- `tenure_months`
- `access_technology`
- `download_speed_mbps`
- `monthly_fee`
- `has_contract_loyalty`

Esse grupo descreve a relação comercial do cliente com o provedor e ajuda a capturar estágio de relacionamento, tecnologia contratada, preço e barreiras de saída.

### Financeiro

- `overdue_invoice_count`
- `oldest_overdue_days`
- `active_agreement_installment_amount`
- `had_price_adjustment_90d`

Esse bloco representa faturas vencidas e ainda não pagas, atraso acumulado, acordos ativos e possível sensibilidade a reajuste. O canal de pagamento não entra como variável da V1 porque boleto e Pix são formas de quitação de cada cobrança e podem variar ao longo do relacionamento.

Um acordo ativo não deve ser interpretado automaticamente como sinal negativo. Ele pode representar dificuldade financeira anterior, mas também uma tentativa de permanência e regularização.

Nesse desenho, `overdue_invoice_count = 0` implica `oldest_overdue_days = 0`, e `oldest_overdue_days > 0` implica `overdue_invoice_count > 0`. Clientes com acordo ativo podem ter `overdue_invoice_count = 0`, pois dívidas anteriores podem ter sido renegociadas.

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
- `churn_90d = 1` representa somente encerramento definitivo solicitado voluntariamente pelo cliente.
- `churn_90d = 0` inclui clientes ativos, bloqueio temporário, suspensão temporária, inadimplência sem cancelamento voluntário, renegociação financeira, alteração de plano e encerramento administrativo exclusivamente por inadimplência.
- Não incluir status de cancelamento em andamento, pedido de desligamento, motivo de cancelamento ou qualquer artefato administrativo de saída como variável de entrada.
- Não incluir no dataset qualquer score interno usado para gerar `churn_90d`.
- Evitar variáveis compostas que repliquem diretamente a lógica de rotulagem.
- Inadimplência e acordo financeiro podem influenciar moderadamente o risco de cancelamento voluntário, mas não devem determinar o alvo.
- Se houver múltiplos snapshots por cliente em versões futuras, a separação entre treino e teste não deve ser aleatória sem controle temporal ou por cliente.

## Possibilidade para versões futuras

- `region_competition_level`: variável útil para representar pressão competitiva regional, mas que provavelmente dependeria de fonte comercial externa e pode não estar disponível de forma estruturada em uma primeira aplicação real.
- `involuntary_churn_90d` ou `default_risk_90d`: possíveis alvos futuros para encerramento administrativo por inadimplência ou risco de inadimplência.
