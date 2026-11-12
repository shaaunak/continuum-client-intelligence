from datetime import date, datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.analytics.client_engine import get_client_journey_detail, list_clients
from app.analytics.export_engine import generate_csv_export
from app.analytics.governance_engine import (
    get_data_quality_report,
    get_metric_dictionary,
    get_metric_lineage,
    get_requirements_hub,
)
from app.analytics.investigation_engine import INVESTIGATION_TEMPLATES, run_investigation
from app.analytics.journey_engine import get_journey_funnel, get_stage_detail
from app.analytics.kpi_engine import get_executive_overview, get_overview_trends
from app.analytics.operations_engine import (
    get_advisor_detail,
    get_advisor_intelligence,
    get_operations_complaints,
    get_operations_sla,
    get_operations_workload,
)
from app.analytics.retention_engine import (
    get_adjusted_comparison,
    get_cohort_retention,
    get_survival_analysis,
)
from app.analytics.simulator_engine import (
    ImpactScenarioInput,
    compute_impact_scenario,
    generate_impact_excel_bytes,
)
from app.core.config import get_settings
from app.core.database import check_db_health, get_db
from app.models.entities import Experiment, Investigation, Recommendation
from app.schemas.common import AnalyticsFilters

api_router = APIRouter()
settings = get_settings()


def parse_filters(
    start_date: date = Query(default=date(2026, 4, 1)),
    end_date: date = Query(default=date(2026, 10, 31)),
    compare_start_date: Optional[date] = Query(default=None),
    compare_end_date: Optional[date] = Query(default=None),
    segment: Optional[str] = Query(default=None),
    team_id: Optional[str] = Query(default=None),
    region: Optional[str] = Query(default=None),
    asset_tier: Optional[str] = Query(default=None),
) -> AnalyticsFilters:
    if end_date < start_date:
        raise HTTPException(status_code=400, detail="end_date must be >= start_date")
    return AnalyticsFilters(
        start_date=start_date,
        end_date=end_date,
        compare_start_date=compare_start_date,
        compare_end_date=compare_end_date,
        segment=segment,
        team_id=team_id,
        region=region,
        asset_tier=asset_tier,
    )


@api_router.get("/health", tags=["System"])
def health_check() -> dict:
    db_ok = check_db_health()
    return {
        "status": "ok" if db_ok else "degraded",
        "service": "continuum-api",
        "environment": settings.ENVIRONMENT,
        "database_connected": db_ok,
        "as_of_date": settings.AS_OF_DATE,
        "dataset_scale": settings.DATASET_SCALE,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@api_router.get("/filters/options", tags=["System"])
def filter_options(db: Session = Depends(get_db)) -> dict:
    teams = db.execute(
        text("SELECT team_id, team_name, region FROM advisor_teams ORDER BY team_id")
    ).mappings().all()
    return {
        "segments": ["Mass Affluent", "Affluent", "High Net Worth", "Ultra High Net Worth"],
        "asset_tiers": ["Tier 1 (<$250K)", "Tier 2 ($250K-$1M)", "Tier 3 ($1M-$5M)", "Tier 4 ($5M+)"],
        "regions": ["East", "North", "South", "West"],
        "teams": [dict(t) for t in teams],
    }


# 1. Executive Overview
@api_router.get("/overview", tags=["Executive Overview"])
def overview(filters: AnalyticsFilters = Depends(parse_filters), db: Session = Depends(get_db)) -> dict:
    return get_executive_overview(db, filters)


@api_router.get("/overview/trends", tags=["Executive Overview"])
def overview_trends(filters: AnalyticsFilters = Depends(parse_filters), db: Session = Depends(get_db)) -> list[dict]:
    return get_overview_trends(db, filters)


# 2. Journey Analytics
@api_router.get("/journey/funnel", tags=["Journey Analytics"])
def journey_funnel(filters: AnalyticsFilters = Depends(parse_filters), db: Session = Depends(get_db)) -> dict:
    return get_journey_funnel(db, filters)


@api_router.get("/journey/stages/{stage}", tags=["Journey Analytics"])
def journey_stage_detail(
    stage: str, filters: AnalyticsFilters = Depends(parse_filters), db: Session = Depends(get_db)
) -> dict:
    return get_stage_detail(db, stage, filters)


# 3. Retention Studio
@api_router.get("/retention/cohorts", tags=["Retention Studio"])
def retention_cohorts(filters: AnalyticsFilters = Depends(parse_filters), db: Session = Depends(get_db)) -> dict:
    return get_cohort_retention(db, filters)


@api_router.get("/retention/survival", tags=["Retention Studio"])
def retention_survival(filters: AnalyticsFilters = Depends(parse_filters), db: Session = Depends(get_db)) -> dict:
    return get_survival_analysis(db, filters)


@api_router.get("/retention/adjusted", tags=["Retention Studio"])
def retention_adjusted(filters: AnalyticsFilters = Depends(parse_filters), db: Session = Depends(get_db)) -> dict:
    return get_adjusted_comparison(db, filters)


# 4. Client Explorer
@api_router.get("/clients", tags=["Client Explorer"])
def clients_list(
    search: Optional[str] = None,
    segment: Optional[str] = None,
    asset_tier: Optional[str] = None,
    lifecycle_status: Optional[str] = None,
    engagement_status: Optional[str] = None,
    team_id: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=5, le=100),
    db: Session = Depends(get_db),
) -> dict:
    return list_clients(
        db,
        search=search,
        segment=segment,
        asset_tier=asset_tier,
        lifecycle_status=lifecycle_status,
        engagement_status=engagement_status,
        team_id=team_id,
        page=page,
        page_size=page_size,
    )


@api_router.get("/clients/{client_id}/journey", tags=["Client Explorer"])
def client_journey(client_id: str, db: Session = Depends(get_db)) -> dict:
    res = get_client_journey_detail(db, client_id)
    if not res:
        raise HTTPException(status_code=404, detail=f"Client {client_id} not found")
    return res


# 5. Service Operations & Advisor Intelligence
@api_router.get("/operations/workload", tags=["Service Operations"])
def operations_workload(filters: AnalyticsFilters = Depends(parse_filters), db: Session = Depends(get_db)) -> dict:
    return get_operations_workload(db, filters)


@api_router.get("/operations/sla", tags=["Service Operations"])
def operations_sla(filters: AnalyticsFilters = Depends(parse_filters), db: Session = Depends(get_db)) -> dict:
    return get_operations_sla(db, filters)


@api_router.get("/operations/complaints", tags=["Service Operations"])
def operations_complaints(
    category: Optional[str] = None,
    filters: AnalyticsFilters = Depends(parse_filters),
    db: Session = Depends(get_db),
) -> dict:
    return get_operations_complaints(db, filters, category=category)


@api_router.get("/advisors", tags=["Advisor Intelligence"])
def advisors_list(filters: AnalyticsFilters = Depends(parse_filters), db: Session = Depends(get_db)) -> dict:
    return get_advisor_intelligence(db, filters)


@api_router.get("/advisors/{advisor_id}", tags=["Advisor Intelligence"])
def advisor_detail(advisor_id: str, db: Session = Depends(get_db)) -> dict:
    res = get_advisor_detail(db, advisor_id)
    if not res:
        raise HTTPException(status_code=404, detail=f"Advisor {advisor_id} not found")
    return res


# 6. Investigation Lab
class InvestigationCreateRequest(BaseModel):
    template_key: str = "retention_decline"
    start_date: date = date(2026, 4, 1)
    end_date: date = date(2026, 10, 31)
    segment: Optional[str] = None
    team_id: Optional[str] = None
    region: Optional[str] = None
    asset_tier: Optional[str] = None
    created_by: str = "Lead Business Analyst"


@api_router.get("/investigations/templates", tags=["Investigation Lab"])
def investigation_templates() -> list[dict]:
    return INVESTIGATION_TEMPLATES


@api_router.post("/investigations", tags=["Investigation Lab"])
def create_investigation(req: InvestigationCreateRequest, db: Session = Depends(get_db)) -> dict:
    filters = AnalyticsFilters(
        start_date=req.start_date,
        end_date=req.end_date,
        segment=req.segment,
        team_id=req.team_id,
        region=req.region,
        asset_tier=req.asset_tier,
    )
    return run_investigation(db, template_key=req.template_key, filters=filters, created_by=req.created_by)


@api_router.get("/investigations", tags=["Investigation Lab"])
def list_investigations(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.query(Investigation).order_by(Investigation.created_at.desc()).limit(20).all()
    return [
        {
            "investigation_id": r.investigation_id,
            "title": r.title,
            "template_key": r.template_key,
            "status": r.status,
            "created_by": r.created_by,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


@api_router.get("/investigations/{investigation_id}", tags=["Investigation Lab"])
def get_investigation(investigation_id: str, db: Session = Depends(get_db)) -> dict:
    inv = db.query(Investigation).filter(Investigation.investigation_id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return {
        "investigation_id": inv.investigation_id,
        "title": inv.title,
        "template_key": inv.template_key,
        "findings": inv.findings_json,
        "created_at": inv.created_at.isoformat() if inv.created_at else None,
    }


# 7. Improvement Roadmap & Experiments
class RecommendationUpdate(BaseModel):
    status: Optional[str] = None
    rice_reach: Optional[int] = None
    rice_impact: Optional[float] = None
    rice_confidence: Optional[float] = None
    rice_effort: Optional[float] = None


@api_router.get("/recommendations", tags=["Improvement Roadmap"])
def list_recommendations(db: Session = Depends(get_db)) -> list[dict]:
    recs = db.query(Recommendation).order_by(Recommendation.rice_score.desc()).all()
    exps = {e.recommendation_id: e for e in db.query(Experiment).all()}
    out = []
    for r in recs:
        e = exps.get(r.recommendation_id)
        out.append(
            {
                "recommendation_id": r.recommendation_id,
                "title": r.title,
                "target_process": r.target_process,
                "business_problem": r.business_problem,
                "supporting_evidence": r.supporting_evidence,
                "hypothesis": r.hypothesis,
                "suggested_intervention": r.suggested_intervention,
                "success_metric": r.success_metric,
                "guardrail_metric": r.guardrail_metric,
                "experiment_design": r.experiment_design,
                "stakeholder_owner": r.stakeholder_owner,
                "implementation_effort": r.implementation_effort,
                "estimated_impact_range": r.estimated_impact_range,
                "dependencies": r.dependencies,
                "risks": r.risks,
                "rice_reach": r.rice_reach,
                "rice_impact": r.rice_impact,
                "rice_confidence": r.rice_confidence,
                "rice_effort": r.rice_effort,
                "rice_score": r.rice_score,
                "priority": r.priority,
                "status": r.status,
                "linked_requirement_id": r.linked_requirement_id,
                "experiment": {
                    "experiment_id": e.experiment_id,
                    "name": e.name,
                    "design_type": e.design_type,
                    "evaluation_window_days": e.evaluation_window_days,
                    "status": e.status,
                    "notes": e.notes,
                }
                if e
                else None,
            }
        )
    return out


@api_router.patch("/recommendations/{recommendation_id}", tags=["Improvement Roadmap"])
def update_recommendation(
    recommendation_id: str, payload: RecommendationUpdate, db: Session = Depends(get_db)
) -> dict:
    rec = db.query(Recommendation).filter(Recommendation.recommendation_id == recommendation_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    if payload.status is not None:
        rec.status = payload.status
    if payload.rice_reach is not None:
        rec.rice_reach = payload.rice_reach
    if payload.rice_impact is not None:
        rec.rice_impact = payload.rice_impact
    if payload.rice_confidence is not None:
        rec.rice_confidence = payload.rice_confidence
    if payload.rice_effort is not None and payload.rice_effort > 0:
        rec.rice_effort = payload.rice_effort
    rec.rice_score = round((rec.rice_reach * rec.rice_impact * rec.rice_confidence) / max(0.5, rec.rice_effort), 1)
    db.commit()
    return {"recommendation_id": rec.recommendation_id, "rice_score": rec.rice_score, "status": rec.status}


# 8. Impact Simulator
@api_router.post("/impact/scenario", tags=["Impact Simulator"])
def impact_scenario(payload: ImpactScenarioInput) -> dict:
    return compute_impact_scenario(payload)


@api_router.post("/impact/excel", tags=["Impact Simulator"])
def impact_excel_download(payload: ImpactScenarioInput) -> Response:
    content = generate_impact_excel_bytes(payload)
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="continuum_impact_simulator.xlsx"'},
    )


# 9. Governance, KPI Dictionary, Requirements & Exports
@api_router.get("/metrics/dictionary", tags=["Governance"])
def metrics_dictionary(db: Session = Depends(get_db)) -> list[dict]:
    return get_metric_dictionary(db)


@api_router.get("/metrics/{metric_key}/lineage", tags=["Governance"])
def metric_lineage(metric_key: str, db: Session = Depends(get_db)) -> dict:
    res = get_metric_lineage(db, metric_key)
    if not res:
        raise HTTPException(status_code=404, detail=f"Metric {metric_key} not found")
    return res


@api_router.get("/requirements", tags=["Governance"])
def requirements_hub() -> dict:
    return get_requirements_hub()


@api_router.get("/data-quality", tags=["Governance"])
def data_quality(db: Session = Depends(get_db)) -> dict:
    return get_data_quality_report(db)


@api_router.get("/exports/{report_type}", tags=["Exports"])
def export_csv(report_type: str, db: Session = Depends(get_db)) -> Response:
    try:
        filename, csv_text = generate_csv_export(db, report_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return Response(
        content=csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
