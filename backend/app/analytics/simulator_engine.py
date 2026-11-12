"""Interactive Impact Simulator engine and Excel workbook generator."""

from __future__ import annotations

from io import BytesIO
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from pydantic import BaseModel, Field


class ImpactScenarioInput(BaseModel):
    eligible_clients: int = Field(default=3200, ge=1, le=500000)
    baseline_attrition_pct: float = Field(default=7.5, ge=0.0, le=50.0)
    preventable_share_pct: float = Field(default=45.0, ge=0.0, le=100.0)
    relative_reduction_pct: float = Field(default=20.0, ge=0.0, le=100.0)
    adoption_rate_pct: float = Field(default=80.0, ge=0.0, le=100.0)
    avg_assets_per_client_usd: float = Field(default=850_000.0, ge=0.0)
    revenue_yield_bps: float = Field(default=65.0, ge=0.0, le=500.0)
    implementation_cost_usd: float = Field(default=180_000.0, ge=0.0)
    annual_operating_cost_usd: float = Field(default=95_000.0, ge=0.0)
    analysis_years: int = Field(default=1, ge=1, le=5)


def compute_impact_scenario(inp: ImpactScenarioInput) -> dict[str, Any]:
    """Deterministic scenario calculation matching the Excel deliverable 1:1."""

    def _calc(rel_red_pct: float, adoption_pct: float) -> dict[str, float]:
        baseline_exits_yr = inp.eligible_clients * (inp.baseline_attrition_pct / 100.0)
        preventable_exits_yr = baseline_exits_yr * (inp.preventable_share_pct / 100.0)
        retained_clients = (
            preventable_exits_yr
            * (rel_red_pct / 100.0)
            * (adoption_pct / 100.0)
            * inp.analysis_years
        )
        retained_assets_usd = retained_clients * inp.avg_assets_per_client_usd
        # Explicit revenue yield assumption (basis points on retained assets)
        implied_annual_fee_revenue_usd = retained_assets_usd * (inp.revenue_yield_bps / 10_000.0)
        total_program_cost_usd = inp.implementation_cost_usd + (
            inp.annual_operating_cost_usd * inp.analysis_years
        )
        return {
            "baseline_exits_per_year": round(baseline_exits_yr, 1),
            "retained_clients": round(retained_clients, 1),
            "retained_assets_usd": round(retained_assets_usd, 2),
            "implied_annual_fee_revenue_usd": round(implied_annual_fee_revenue_usd, 2),
            "total_program_cost_usd": round(total_program_cost_usd, 2),
        }

    base = _calc(inp.relative_reduction_pct, inp.adoption_rate_pct)
    conservative = _calc(inp.relative_reduction_pct * 0.60, inp.adoption_rate_pct * 0.80)
    optimistic = _calc(min(100.0, inp.relative_reduction_pct * 1.35), min(100.0, inp.adoption_rate_pct * 1.10))

    sensitivity = []
    for red in [10, 15, 20, 25, 30]:
        row_item = {"relative_reduction_pct": red, "adoption_cases": []}
        for adopt in [60, 80, 100]:
            res = _calc(float(red), float(adopt))
            row_item["adoption_cases"].append(
                {
                    "adoption_pct": adopt,
                    "retained_clients": res["retained_clients"],
                    "retained_assets_usd": res["retained_assets_usd"],
                }
            )
        sensitivity.append(row_item)

    return {
        "disclaimer": "These are assumption-driven planning scenarios, NOT measured causal forecasts.",
        "inputs": inp.model_dump(),
        "scenarios": {
            "conservative": conservative,
            "base": base,
            "optimistic": optimistic,
        },
        "sensitivity_table": sensitivity,
    }


def generate_impact_excel_bytes(inp: ImpactScenarioInput) -> bytes:
    """Generate formula-driven Excel workbook matching the web Impact Simulator."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Impact Simulator"

    navy_fill = PatternFill(start_color="20364A", end_color="20364A", fill_type="solid")
    soft_fill = PatternFill(start_color="E9F3EE", end_color="E9F3EE", fill_type="solid")
    header_font = Font(name="Calibri", size=12, bold=True, color="FFFFFF")
    bold_font = Font(name="Calibri", size=11, bold=True, color="17242D")

    ws["A1"] = "CONTINUUM — Operational Improvement Impact Simulator"
    ws["A1"].font = Font(name="Calibri", size=14, bold=True, color="20364A")
    ws["A2"] = "Meridian Private Wealth (Fictional) — Assumption-Driven Planning Scenarios (Not Causal Forecasts)"
    ws["A2"].font = Font(name="Calibri", size=10, italic=True, color="65727A")

    ws["A4"] = "Input Parameter"
    ws["B4"] = "Base Value"
    ws["C4"] = "Notes"
    for col in ("A4", "B4", "C4"):
        ws[col].fill = navy_fill
        ws[col].font = header_font

    inputs_rows = [
        ("Eligible Client Population", inp.eligible_clients, "Clients exposed to target process", "#,##0"),
        ("Baseline Annual Attrition (%)", inp.baseline_attrition_pct / 100.0, "Historical annual exit rate", "0.0%"),
        ("Share of Attrition Assumed Preventable (%)", inp.preventable_share_pct / 100.0, "Operational share", "0.0%"),
        ("Hypothetical Relative Reduction (%)", inp.relative_reduction_pct / 100.0, "Scenario assumption", "0.0%"),
        ("Intervention Adoption Rate (%)", inp.adoption_rate_pct / 100.0, "Operational adherence", "0.0%"),
        ("Average Assets per Client ($)", inp.avg_assets_per_client_usd, "Not equal to firm revenue", "$#,##0"),
        ("Explicit Revenue Yield Assumption (bps)", inp.revenue_yield_bps, "Advisory fee bps on AUM", "0.0"),
        ("Implementation Cost ($)", inp.implementation_cost_usd, "One-time setup cost", "$#,##0"),
        ("Annual Operating Cost ($)", inp.annual_operating_cost_usd, "Ongoing yearly cost", "$#,##0"),
        ("Analysis Period (Years)", inp.analysis_years, "Horizon in years", "0"),
    ]

    for idx, (label, val, note, num_fmt) in enumerate(inputs_rows, start=5):
        ws[f"A{idx}"] = label
        ws[f"B{idx}"] = val
        ws[f"B{idx}"].number_format = num_fmt
        ws[f"C{idx}"] = note

    # Scenario Outputs (Rows 17-23)
    ws["A17"] = "Scenario Output"
    ws["B17"] = "Conservative (0.6x Red / 0.8x Adopt)"
    ws["C17"] = "Base Case"
    ws["D17"] = "Optimistic (1.35x Red / 1.1x Adopt)"
    for col in ("A17", "B17", "C17", "D17"):
        ws[col].fill = navy_fill
        ws[col].font = header_font
        ws[col].alignment = Alignment(wrap_text=True)

    ws["A18"] = "Baseline Exits / Year"
    ws["B18"] = "=B5*B6"
    ws["C18"] = "=B5*B6"
    ws["D18"] = "=B5*B6"

    ws["A19"] = "Estimated Retained Clients"
    ws["B19"] = "=B18*B7*(B8*0.6)*(B9*0.8)*B14"
    ws["C19"] = "=B18*B7*B8*B9*B14"
    ws["D19"] = "=B18*B7*MIN(1,B8*1.35)*MIN(1,B9*1.1)*B14"

    ws["A20"] = "Scenario Retained Assets ($)"
    ws["B20"] = "=B19*B10"
    ws["C20"] = "=C19*B10"
    ws["D20"] = "=D19*B10"

    ws["A21"] = "Implied Annual Fee Revenue ($)"
    ws["B21"] = "=B20*(B11/10000)"
    ws["C21"] = "=C20*(B11/10000)"
    ws["D21"] = "=D20*(B11/10000)"

    ws["A22"] = "Total Program Cost ($)"
    ws["B22"] = "=B12+(B13*B14)"
    ws["C22"] = "=B12+(B13*B14)"
    ws["D22"] = "=B12+(B13*B14)"

    for r in (18, 19):
        for col in ("B", "C", "D"):
            ws[f"{col}{r}"].number_format = "#,##0.0"
    for r in (20, 21, 22):
        for col in ("B", "C", "D"):
            ws[f"{col}{r}"].number_format = "$#,##0"
    for r in range(18, 23):
        ws[f"A{r}"].font = bold_font
        ws[f"C{r}"].fill = soft_fill

    ws.column_dimensions["A"].width = 42
    ws.column_dimensions["B"].width = 24
    ws.column_dimensions["C"].width = 24
    ws.column_dimensions["D"].width = 24

    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()
