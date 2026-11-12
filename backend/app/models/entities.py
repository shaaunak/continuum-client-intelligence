from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AdvisorTeam(Base):
    __tablename__ = "advisor_teams"

    team_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    team_name: Mapped[str] = mapped_column(String(120), nullable=False)
    region: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    target_capacity_cases: Mapped[int] = mapped_column(Integer, nullable=False)
    headcount: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    advisors: Mapped[list["Advisor"]] = relationship(back_populates="team")


class Advisor(Base):
    __tablename__ = "advisors"

    advisor_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    advisor_code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    team_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("advisor_teams.team_id"), nullable=False, index=True
    )
    seniority_level: Mapped[str] = mapped_column(String(32), nullable=False)
    max_active_cases: Mapped[int] = mapped_column(Integer, nullable=False, default=35)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    hired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    team: Mapped["AdvisorTeam"] = relationship(back_populates="advisors")


class Client(Base):
    __tablename__ = "clients"
    __table_args__ = (
        Index("ix_clients_segment_tier", "segment", "asset_tier"),
        Index("ix_clients_activated_exited", "activated_at", "exited_at"),
    )

    client_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    segment: Mapped[str] = mapped_column(String(48), nullable=False, index=True)
    asset_tier: Mapped[str] = mapped_column(String(48), nullable=False, index=True)
    region: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    acquisition_channel: Mapped[str] = mapped_column(String(64), nullable=False)
    prospect_created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    activated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    exited_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    exit_reason: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    lifecycle_status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    aum_usd: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class AdvisorAssignment(Base):
    __tablename__ = "advisor_assignments"
    __table_args__ = (
        Index("ix_assignments_client_primary", "client_id", "is_primary"),
        Index("ix_assignments_advisor_dates", "advisor_id", "assigned_at", "unassigned_at"),
    )

    assignment_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    client_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("clients.client_id"), nullable=False
    )
    advisor_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("advisors.advisor_id"), nullable=False
    )
    team_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("advisor_teams.team_id"), nullable=False, index=True
    )
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    unassigned_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    assignment_reason: Mapped[str] = mapped_column(String(64), nullable=False)


class ClientAccount(Base):
    __tablename__ = "client_accounts"

    account_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    client_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("clients.client_id"), nullable=False, index=True
    )
    account_type: Mapped[str] = mapped_column(String(64), nullable=False)
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    funded_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    closed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    initial_funding_usd: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)


class JourneyStageEpisode(Base):
    __tablename__ = "journey_stage_episodes"
    __table_args__ = (
        Index("ix_episodes_client_stage", "client_id", "stage"),
        Index("ix_episodes_stage_entered", "stage", "entered_at"),
    )

    episode_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    client_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("clients.client_id"), nullable=False
    )
    stage: Mapped[str] = mapped_column(String(48), nullable=False, index=True)
    entered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    exited_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    assigned_team_id: Mapped[Optional[str]] = mapped_column(
        String(32), ForeignKey("advisor_teams.team_id"), nullable=True
    )
    assigned_advisor_id: Mapped[Optional[str]] = mapped_column(
        String(32), ForeignKey("advisors.advisor_id"), nullable=True
    )
    outcome: Mapped[str] = mapped_column(String(32), nullable=False)
    rework_reason: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    previous_episode_id: Mapped[Optional[str]] = mapped_column(
        String(48), ForeignKey("journey_stage_episodes.episode_id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class JourneyEvent(Base):
    __tablename__ = "journey_events"
    __table_args__ = (Index("ix_journey_events_client_ts", "client_id", "event_timestamp"),)

    event_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    client_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("clients.client_id"), nullable=False
    )
    episode_id: Mapped[Optional[str]] = mapped_column(
        String(48), ForeignKey("journey_stage_episodes.episode_id"), nullable=True
    )
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    event_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    actor_type: Mapped[str] = mapped_column(String(32), nullable=False)
    actor_id: Mapped[Optional[str]] = mapped_column(String(48), nullable=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)


class SlaPolicy(Base):
    __tablename__ = "sla_policies"

    policy_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    request_category: Mapped[str] = mapped_column(String(64), nullable=False)
    complexity_level: Mapped[str] = mapped_column(String(32), nullable=False)
    first_response_business_hours: Mapped[float] = mapped_column(Float, nullable=False)
    resolution_business_hours: Mapped[float] = mapped_column(Float, nullable=False)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ServiceCase(Base):
    __tablename__ = "service_cases"
    __table_args__ = (
        Index("ix_cases_client_created", "client_id", "created_at"),
        Index("ix_cases_team_status", "assigned_team_id", "status"),
        Index("ix_cases_advisor_status", "assigned_advisor_id", "status"),
    )

    case_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    client_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("clients.client_id"), nullable=False
    )
    assigned_advisor_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("advisors.advisor_id"), nullable=False
    )
    assigned_team_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("advisor_teams.team_id"), nullable=False
    )
    request_category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    complexity_level: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    first_response_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    first_response_due_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    first_response_breached: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    resolution_due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    resolution_breached: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    reopen_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    repeat_contact_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    channel: Mapped[str] = mapped_column(String(32), nullable=False)


class ServiceCaseEvent(Base):
    __tablename__ = "service_case_events"
    __table_args__ = (Index("ix_case_events_case_ts", "case_id", "event_timestamp"),)

    event_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    case_id: Mapped[str] = mapped_column(
        String(48), ForeignKey("service_cases.case_id"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    event_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    actor_id: Mapped[Optional[str]] = mapped_column(String(48), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class Complaint(Base):
    __tablename__ = "complaints"
    __table_args__ = (
        Index("ix_complaints_category_submitted", "category", "submitted_at"),
        Index("ix_complaints_client", "client_id"),
    )

    complaint_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    client_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("clients.client_id"), nullable=False
    )
    case_id: Mapped[Optional[str]] = mapped_column(
        String(48), ForeignKey("service_cases.case_id"), nullable=True
    )
    assigned_team_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("advisor_teams.team_id"), nullable=False, index=True
    )
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    reopened: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    reopen_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    repeat_contact_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    root_cause_process: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)


class ClientInteraction(Base):
    __tablename__ = "client_interactions"
    __table_args__ = (Index("ix_interactions_client_ts", "client_id", "occurred_at"),)

    interaction_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    client_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("clients.client_id"), nullable=False
    )
    advisor_id: Mapped[Optional[str]] = mapped_column(
        String(32), ForeignKey("advisors.advisor_id"), nullable=True
    )
    interaction_type: Mapped[str] = mapped_column(String(48), nullable=False)
    qualifying_engagement: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    channel: Mapped[str] = mapped_column(String(32), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)


class FollowUpTask(Base):
    __tablename__ = "follow_up_tasks"
    __table_args__ = (Index("ix_followups_advisor_status", "advisor_id", "status"),)

    task_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    client_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("clients.client_id"), nullable=False, index=True
    )
    case_id: Mapped[Optional[str]] = mapped_column(
        String(48), ForeignKey("service_cases.case_id"), nullable=True
    )
    advisor_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("advisors.advisor_id"), nullable=False
    )
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    task_type: Mapped[str] = mapped_column(String(64), nullable=False)


class ProcessChange(Base):
    __tablename__ = "process_changes"

    change_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    change_code: Mapped[str] = mapped_column(String(48), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    target_stage: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    target_category: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    effective_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    affected_teams: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)


class ClientStatusEvent(Base):
    __tablename__ = "client_status_events"
    __table_args__ = (Index("ix_client_status_client_ts", "client_id", "effective_at"),)

    status_event_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    client_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("clients.client_id"), nullable=False
    )
    status_type: Mapped[str] = mapped_column(String(32), nullable=False)
    status_value: Mapped[str] = mapped_column(String(48), nullable=False)
    effective_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    rule_reason: Mapped[str] = mapped_column(Text, nullable=False)


class Investigation(Base):
    __tablename__ = "investigations"

    investigation_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    template_key: Mapped[str] = mapped_column(String(64), nullable=False)
    business_question: Mapped[str] = mapped_column(Text, nullable=False)
    scope_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    findings_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="Completed")
    created_by: Mapped[str] = mapped_column(String(64), nullable=False, default="Lead Analyst")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class Recommendation(Base):
    __tablename__ = "recommendations"

    recommendation_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    target_process: Mapped[str] = mapped_column(String(120), nullable=False)
    business_problem: Mapped[str] = mapped_column(Text, nullable=False)
    supporting_evidence: Mapped[str] = mapped_column(Text, nullable=False)
    hypothesis: Mapped[str] = mapped_column(Text, nullable=False)
    suggested_intervention: Mapped[str] = mapped_column(Text, nullable=False)
    success_metric: Mapped[str] = mapped_column(String(160), nullable=False)
    guardrail_metric: Mapped[str] = mapped_column(String(200), nullable=False)
    experiment_design: Mapped[str] = mapped_column(Text, nullable=False)
    stakeholder_owner: Mapped[str] = mapped_column(String(120), nullable=False)
    implementation_effort: Mapped[str] = mapped_column(String(32), nullable=False)
    estimated_impact_range: Mapped[str] = mapped_column(String(120), nullable=False)
    dependencies: Mapped[str] = mapped_column(Text, nullable=False)
    risks: Mapped[str] = mapped_column(Text, nullable=False)
    rice_reach: Mapped[int] = mapped_column(Integer, nullable=False)
    rice_impact: Mapped[float] = mapped_column(Float, nullable=False)
    rice_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    rice_effort: Mapped[float] = mapped_column(Float, nullable=False)
    rice_score: Mapped[float] = mapped_column(Float, nullable=False)
    priority: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="Proposed")
    linked_requirement_id: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class Experiment(Base):
    __tablename__ = "experiments"

    experiment_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    recommendation_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("recommendations.recommendation_id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    design_type: Mapped[str] = mapped_column(String(120), nullable=False)
    primary_metric: Mapped[str] = mapped_column(String(160), nullable=False)
    guardrail_metrics: Mapped[str] = mapped_column(Text, nullable=False)
    target_population: Mapped[str] = mapped_column(Text, nullable=False)
    evaluation_window_days: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="Proposed")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class MetricDefinition(Base):
    __tablename__ = "metric_definitions"

    metric_key: Mapped[str] = mapped_column(String(64), primary_key=True)
    kpi_name: Mapped[str] = mapped_column(String(120), nullable=False)
    business_meaning: Mapped[str] = mapped_column(Text, nullable=False)
    formula: Mapped[str] = mapped_column(Text, nullable=False)
    numerator: Mapped[str] = mapped_column(Text, nullable=False)
    denominator: Mapped[str] = mapped_column(Text, nullable=False)
    time_basis: Mapped[str] = mapped_column(String(120), nullable=False)
    inclusion_criteria: Mapped[str] = mapped_column(Text, nullable=False)
    exclusions: Mapped[str] = mapped_column(Text, nullable=False)
    data_source: Mapped[str] = mapped_column(String(120), nullable=False)
    sql_template: Mapped[str] = mapped_column(Text, nullable=False)
    known_limitations: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
