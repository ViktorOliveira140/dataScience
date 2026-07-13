from pathlib import Path

import pandas as pd
import streamlit as st


DATA_PATH = Path("data/customers_churn_synthetic.csv")

COLUMN_LABELS = {
    "customer_id": "ID técnico do cliente",
    "tenure_months": "Tempo como cliente (meses)",
    "access_technology": "Tecnologia de acesso",
    "download_speed_mbps": "Velocidade contratada (Mbps)",
    "monthly_fee": "Mensalidade (R$)",
    "has_contract_loyalty": "Possui fidelidade",
    "overdue_invoice_count": "Faturas vencidas",
    "oldest_overdue_days": "Maior atraso em aberto (dias)",
    "active_agreement_installment_amount": "Parcela de acordo ativa (R$)",
    "had_price_adjustment_90d": "Reajuste nos últimos 90 dias",
    "support_tickets_90d": "Chamados nos últimos 90 dias",
    "repeat_issue_90d": "Problema reincidente",
    "avg_resolution_hours_90d": "Tempo médio de resolução (h)",
    "outage_count_30d": "Eventos de indisponibilidade",
    "network_outage_hours_30d": "Horas de indisponibilidade",
    "churn_90d": "Churn voluntário em 90 dias",
}


@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def add_analysis_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    data = dataframe.copy()

    data["has_active_agreement"] = data["active_agreement_installment_amount"] > 0
    data["support_tickets_band"] = pd.cut(
        data["support_tickets_90d"],
        bins=[-1, 0, 1, 2, 6],
        labels=["0", "1", "2", "3+"],
    )
    data["network_outage_hours_band"] = pd.cut(
        data["network_outage_hours_30d"],
        bins=[-1, 0, 2, 6, 12, 72],
        labels=["0", "0-2", "2-6", "6-12", "12+"],
    )

    return data


def churn_by_group(
    dataframe: pd.DataFrame,
    column: str,
    group_label: str,
    value_labels: dict | None = None,
) -> pd.DataFrame:
    summary = (
        dataframe.groupby(column, observed=True)
        .agg(
            clientes=("customer_id", "count"),
            cancelamentos=("churn_90d", "sum"),
            taxa_churn=("churn_90d", "mean"),
        )
        .sort_index()
        .reset_index()
    )

    if value_labels:
        summary[column] = summary[column].map(value_labels)

    summary = summary.rename(
        columns={
            column: group_label,
            "clientes": "Clientes",
            "cancelamentos": "Cancelamentos",
            "taxa_churn": "Taxa de churn (%)",
        }
    )
    summary["Taxa de churn (%)"] = summary["Taxa de churn (%)"].mul(100).round(2)

    return summary


def show_churn_section(
    title: str,
    dataframe: pd.DataFrame,
    column: str,
    group_label: str,
    value_labels: dict | None = None,
) -> None:
    st.subheader(title)
    summary = churn_by_group(dataframe, column, group_label, value_labels)
    st.bar_chart(summary, x=group_label, y="Taxa de churn (%)")
    st.dataframe(summary, width="stretch", hide_index=True)


st.set_page_config(
    page_title="Churn em Telecom",
    layout="wide",
)

st.title("Churn em Telecom com Dados Sintéticos")

st.write(
    "Dashboard para explorar sinais associados ao churn voluntário em clientes "
    "de um provedor de internet."
)

st.info(
    "Os dados são sintéticos e não representam taxas reais da empresa. "
    "As diferenças apresentadas indicam associação, não causalidade."
)

df = add_analysis_columns(load_data(DATA_PATH))

total_customers = len(df)
churn_rate = df["churn_90d"].mean()
overdue_rate = (df["overdue_invoice_count"] > 0).mean()
agreement_rate = df["has_active_agreement"].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Clientes", f"{total_customers:,}".replace(",", "."))
col2.metric("Churn voluntário", f"{churn_rate:.2%}")
col3.metric("Com fatura vencida", f"{overdue_rate:.2%}")
col4.metric("Com acordo ativo", f"{agreement_rate:.2%}")

st.divider()

st.header("Principais Comparações")

show_churn_section(
    "Churn por tecnologia de acesso",
    df,
    "access_technology",
    "Tecnologia de acesso",
    {"fiber": "Fibra", "radio": "Rádio"},
)

col1, col2 = st.columns(2)

with col1:
    show_churn_section(
        "Churn por fidelidade",
        df,
        "has_contract_loyalty",
        "Fidelidade",
        {0: "Sem fidelidade", 1: "Com fidelidade"},
    )

with col2:
    show_churn_section(
        "Churn por reajuste recente",
        df,
        "had_price_adjustment_90d",
        "Reajuste recente",
        {0: "Sem reajuste", 1: "Com reajuste"},
    )

col1, col2 = st.columns(2)

with col1:
    show_churn_section(
        "Churn por chamados de suporte",
        df,
        "support_tickets_band",
        "Chamados nos últimos 90 dias",
    )

with col2:
    show_churn_section(
        "Churn por horas de indisponibilidade",
        df,
        "network_outage_hours_band",
        "Horas de indisponibilidade",
    )

col1, col2 = st.columns(2)

with col1:
    show_churn_section(
        "Churn por faturas vencidas",
        df,
        "overdue_invoice_count",
        "Faturas vencidas",
    )

with col2:
    show_churn_section(
        "Churn por acordo ativo",
        df,
        "has_active_agreement",
        "Acordo ativo",
        {False: "Sem acordo", True: "Com acordo"},
    )

st.divider()

st.header("Prévia da Base")

preview = df.drop(
    columns=[
        "has_active_agreement",
        "support_tickets_band",
        "network_outage_hours_band",
    ]
).rename(columns=COLUMN_LABELS)

st.dataframe(preview.head(), width="stretch", hide_index=True)
st.caption(f"Linhas: {df.shape[0]} | Colunas originais: 16")
