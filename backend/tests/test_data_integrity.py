"""Automated data integrity and planted-story verification tests."""

from datetime import datetime, timezone

import pytest
from sqlalchemy import text

from app.analytics.business_hours import add_business_hours, elapsed_business_hours
from app.core.database import SessionLocal
from data.generator.generate_data import AS_OF_DATE, generate_synthetic_dataset


@pytest.fixture(scope="module")
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_business_hours_calendar():
    # Friday 16:00 ET (20:00 UTC in EDT) + 2 business hours -> Monday 10:00 ET
    friday_utc = datetime(2026, 10, 23, 20, 0, 0, tzinfo=timezone.utc)
    due = add_business_hours(friday_utc, 2.0)
    assert due.weekday() == 0  # Monday
    elapsed = elapsed_business_hours(friday_utc, due)
    assert abs(elapsed - 2.0) < 0.05


def test_seed_reproducibility():
    d1 = generate_synthetic_dataset(seed=20270101, scale="compact")
    d2 = generate_synthetic_dataset(seed=20270101, scale="compact")
    assert len(d1.clients) == len(d2.clients) == 2400
    assert d1.clients[0] == d2.clients[0]
    assert len(d1.service_cases) == len(d2.service_cases)


def test_database_record_counts(db):
    clients_cnt = db.execute(text("SELECT COUNT(*) FROM clients")).scalar()
    advisors_cnt = db.execute(text("SELECT COUNT(*) FROM advisors")).scalar()
    teams_cnt = db.execute(text("SELECT COUNT(*) FROM advisor_teams")).scalar()
    cases_cnt = db.execute(text("SELECT COUNT(*) FROM service_cases")).scalar()
    assert teams_cnt == 8
    assert advisors_cnt == 48
    assert clients_cnt >= 2400
    assert cases_cnt >= 10000


def test_chronology_and_timestamp_validity(db):
    bad_exits = db.execute(
        text("SELECT COUNT(*) FROM clients WHERE exited_at IS NOT NULL AND (activated_at IS NULL OR exited_at < activated_at)")
    ).scalar()
    assert bad_exits == 0

    future_exits = db.execute(
        text("SELECT COUNT(*) FROM clients WHERE exited_at > :as_of"),
        {"as_of": AS_OF_DATE},
    ).scalar()
    assert future_exits == 0

    bad_responses = db.execute(
        text("SELECT COUNT(*) FROM service_cases WHERE first_response_at IS NOT NULL AND first_response_at < created_at")
    ).scalar()
    assert bad_responses == 0

    bad_resolutions = db.execute(
        text("SELECT COUNT(*) FROM service_cases WHERE resolved_at IS NOT NULL AND resolved_at < created_at")
    ).scalar()
    assert bad_resolutions == 0

    # Open cases not yet due must not be marked breached
    premature_breach = db.execute(
        text(
            "SELECT COUNT(*) FROM service_cases WHERE first_response_at IS NULL AND first_response_due_at > :as_of AND first_response_breached = TRUE"
        ),
        {"as_of": AS_OF_DATE},
    ).scalar()
    assert premature_breach == 0


def test_planted_story_a_kyc_rework(db):
    row = db.execute(
        text(
            """
            SELECT
                COUNT(*) FILTER (WHERE entered_at < '2026-04-01' AND outcome = 'Reopened')::float
                    / NULLIF(COUNT(*) FILTER (WHERE entered_at < '2026-04-01' AND previous_episode_id IS NULL), 0) AS pre_rework,
                COUNT(*) FILTER (WHERE entered_at >= '2026-04-01' AND outcome = 'Reopened')::float
                    / NULLIF(COUNT(*) FILTER (WHERE entered_at >= '2026-04-01' AND previous_episode_id IS NULL), 0) AS post_rework
            FROM journey_stage_episodes
            WHERE stage = 'KYC'
            """
        )
    ).mappings().one()
    assert row["post_rework"] > row["pre_rework"] + 0.10


def test_planted_story_b_t3_capacity_pressure(db):
    row = db.execute(
        text(
            """
            SELECT
                COUNT(*) FILTER (WHERE assigned_team_id = 'T-03' AND status IN ('Open','In Progress'))::float
                    / NULLIF((SELECT SUM(CASE WHEN active THEN max_active_cases ELSE 0 END) FROM advisors WHERE team_id = 'T-03'), 0) AS t3_util,
                COUNT(*) FILTER (WHERE assigned_team_id = 'T-01' AND status IN ('Open','In Progress'))::float
                    / NULLIF((SELECT SUM(CASE WHEN active THEN max_active_cases ELSE 0 END) FROM advisors WHERE team_id = 'T-01'), 0) AS t1_util
            FROM service_cases
            """
        )
    ).mappings().one()
    assert row["t3_util"] > row["t1_util"]


def test_planted_story_e_transfer_complaints(db):
    row = db.execute(
        text(
            """
            SELECT
                COUNT(*) FILTER (WHERE category = 'Transfer & Settlement' AND submitted_at < '2026-06-01')::float
                    / NULLIF(COUNT(*) FILTER (WHERE submitted_at < '2026-06-01'), 0) AS pre_share,
                COUNT(*) FILTER (WHERE category = 'Transfer & Settlement' AND submitted_at >= '2026-06-01')::float
                    / NULLIF(COUNT(*) FILTER (WHERE submitted_at >= '2026-06-01'), 0) AS post_share
            FROM complaints
            """
        )
    ).mappings().one()
    assert row["post_share"] > row["pre_share"]
