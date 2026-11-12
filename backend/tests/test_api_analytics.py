"""Automated API, analytical correctness, and reconciliation tests."""

import io
import pytest
from fastapi.testclient import TestClient
from openpyxl import load_workbook

from app.analytics.simulator_engine import ImpactScenarioInput, compute_impact_scenario, generate_impact_excel_bytes
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["database_connected"] is True


def test_overview_and_trends():
    r = client.get("/api/v1/overview?start_date=2026-04-01&end_date=2026-10-31")
    assert r.status_code == 200
    data = r.json()
    assert len(data["kpis"]) == 6
    assert len(data["friction_signals"]) == 3
    assert len(data["insights"]) >= 2

    # Invalid date range should return 400
    r_bad = client.get("/api/v1/overview?start_date=2026-10-31&end_date=2026-04-01")
    assert r_bad.status_code == 400

    r_tr = client.get("/api/v1/overview/trends")
    assert r_tr.status_code == 200
    assert len(r_tr.json()) >= 24


def test_journey_funnel_and_kyc_stage():
    r = client.get("/api/v1/journey/funnel?start_date=2026-04-01&end_date=2026-10-31")
    assert r.status_code == 200
    stages = r.json()["stages"]
    assert len(stages) == 7
    kyc = next(s for s in stages if s["stage"] == "KYC")
    # Post-April 2026 KYC rework should show positive change vs prior window
    assert kyc["rework_change_pp"] > 5.0

    r_stg = client.get("/api/v1/journey/stages/KYC?start_date=2026-04-01&end_date=2026-10-31")
    assert r_stg.status_code == 200
    assert len(r_stg.json()["rework_reasons"]) >= 3


def test_retention_cohorts_maturity_and_survival_landmark():
    r_coh = client.get("/api/v1/retention/cohorts")
    assert r_coh.status_code == 200
    cohorts = r_coh.json()["cohorts"]
    assert len(cohorts) >= 24
    # Most recent cohort (2026-10) should have 0 observed months, never fabricated 24 months
    latest = cohorts[-1]
    assert latest["observed_months"] == 0

    r_surv = client.get("/api/v1/retention/survival")
    assert r_surv.status_code == 200
    surv = r_surv.json()
    assert surv["landmark_days"] == 90
    assert surv["eligible_clients"] > 1000
    groups = {g["group"]: g for g in surv["groups"]}
    assert "0 SLA Breaches" in groups
    assert "2+ SLA Breaches" in groups

    r_adj = client.get("/api/v1/retention/adjusted")
    assert r_adj.status_code == 200
    adj = r_adj.json()
    assert adj["cox_model"]["available"] is True
    unadj_hr = adj["cox_model"]["unadjusted_hr"]["2plus_breaches_vs_0"]["hazard_ratio"]
    adj_hr = adj["cox_model"]["adjusted_hr"]["2plus_breaches_vs_0"]["hazard_ratio"]
    # Unadjusted HR should be larger than or close to adjusted due to asset tier confounding
    assert unadj_hr > 1.2
    assert adj_hr > 1.1


def test_client_explorer_and_sql_injection_resistance():
    r = client.get("/api/v1/clients?engagement_status=At%20Risk&page=1&page_size=10")
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) > 0
    cid = items[0]["client_id"]

    r_det = client.get(f"/api/v1/clients/{cid}/journey")
    assert r_det.status_code == 200
    assert r_det.json()["client"]["client_id"] == cid
    assert len(r_det.json()["timeline"]) > 0

    # SQL injection attempt in search
    r_sqli = client.get("/api/v1/clients?search=' OR 1=1;--")
    assert r_sqli.status_code == 200
    assert r_sqli.json()["total"] == 0


def test_operations_and_advisors():
    r_wl = client.get("/api/v1/operations/workload")
    assert r_wl.status_code == 200
    teams = {t["team_id"]: t for t in r_wl.json()["teams"]}
    assert teams["T-03"]["utilization_pct"] > teams["T-01"]["utilization_pct"]

    r_sla = client.get("/api/v1/operations/sla")
    assert r_sla.status_code == 200
    assert r_sla.json()["summary"]["p90_business_hours"] >= r_sla.json()["summary"]["p50_business_hours"]

    r_cmp = client.get("/api/v1/operations/complaints")
    assert r_cmp.status_code == 200
    assert r_cmp.json()["total_complaints"] > 0

    r_adv = client.get("/api/v1/advisors")
    assert r_adv.status_code == 200
    assert len(r_adv.json()["advisors"]) == 48


def test_investigation_lab_and_recommendations():
    r_inv = client.post("/api/v1/investigations", json={"template_key": "retention_decline"})
    assert r_inv.status_code == 200
    inv_id = r_inv.json()["investigation_id"]

    r_get = client.get(f"/api/v1/investigations/{inv_id}")
    assert r_get.status_code == 200
    assert "step_6_summary" in r_get.json()["findings"]

    r_rec = client.get("/api/v1/recommendations")
    assert r_rec.status_code == 200
    assert len(r_rec.json()) == 4


def test_impact_simulator_and_excel_parity():
    inp = ImpactScenarioInput(
        eligible_clients=3200,
        baseline_attrition_pct=7.5,
        preventable_share_pct=45.0,
        relative_reduction_pct=20.0,
        adoption_rate_pct=80.0,
        avg_assets_per_client_usd=850_000.0,
        revenue_yield_bps=65.0,
        implementation_cost_usd=180_000.0,
        annual_operating_cost_usd=95_000.0,
        analysis_years=1,
    )
    res = compute_impact_scenario(inp)
    base = res["scenarios"]["base"]
    # Manual check: 3200 * 0.075 = 240 exits; * 0.45 = 108 preventable; * 0.20 * 0.80 = 17.28 -> 17.3 retained clients
    assert abs(base["retained_clients"] - 17.3) <= 0.1
    assert abs(base["total_program_cost_usd"] - 275_000.0) < 0.01

    xlsx_bytes = generate_impact_excel_bytes(inp)
    wb = load_workbook(io.BytesIO(xlsx_bytes), data_only=False)
    ws = wb["Impact Simulator"]
    assert ws["B5"].value == 3200
    assert ws["C19"].value == "=B18*B7*B8*B9*B14"


def test_governance_and_exports():
    r_dict = client.get("/api/v1/metrics/dictionary")
    assert r_dict.status_code == 200
    assert len(r_dict.json()) >= 14

    r_dq = client.get("/api/v1/data-quality")
    assert r_dq.status_code == 200
    assert r_dq.json()["all_passed"] is True

    r_req = client.get("/api/v1/requirements")
    assert r_req.status_code == 200
    assert len(r_req.json()["user_stories"]) >= 5

    r_csv = client.get("/api/v1/exports/executive_monthly_metrics")
    assert r_csv.status_code == 200
    assert "month,active_start,exited_month" in r_csv.text
