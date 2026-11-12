"""Database seeding service for CONTINUUM synthetic dataset."""

from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

# Ensure repository root is importable for data.generator
ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.models.entities import (
    Advisor,
    AdvisorAssignment,
    AdvisorTeam,
    Client,
    ClientAccount,
    ClientInteraction,
    ClientStatusEvent,
    Complaint,
    Experiment,
    FollowUpTask,
    JourneyEvent,
    JourneyStageEpisode,
    MetricDefinition,
    ProcessChange,
    Recommendation,
    ServiceCase,
    ServiceCaseEvent,
    SlaPolicy,
)
from data.generator.generate_data import generate_synthetic_dataset

TABLES_TRUNCATE_ORDER = [
    "experiments",
    "recommendations",
    "investigations",
    "metric_definitions",
    "client_status_events",
    "follow_up_tasks",
    "client_interactions",
    "complaints",
    "service_case_events",
    "service_cases",
    "journey_events",
    "journey_stage_episodes",
    "client_accounts",
    "advisor_assignments",
    "clients",
    "process_changes",
    "sla_policies",
    "advisors",
    "advisor_teams",
]


def _chunked_insert(db: Session, model: type, rows: list[dict], chunk_size: int = 5000) -> None:
    if not rows:
        return
    for i in range(0, len(rows), chunk_size):
        db.execute(model.__table__.insert(), rows[i : i + chunk_size])


def seed_database(seed: int | None = None, scale: str | None = None) -> dict[str, int]:
    settings = get_settings()
    use_seed = seed if seed is not None else settings.DATA_SEED
    use_scale = scale if scale is not None else settings.DATASET_SCALE

    dataset = generate_synthetic_dataset(seed=use_seed, scale=use_scale)

    db = SessionLocal()
    try:
        # Truncate in dependency order
        db.execute(
            text(f"TRUNCATE TABLE {', '.join(TABLES_TRUNCATE_ORDER)} RESTART IDENTITY CASCADE")
        )
        db.commit()

        _chunked_insert(db, AdvisorTeam, dataset.teams)
        _chunked_insert(db, Advisor, dataset.advisors)
        _chunked_insert(db, SlaPolicy, dataset.sla_policies)
        _chunked_insert(db, ProcessChange, dataset.process_changes)
        _chunked_insert(db, Client, dataset.clients)
        _chunked_insert(db, AdvisorAssignment, dataset.advisor_assignments)
        _chunked_insert(db, ClientAccount, dataset.client_accounts)
        _chunked_insert(db, JourneyStageEpisode, dataset.journey_stage_episodes)
        _chunked_insert(db, JourneyEvent, dataset.journey_events)
        _chunked_insert(db, ServiceCase, dataset.service_cases)
        _chunked_insert(db, ServiceCaseEvent, dataset.service_case_events)
        _chunked_insert(db, Complaint, dataset.complaints)
        _chunked_insert(db, ClientInteraction, dataset.client_interactions)
        _chunked_insert(db, FollowUpTask, dataset.follow_up_tasks)
        _chunked_insert(db, ClientStatusEvent, dataset.client_status_events)
        _chunked_insert(db, Recommendation, dataset.recommendations)
        _chunked_insert(db, Experiment, dataset.experiments)
        _chunked_insert(db, MetricDefinition, dataset.metric_definitions)

        db.commit()

        return {
            "teams": len(dataset.teams),
            "advisors": len(dataset.advisors),
            "clients": len(dataset.clients),
            "journey_stage_episodes": len(dataset.journey_stage_episodes),
            "journey_events": len(dataset.journey_events),
            "service_cases": len(dataset.service_cases),
            "complaints": len(dataset.complaints),
            "client_interactions": len(dataset.client_interactions),
            "follow_up_tasks": len(dataset.follow_up_tasks),
            "recommendations": len(dataset.recommendations),
            "metric_definitions": len(dataset.metric_definitions),
        }
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
