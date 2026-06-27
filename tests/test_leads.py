from __future__ import annotations

from telegram_business_bot.leads import LeadStore, parse_lead_command


def test_parse_lead_command() -> None:
    lead = parse_lead_command("/lead Alice | alice@example.com | Need a quote")

    assert lead.name == "Alice"
    assert lead.email == "alice@example.com"
    assert lead.message == "Need a quote"


def test_lead_store_appends_and_reads_rows(tmp_path) -> None:
    store = LeadStore(tmp_path / "leads.csv")
    lead = parse_lead_command("/lead Alice | alice@example.com | Need a quote")

    store.append(lead)
    rows = store.read_all()

    assert rows[0]["name"] == "Alice"
    assert rows[0]["email"] == "alice@example.com"


def test_lead_store_summary(tmp_path) -> None:
    store = LeadStore(tmp_path / "leads.csv")
    lead = parse_lead_command("/lead Alice | alice@example.com | Need a quote")

    store.append(lead)
    summary = store.summary()

    assert summary.rows == 1
    assert summary.path == tmp_path / "leads.csv"
    assert summary.latest_created_at is not None


def test_parse_lead_command_rejects_invalid_email() -> None:
    try:
        parse_lead_command("/lead Alice | not-email | Need a quote")
    except ValueError as exc:
        assert "Lead is invalid" in str(exc)
    else:
        raise AssertionError("Expected invalid lead to raise ValueError")
