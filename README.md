# Churn em Telecom com Dados Sintéticos

Criei este projeto para montar uma demonstração simples de ciência de dados voltada ao contexto de um provedor de internet.

A ideia é explorar uma pergunta prática: quais sinais operacionais e financeiros podem ajudar a identificar clientes com maior risco de cancelar o serviço nos próximos 90 dias.

O foco aqui não é construir algo grande ou sofisticado logo de início. A prioridade é organizar um projeto enxuto, legível e fácil de explicar para áreas de negócio, principalmente atendimento, suporte, financeiro e retenção.

Como este trabalho começou sem uso de bases internas, a primeira versão utiliza apenas dados sintéticos. Isso permite estruturar o problema, testar hipóteses e desenhar uma abordagem inicial sem expor informações reais de clientes.

Cada linha do dataset representa a situação de um cliente em uma data de referência. A variável-alvo da primeira versão é `churn_90d`, que indica se houve cancelamento voluntário nos 90 dias seguintes.

A base foi pensada para refletir sinais que costumam existir em sistemas comuns de operação, como:

- cadastro e contrato;
- faturamento;
- atendimento;
- indicadores simples de rede.

O projeto já conta com uma base sintética plausível, um dicionário de dados claro, uma análise exploratória inicial, um dashboard simples, um baseline interpretável para churn voluntário e uma primeira comparação com modelo baseado em árvores.

## Limites desta versão

Os dados deste repositório são sintéticos. Eles não representam clientes reais, não devem ser tratados como evidência de desempenho em produção e não substituem uma validação futura com dados internos, critérios de governança e recorte temporal adequado.

As proporções usadas no gerador, incluindo a inadimplência simulada, são hipóteses para demonstração. Elas não representam taxas reais da empresa.

Além disso, este projeto não parte da premissa de que correlação significa causalidade. A proposta é apoiar análise e priorização, não automatizar decisões de retenção de forma isolada.

## Estrutura inicial

A estrutura pública será mantida simples no começo, com documentação objetiva e espaço para evolução gradual do código e das análises.

Nesta fase, o projeto já inclui:

- gerador reproduzível do dataset sintético;
- análise exploratória inicial em notebook;
- dashboard inicial em Streamlit;
- modelo baseline com regressão logística;
- comparação inicial com Random Forest.

## Instalação

Crie um ambiente virtual e instale as dependências:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Geração do dataset

O dataset deve ser gerado antes da análise exploratória e do dashboard.

Para gerar o dataset com os padrões da V1, use:

```bash
python src/generate_dataset.py
```

Esse comando cria o arquivo `data/customers_churn_synthetic.csv` com 5.000 clientes e seed 42.

Também é possível informar a quantidade de clientes, a seed e o caminho de saída:

```bash
python src/generate_dataset.py --n-customers 10000 --seed 123 --output data/customers_churn_synthetic.csv
```

O diretório `data/` é usado para arquivos gerados e não deve ser versionado por padrão.

## Análise exploratória

Para abrir o notebook da análise exploratória, use:

```bash
jupyter lab
```

Depois abra o arquivo `notebooks/01_eda.ipynb`.

## Dashboard

Para executar o dashboard inicial, use:

```bash
streamlit run src/app.py
```

O dashboard lê o arquivo `data/customers_churn_synthetic.csv`. Se o dataset ainda não existir, gere-o primeiro com `python src/generate_dataset.py`.

## Modelo baseline

Para abrir o notebook do modelo baseline, use:

```bash
jupyter lab
```

Depois abra o arquivo `notebooks/02_modeling_baseline.ipynb`.

O baseline usa regressão logística e compara o resultado com uma referência ingênua que prevê sempre a classe majoritária. A análise também mostra por que a acurácia isolada é insuficiente para avaliar churn, já que o cancelamento voluntário é um evento minoritário.

## Comparação de modelos

Para abrir o notebook de comparação, use:

```bash
jupyter lab
```

Depois abra o arquivo `notebooks/03_model_comparison.ipynb`.

Essa etapa compara a regressão logística com uma Random Forest. A comparação não define um modelo pronto para produção; ela serve para avaliar trade-offs entre simplicidade, interpretação, falsos positivos, recall e priorização por ranking.

## Validação

O gerador valida a estrutura do dataset antes de salvar o arquivo. As validações cobrem quantidade de linhas, colunas esperadas, tipos, categorias, faixas, ausência de nulos e regras básicas de consistência.

Para executar os testes automatizados:

```bash
pytest
```

## Próximos passos

As próximas etapas previstas são:

- análise dos cenários de priorização;
- uma apresentação simples dos resultados.
