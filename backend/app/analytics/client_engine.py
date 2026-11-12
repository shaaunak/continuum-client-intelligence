"""Client explorer, journey timeline reconstruction, and deterministic risk-status engine."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings


def _as_of_dt() -> datetime:
    settings = get_settings()
    return datetime.fromisoformat(f"{settings.AS_OF_DATE}T23:59:59+00:00")


def list_clients(
    db: Session,
    search: str | None = None,
    segment: str | None = None,
    asset_tier: str | None = None,
    lifecycle_status: str | None = None,
    engagement_status: str | None = None,
    team_id: str | None = None,
    page: int = 1,
    page_size: int = 25,
) -> dict[str, Any]:
    as_of = _as_of_dt()
    clauses = ["1=1"]
    params: dict[str, Any] = {"as_of": as_of, "limit": page_size, "offset": (page - 1) * page_size}

    if search:
        clauses.append("c.client_id ILIKE :search")
        params["search"] = f"%{search.strip()}%"
    if segment and segment != "All":
        clauses.append("c.segment = :segment")
        params["segment"] = segment
    if asset_tier and asset_tier != "All":
        clauses.append("c.asset_tier = :asset_tier")
        params["asset_tier"] = asset_tier
    if lifecycle_status and lifecycle_status != "All":
        clauses.append("c.lifecycle_status = :lifecycle_status")
        params["lifecycle_status"] = lifecycle_status
    if team_id and team_id != "All":
        clauses.append("aa.team_id = :team_id")
        params["team_id"] = team_id

    having_clauses = []
    if engagement_status and engagement_status != "All":
        having_clauses.append("eng_status = :eng_status")
        params["eng_status"] = engagement_status

    where_sql = " AND ".join(clauses)
    outer_where = ("WHERE " + " AND ".join(having_clauses)) if having_clauses else ""

    base_cte = f"""
        WITH client_base AS (
            SELECT
                c.client_id,
                c.segment,
                c.asset_tier,
                c.region,
                c.lifecycle_status,
                c.prospect_created_at,
                c.activated_at,
                c.exited_at,
                c.aum_usd,
                a.advisor_id,
                a.display_name AS advisor_name,
                t.team_id,
                t.team_name,
                (
                    SELECT EXTRACT(DAY FROM (:as_of - MAX(ci.occurred_at)))::int
                    FROM client_interactions ci
                    WHERE ci.client_id = c.client_id AND ci.qualifying_engagement = TRUE
                ) AS days_since_contact,
                (
                    SELECT COUNT(*)::int
                    FROM service_cases sc
                    WHERE sc.client_id = c.client_id AND sc.status IN ('Open', 'In Progress')
                ) AS open_cases,
                (
                    SELECT COUNT(*)::int
                    FROM service_cases sc
                    WHERE sc.client_id = c.client_id
                      AND c.activated_at IS NOT NULL
                      AND sc.created_at <= c.activated_at + INTERVAL '90 days'
                      AND sc.first_response_breached = TRUE
                ) AS early_sla_breaches
            FROM clients c
            LEFT JOIN advisor_assignments aa ON aa.client_id = c.client_id AND aa.is_primary = TRUE
            LEFT JOIN advisors a ON a.advisor_id = aa.advisor_id
            LEFT JOIN advisor_teams t ON t.team_id = aa.team_id
            WHERE {where_sql}
        ),
        enriched AS (
            SELECT
                *,
                CASE
                    WHEN lifecycle_status IN ('Exited', 'Abandoned') THEN lifecycle_status
                    WHEN lifecycle_status IN ('Prospect', 'Onboarding') THEN 'Onboarding'
                    WHEN early_sla_breaches >= 2 THEN 'At Risk'
                    WHEN days_since_contact IS NOT NULL AND days_since_contact > 90 THEN 'Inactive'
                    ELSE 'Engaged'
                END AS eng_status
            FROM client_base
        )
    """

    total = db.execute(text(f"{base_cte} SELECT COUNT(*) FROM enriched {outer_where}"), params).scalar() or 0
    rows = db.execute(
        text(
            f"""
            {base_cte}
            SELECT * FROM enriched
            {outer_where}
            ORDER BY
                CASE WHEN eng_status = 'At Risk' THEN 0 WHEN eng_status = 'Inactive' THEN 1 ELSE 2 END,
                early_sla_breaches DESC,
                client_id ASC
            LIMIT :limit OFFSET :offset
            """
        ),
        params,
    ).mappings().all()

    return {
        "total": int(total),
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "client_id": r["client_id"],
                "segment": r["segment"],
                "asset_tier": r["asset_tier"],
                "region": r["region"],
                "advisor_id": r["advisor_id"],
                "advisor_name": r["advisor_name"],
                "team_id": r["team_id"],
                "team_name": r["team_name"],
                "lifecycle_status": r["lifecycle_status"],
                "engagement_status": r["eng_status"],
                "days_since_last_contact": r["days_since_contact"],
                "open_cases": int(r["open_cases"] or 0),
                "early_sla_breaches": int(r["early_sla_breaches"] or 0),
                "aum_usd": float(r["aum_usd"] or 0.0),
            }
            for r in rows
        ],
    }


def get_client_journey_detail(db: Session, client_id: str) -> dict[str, Any] | None:
    as_of = _as_of_dt()
    client = db.execute(
        text(
            """
            SELECT
                c.*,
                a.advisor_id,
                a.display_name AS advisor_name,
                t.team_id,
                t.team_name
            FROM clients c
            LEFT JOIN advisor_assignments aa ON aa.client_id = c.client_id AND aa.is_primary = TRUE
            LEFT JOIN advisors a ON a.advisor_id = aa.advisor_id
            LEFT JOIN advisor_teams t ON t.team_id = aa.team_id
            WHERE c.client_id = :cid
            """
        ),
        {"cid": client_id},
    ).mappings().first()

    if not client:
        return None

    episodes = db.execute(
        text(
            """
            SELECT episode_id, stage, entered_at, exited_at, outcome, rework_reason, previous_episode_id
            FROM journey_stage_episodes
            WHERE client_id = :cid
            ORDER BY entered_at ASC
            """
        ),
        {"cid": client_id},
    ).mappings().all()

    events = db.execute(
        text(
            """
            SELECT event_id, episode_id, event_type, event_timestamp, actor_type, actor_id, summary, metadata_json
            FROM journey_events
            WHERE client_id = :cid
            ORDER BY event_timestamp ASC
            """
        ),
        {"cid": client_id},
    ).mappings().all()

    cases = db.execute(
        text(
            """
            SELECT case_id, request_category, complexity_level, status, created_at,
                   first_response_at, first_response_due_at, first_response_breached,
                   resolved_at, reopen_count, repeat_contact_count
            FROM service_cases
            WHERE client_id = :cid
            ORDER BY created_at ASC
            """
        ),
        {"cid": client_id},
    ).mappings().all()

    complaints = db.execute(
        text(
            """
            SELECT complaint_id, case_id, category, severity, submitted_at, resolved_at, reopened, root_cause_process
            FROM complaints
            WHERE client_id = :cid
            ORDER BY submitted_at ASC
            """
        ),
        {"cid": client_id},
    ).mappings().all()

    last_contact_row = db.execute(
        text(
            """
            SELECT MAX(occurred_at) AS last_contact
            FROM client_interactions
            WHERE client_id = :cid AND qualifying_engagement = TRUE
            """
        ),
        {"cid": client_id},
    ).mappings().first()

    last_contact = last_contact_row["last_contact"] if last_contact_row else None
    days_since_contact = int((as_of - last_contact).days) if last_contact else None

    activated_at = client["activated_at"]
    early_breaches = sum(
        1
        for sc in cases
        if activated_at is not None
        and (sc["created_at"] - activated_at).total_seconds() <= 90 * 86400
        and sc["first_response_breached"]
    )
    open_cases = sum(1 for sc in cases if sc["status"] in ("Open", "In Progress"))
    rework_cycles = sum(1 for ep in episodes if ep["outcome"] == "Reopened")

    # Deterministic, transparent risk rule
    risk_rules_triggered = []
    if early_breaches >= 2:
        risk_rules_triggered.append(f"Rule R1: {early_breaches} early SLA breaches in first 90 days (>=2 threshold)")
    if days_since_contact is not None and days_since_contact > 90 and client["lifecycle_status"] == "Active":
        risk_rules_triggered.append(f"Rule R2: {days_since_contact} days since last qualifying engagement (>90d threshold)")
    if len(complaints) > 0 and any(cmp["reopened"] for cmp in complaints):
        risk_rules_triggered.append("Rule R3: Reopened formal complaint on record")

    if client["lifecycle_status"] in ("Exited", "Abandoned"):
        engagement_status = client["lifecycle_status"]
    elif client["lifecycle_status"] in ("Prospect", "Onboarding"):
        engagement_status = "Onboarding"
    elif early_breaches >= 2 or len(risk_rules_triggered) >= 2:
        engagement_status = "At Risk"
    elif days_since_contact is not None and days_since_contact > 90:
        engagement_status = "Inactive"
    else:
        engagement_status = "Engaged"

    # Build unified chronological timeline
    timeline = []
    for ev in events:
        timeline.append(
            {
                "id": ev["event_id"],
                "timestamp": ev["event_timestamp"].isoformat(),
                "category": "lifecycle",
                "title": ev["event_type"],
                "summary": ev["summary"],
                "actor": f"{ev['actor_type']} ({ev['actor_id']})",
                "severity": "warning" if "returned" in ev["event_type"].lower() else ("risk" if "exited" in ev["event_type"].lower() or "complaint" in ev["event_type"].lower() else "normal"),
            }
        )
    for sc in cases:
        timeline.append(
            {
                "id": sc["case_id"],
                "timestamp": sc["created_at"].isoformat(),
                "category": "service_case",
                "title": f"Service Case {sc['case_id']} — {sc['request_category']}",
                "summary": f"Complexity: {sc['complexity_level']} | Status: {sc['status']} | First-Response SLA: {'Breached' if sc['first_response_breached'] else 'Met/Pending'}",
                "actor": client["advisor_name"] or "Advisor",
                "severity": "risk" if sc["first_response_breached"] else "normal",
            }
        )
    timeline.sort(key=lambda x: x["timestamp"])

    tenure_days = (
        int(((client["exited_at"] or as_of) - activated_at).days)
        if activated_at is not None
        else None
    )

    return {
        "client": {
            "client_id": client["client_id"],
            "segment": client["segment"],
            "asset_tier": client["asset_tier"],
            "region": client["region"],
            "acquisition_channel": client["acquisition_channel"],
            "advisor_id": client["advisor_id"],
            "advisor_name": client["advisor_name"],
            "team_id": client["team_id"],
            "team_name": client["team_name"],
            "lifecycle_status": client["lifecycle_status"],
            "engagement_status": engagement_status,
            "relationship_tenure_days": tenure_days,
            "aum_usd": float(client["aum_usd"]),
            "early_sla_breaches": early_breaches,
            "open_requests": open_cases,
            "rework_cycles": rework_cycles,
            "days_since_last_contact": days_since_contact,
            "exited_at": client["exited_at"].isoformat() if client["exited_at"] else None,
            "exit_reason": client["exit_reason"],
        },
        "risk_assessment": {
            "method": "Transparent Rules-Based Classification (v1.0)",
            "rules_triggered": risk_rules_triggered,
            "limitation": "Deterministic risk flags highlight operational friction for review; they do not predict individual client exits with certainty.",
        },
        "stage_episodes": [
            {
                "episode_id": ep["episode_id"],
                "stage": ep["stage"],
                "entered_at": ep["entered_at"].isoformat(),
                "exited_at": ep["exited_at"].isoformat() if ep["exited_at"] else None,
                "outcome": ep["outcome"],
                "rework_reason": ep["rework_reason"],
            }
            for ep in episodes
        ],
        "timeline": timeline,
        "service_cases": [
            {
                "case_id": sc["case_id"],
                "request_category": sc["request_category"],
                "complexity_level": sc["complexity_level"],
                "status": sc["status"],
                "created_at": sc["created_at"].isoformat(),
                "first_response_breached": sc["first_response_breached"],
                "reopen_count": sc["reopen_count"],
            }
            for sc in cases
        ],
        "complaints": [
            {
                "complaint_id": cmp["complaint_id"],
                "category": cmp["category"],
                "severity": cmp["severity"],
                "submitted_at": cmp["submitted_at"].isoformat(),
                "reopened": cmp["reopened"],
                "root_cause_process": cmp["root_cause_process"],
            }
            for cmp in complaints
        ],
    }
