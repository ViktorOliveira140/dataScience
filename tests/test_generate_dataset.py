from pathlib import Path

import pandas as pd
import pytest

from src.generate_dataset import COLUMNS, generate_dataset, save_dataset, validate_dataset


def test_generate_dataset_is_reproducible_with_same_seed() -> None:
    first = generate_dataset(n_customers=200, seed=42)
    second = generate_dataset(n_customers=200, seed=42)

    pd.testing.assert_frame_equal(first, second)


def test_generate_dataset_changes_with_different_seed() -> None:
    first = generate_dataset(n_customers=200, seed=42)
    second = generate_dataset(n_customers=200, seed=43)

    assert not first.equals(second)


def test_dataset_has_expected_columns_and_rows() -> None:
    dataset = generate_dataset(n_customers=300, seed=42)

    assert list(dataset.columns) == COLUMNS
    assert len(dataset) == 300
    assert dataset["customer_id"].is_unique


def test_dataset_has_valid_categories_and_no_nulls() -> None:
    dataset = generate_dataset(n_customers=300, seed=42)

    assert not dataset.isna().any().any()
    assert set(dataset["access_technology"]).issubset({"fiber", "radio"})
    assert set(dataset["churn_90d"]).issubset({0, 1})


def test_financial_support_and_network_rules_are_consistent() -> None:
    dataset = generate_dataset(n_customers=500, seed=42)

    assert (dataset.loc[dataset["overdue_invoice_count"] == 0, "oldest_overdue_days"] == 0).all()
    assert (dataset.loc[dataset["oldest_overdue_days"] > 0, "overdue_invoice_count"] > 0).all()
    assert (
        dataset.loc[dataset["support_tickets_90d"] == 0, "avg_resolution_hours_90d"] == 0
    ).all()
    assert (dataset.loc[dataset["support_tickets_90d"] == 0, "repeat_issue_90d"] == 0).all()
    assert (
        dataset.loc[dataset["outage_count_30d"] == 0, "network_outage_hours_30d"] == 0
    ).all()


def test_financial_process_allows_realistic_agreement_cases() -> None:
    dataset = generate_dataset(n_customers=5_000, seed=42)
    has_agreement = dataset["active_agreement_installment_amount"] > 0

    assert has_agreement.any()
    assert ((has_agreement) & (dataset["overdue_invoice_count"] == 0)).any()
    assert (dataset["oldest_overdue_days"] > 60).any()


def test_validate_dataset_rejects_wrong_columns() -> None:
    dataset = generate_dataset(n_customers=20, seed=42).drop(columns=["churn_90d"])

    with pytest.raises(ValueError, match="columns"):
        validate_dataset(dataset, expected_rows=20)


def test_churn_rate_stays_in_plausible_range() -> None:
    dataset = generate_dataset(n_customers=5_000, seed=42)
    churn_rate = dataset["churn_90d"].mean()

    assert 0.08 <= churn_rate <= 0.15


def test_dataset_is_saved_to_requested_path(tmp_path: Path) -> None:
    output = tmp_path / "data" / "customers_churn_synthetic.csv"
    dataset = generate_dataset(n_customers=50, seed=42)

    save_dataset(dataset, output)

    saved = pd.read_csv(output)
    assert output.exists()
    assert list(saved.columns) == COLUMNS
    assert len(saved) == 50
