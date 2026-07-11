# Churn em Telecom com Dados Sintéticos

Criei este projeto para montar uma demonstração simples de ciência de dados voltada ao contexto de um provedor de internet.

A ideia é explorar uma pergunta prática: quais sinais operacionais e financeiros podem ajudar a identificar clientes com maior risco de cancelar o serviço nos próximos 90 dias.

O foco aqui não é construir algo grande ou sofisticado logo de início. A prioridade é organizar um projeto enxuto, legível e fácil de explicar para áreas de negócio, principalmente atendimento, suporte, financeiro e retenção.

Como este trabalho começou sem uso de bases internas, a primeira versão utiliza apenas dados sintéticos. Isso permite estruturar o problema, testar hipóteses e desenhar uma abordagem inicial sem expor informações reais de clientes.

Cada linha do dataset representa a situação de um cliente em uma data de referência. A variável-alvo da primeira versão é `churn_90d`, que indica se houve cancelamento nos 90 dias seguintes.

A base foi pensada para refletir sinais que costumam existir em sistemas comuns de operação, como:

- cadastro e contrato;
- faturamento;
- atendimento;
- indicadores simples de rede.

O objetivo desta fase é preparar uma base sintética plausível, um dicionário de dados claro e a estrutura inicial do projeto. A partir disso, o próximo passo será analisar o comportamento da carteira, construir um baseline interpretável e avaliar se os sinais escolhidos ajudam de fato a separar perfis de maior e menor risco.

## Limites desta versão

Os dados deste repositório são sintéticos. Eles não representam clientes reais, não devem ser tratados como evidência de desempenho em produção e não substituem uma validação futura com dados internos, critérios de governança e recorte temporal adequado.

Além disso, este projeto não parte da premissa de que correlação significa causalidade. A proposta é apoiar análise e priorização, não automatizar decisões de retenção de forma isolada.

## Estrutura inicial

A estrutura pública será mantida simples no começo, com documentação objetiva e espaço para evolução gradual do código e das análises.

Na fase seguinte, o projeto deve incorporar:

- geração reproduzível do dataset sintético;
- validações básicas da base;
- análise exploratória;
- modelo baseline interpretável;
- comparação com um segundo modelo;
- uma apresentação simples dos resultados.

## Próximos passos

Os próximos passos previstos são:

1. fechar o dicionário de dados da primeira versão;
2. implementar o gerador sintético com regras reproduzíveis;
3. validar tipos, faixas e consistência da base;
4. realizar a análise exploratória inicial;
5. treinar um baseline simples para estimativa de churn.
