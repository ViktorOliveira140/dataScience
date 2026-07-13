from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


DEFAULT_N_CUSTOMERS = 5_000
DEFAULT_SEED = 42
DEFAULT_OUTPUT = Path("data/customers_churn_synthetic.csv")
OVERDUE_INVOICE_INTERCEPT = -1.6

COLUMNS = [
    "customer_id",
    "tenure_months",
    "access_technology",
    "download_speed_mbps",
    "monthly_fee",
    "has_contract_loyalty",
    "overdue_invoice_count",
    "oldest_overdue_days",
    "active_agreement_installment_amount",
    "had_price_adjustment_90d",
    "support_tickets_90d",
    "repeat_issue_90d",
    "avg_resolution_hours_90d",
    "outage_count_30d",
    "network_outage_hours_30d",
    "churn_90d",
]

ACCESS_TECHNOLOGIES = {"fiber", "radio"}


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-values))


def generate_dataset(n_customers: int = DEFAULT_N_CUSTOMERS, seed: int = DEFAULT_SEED) -> pd.DataFrame:
    if n_customers <= 0:
        raise ValueError("n_customers must be greater than zero")

    rng = np.random.default_rng(seed)

    customer_id = [f"CUST-{i:06d}" for i in range(1, n_customers + 1)]

    tenure_months = np.clip(rng.gamma(shape=2.1, scale=18, size=n_customers).round(), 1, 120).astype(int)

    access_technology = rng.choice(["fiber", "radio"], size=n_customers, p=[0.76, 0.24])
    is_fiber = access_technology == "fiber"

    fiber_speeds = rng.choice([100, 200, 300, 500, 600], size=n_customers, p=[0.18, 0.28, 0.27, 0.19, 0.08])
    radio_speeds = rng.choice([20, 30, 50, 80], size=n_customers, p=[0.22, 0.34, 0.32, 0.12])
    download_speed_mbps = np.where(is_fiber, fiber_speeds, radio_speeds).astype(int)

    monthly_fee = (
        62
        + np.where(is_fiber, 18, 0)
        + download_speed_mbps * np.where(is_fiber, 0.16, 0.48)
        + rng.normal(0, 7, n_customers)
    )
    monthly_fee = np.clip(monthly_fee, 59.9, 219.9).round(2)

    loyalty_probability = sigmoid(
        -0.15
        + 0.55 * is_fiber.astype(int)
        + 0.65 * (tenure_months <= 24).astype(int)
        - 0.45 * (tenure_months > 72).astype(int)
    )
    has_contract_loyalty = rng.binomial(1, loyalty_probability).astype(int)

    financial_pressure = rng.normal(0, 1, n_customers)
    financial_pressure += 0.35 * (has_contract_loyalty == 0)
    financial_pressure += 0.25 * (tenure_months <= 12)

    overdue_invoice_lambda = np.exp(
        OVERDUE_INVOICE_INTERCEPT + 0.7 * financial_pressure + 0.15 * (~is_fiber).astype(int)
    )
    overdue_invoice_count = np.clip(rng.poisson(overdue_invoice_lambda), 0, 8).astype(int)

    oldest_overdue_days = np.zeros(n_customers, dtype=int)
    has_overdue_invoice = overdue_invoice_count > 0
    overdue_base = rng.gamma(shape=1.9, scale=23, size=n_customers)
    overdue_extra = rng.normal(0, 9, n_customers) + (overdue_invoice_count - 1) * rng.uniform(
        14, 28, n_customers
    )
    oldest_overdue_days[has_overdue_invoice] = np.clip(
        overdue_base[has_overdue_invoice] + overdue_extra[has_overdue_invoice],
        1,
        180,
    ).round().astype(int)

    had_prior_default = financial_pressure + rng.normal(0, 0.75, n_customers) > 0.95
    agreement_probability = sigmoid(
        -2.6
        + 1.1 * had_prior_default.astype(int)
        + 0.35 * (oldest_overdue_days > 60).astype(int)
        + 0.25 * (overdue_invoice_count >= 2).astype(int)
    )
    has_active_agreement = rng.binomial(1, agreement_probability).astype(bool)
    active_agreement_installment_amount = np.zeros(n_customers)
    agreement_amount = monthly_fee * rng.uniform(0.18, 0.75, n_customers) + rng.normal(0, 8, n_customers)
    active_agreement_installment_amount[has_active_agreement] = np.clip(
        agreement_amount[has_active_agreement],
        20,
        160,
    )
    active_agreement_installment_amount = active_agreement_installment_amount.round(2)

    adjustment_probability = sigmoid(-2.0 + 0.5 * (tenure_months > 18) + 0.35 * (tenure_months > 48))
    had_price_adjustment_90d = rng.binomial(1, adjustment_probability).astype(int)

    outage_lambda = np.exp(-0.65 + 0.55 * (~is_fiber).astype(int) + rng.normal(0, 0.35, n_customers))
    outage_count_30d = np.clip(rng.poisson(outage_lambda), 0, 8).astype(int)

    network_outage_hours_30d = np.zeros(n_customers)
    has_outage = outage_count_30d > 0
    outage_hours = outage_count_30d * rng.gamma(shape=1.6, scale=1.25, size=n_customers)
    network_outage_hours_30d[has_outage] = np.clip(outage_hours[has_outage], 0.25, 72)
    network_outage_hours_30d = network_outage_hours_30d.round(2)

    ticket_lambda = np.exp(
        -1.15
        + 0.22 * outage_count_30d
        + 0.035 * network_outage_hours_30d
        + 0.22 * (~is_fiber).astype(int)
    )
    support_tickets_90d = np.clip(rng.poisson(ticket_lambda), 0, 6).astype(int)

    repeat_issue_probability = sigmoid(
        -3.0
        + 0.85 * (support_tickets_90d >= 2).astype(int)
        + 0.45 * (support_tickets_90d >= 3).astype(int)
        + 0.35 * (outage_count_30d >= 3).astype(int)
    )
    repeat_issue_90d = rng.binomial(1, repeat_issue_probability).astype(int)
    repeat_issue_90d = np.where(support_tickets_90d == 0, 0, repeat_issue_90d).astype(int)

    avg_resolution_hours_90d = np.zeros(n_customers)
    has_ticket = support_tickets_90d > 0
    resolution_hours = (
        rng.gamma(shape=2.2, scale=9.0, size=n_customers)
        + 6 * repeat_issue_90d
        + 1.7 * support_tickets_90d
        + 0.25 * network_outage_hours_30d
    )
    avg_resolution_hours_90d[has_ticket] = np.clip(resolution_hours[has_ticket], 1, 120)
    avg_resolution_hours_90d = avg_resolution_hours_90d.round(2)

    churn_logit = (
        -3.00
        + 0.45 * (tenure_months <= 12).astype(int)
        + 0.35 * (has_contract_loyalty == 0).astype(int)
        + 0.42 * had_price_adjustment_90d
        + 0.18 * np.minimum(overdue_invoice_count, 4)
        + 0.0025 * np.minimum(oldest_overdue_days, 150)
        - 0.15 * (active_agreement_installment_amount > 0).astype(int)
        + 0.26 * support_tickets_90d
        + 0.55 * repeat_issue_90d
        + 0.004 * avg_resolution_hours_90d
        + 0.13 * outage_count_30d
        + 0.012 * np.minimum(network_outage_hours_30d, 48)
        + 0.32 * ((support_tickets_90d >= 2) & (repeat_issue_90d == 1)).astype(int)
        + 0.28 * ((outage_count_30d >= 3) & (has_contract_loyalty == 0)).astype(int)
        + 0.18 * ((had_price_adjustment_90d == 1) & (overdue_invoice_count >= 2)).astype(int)
        + rng.normal(0, 0.65, n_customers)
    )
    churn_probability = np.clip(sigmoid(churn_logit), 0.02, 0.68)
    churn_90d = rng.binomial(1, churn_probability).astype(int)

    dataset = pd.DataFrame(
        {
            "customer_id": customer_id,
            "tenure_months": tenure_months,
            "access_technology": access_technology,
            "download_speed_mbps": download_speed_mbps,
            "monthly_fee": monthly_fee,
            "has_contract_loyalty": has_contract_loyalty,
            "overdue_invoice_count": overdue_invoice_count,
            "oldest_overdue_days": oldest_overdue_days,
            "active_agreement_installment_amount": active_agreement_installment_amount,
            "had_price_adjustment_90d": had_price_adjustment_90d,
            "support_tickets_90d": support_tickets_90d,
            "repeat_issue_90d": repeat_issue_90d,
            "avg_resolution_hours_90d": avg_resolution_hours_90d,
            "outage_count_30d": outage_count_30d,
            "network_outage_hours_30d": network_outage_hours_30d,
            "churn_90d": churn_90d,
        },
        columns=COLUMNS,
    )

    validate_dataset(dataset, expected_rows=n_customers)
    return dataset


def validate_dataset(dataset: pd.DataFrame, expected_rows: int | None = None) -> None:
    if list(dataset.columns) != COLUMNS:
        raise ValueError("dataset columns do not match the V1 data dictionary")

    if expected_rows is not None and len(dataset) != expected_rows:
        raise ValueError("dataset row count does not match the requested size")

    if dataset.isna().any().any():
        raise ValueError("dataset contains null values")

    if not dataset["customer_id"].is_unique:
        raise ValueError("customer_id values must be unique")

    if not dataset["access_technology"].isin(ACCESS_TECHNOLOGIES).all():
        raise ValueError("access_technology contains invalid values")

    numeric_ranges = {
        "tenure_months": (1, 120),
        "download_speed_mbps": (20, 600),
        "monthly_fee": (59.9, 219.9),
        "overdue_invoice_count": (0, 8),
        "oldest_overdue_days": (0, 180),
        "active_agreement_installment_amount": (0, 160),
        "had_price_adjustment_90d": (0, 1),
        "support_tickets_90d": (0, 6),
        "repeat_issue_90d": (0, 1),
        "avg_resolution_hours_90d": (0, 120),
        "outage_count_30d": (0, 8),
        "network_outage_hours_30d": (0, 72),
        "churn_90d": (0, 1),
    }
    for column, (minimum, maximum) in numeric_ranges.items():
        if not dataset[column].between(minimum, maximum).all():
            raise ValueError(f"{column} contains values outside the expected range")

    integer_columns = [
        "tenure_months",
        "download_speed_mbps",
        "has_contract_loyalty",
        "overdue_invoice_count",
        "oldest_overdue_days",
        "had_price_adjustment_90d",
        "support_tickets_90d",
        "repeat_issue_90d",
        "outage_count_30d",
        "churn_90d",
    ]
    for column in integer_columns:
        if not pd.api.types.is_integer_dtype(dataset[column]):
            raise ValueError(f"{column} must be an integer column")

    binary_columns = ["has_contract_loyalty", "had_price_adjustment_90d", "repeat_issue_90d", "churn_90d"]
    for column in binary_columns:
        if not dataset[column].isin([0, 1]).all():
            raise ValueError(f"{column} must contain only 0 and 1")

    if not (dataset.loc[dataset["overdue_invoice_count"] == 0, "oldest_overdue_days"] == 0).all():
        raise ValueError("oldest_overdue_days must be zero when overdue_invoice_count is zero")

    if not (dataset.loc[dataset["oldest_overdue_days"] > 0, "overdue_invoice_count"] > 0).all():
        raise ValueError("overdue_invoice_count must be greater than zero when oldest_overdue_days is positive")

    if not (dataset.loc[dataset["support_tickets_90d"] == 0, "avg_resolution_hours_90d"] == 0).all():
        raise ValueError("avg_resolution_hours_90d must be zero when support_tickets_90d is zero")

    if not (dataset.loc[dataset["support_tickets_90d"] == 0, "repeat_issue_90d"] == 0).all():
        raise ValueError("repeat_issue_90d must be zero when support_tickets_90d is zero")

    if not (dataset.loc[dataset["outage_count_30d"] == 0, "network_outage_hours_30d"] == 0).all():
        raise ValueError("network_outage_hours_30d must be zero when outage_count_30d is zero")


def save_dataset(dataset: pd.DataFrame, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(output, index=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gera o dataset sintético de churn voluntário.")
    parser.add_argument("--n-customers", type=int, default=DEFAULT_N_CUSTOMERS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dataset = generate_dataset(n_customers=args.n_customers, seed=args.seed)
    save_dataset(dataset, args.output)
    churn_rate = dataset["churn_90d"].mean()
    print(f"Dataset salvo em {args.output}")
    print(f"Linhas: {len(dataset)}")
    print(f"Taxa de churn voluntario: {churn_rate:.2%}")


if __name__ == "__main__":
    main()
