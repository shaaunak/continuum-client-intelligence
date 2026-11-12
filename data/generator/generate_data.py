"""Deterministic synthetic dataset generator for CONTINUUM.

Generates Meridian Private Wealth (fictional) client lifecycle, onboarding,
service case, SLA, complaint, advisor workload, and retention data with
5 planted analytical stories and strict chronological/referential integrity.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import numpy as np

from app.analytics.business_hours import add_business_hours

AS_OF_DATE = datetime(2026, 10, 31, 23, 59, 59, tzinfo=timezone.utc)
START_DATE = datetime(2023, 11, 1, 9, 0, 0, tzinfo=timezone.utc)

KYC_CHANGE_DATE = datetime(2026, 4, 1, 0, 0, 0, tzinfo=timezone.utc)
CAPACITY_CHANGE_DATE = datetime(2026, 5, 15, 0, 0, 0, tzinfo=timezone.utc)
TRANSFER_CHANGE_DATE = datetime(2026, 6, 1, 0, 0, 0, tzinfo=timezone.utc)

TEAMS_SPEC = [
    ("T-01", "Northeast Wealth Partners", "East", 210, 6),
    ("T-02", "Manhattan Private Client", "East", 210, 6),
    ("T-03", "North Region — Premier Advisory", "North", 140, 4),  # Reduced from 6 to 4 on 2026-05-15
    ("T-04", "Great Lakes Advisory", "North", 210, 6),
    ("T-05", "Southeast Wealth Group", "South", 210, 6),
    ("T-06", "Texas & Gulf Private Wealth", "South", 210, 6),
    ("T-07", "Pacific Coast Advisory", "West", 210, 6),
    ("T-08", "Mountain West Client Group", "West", 210, 6),
]

FIRST_NAMES = [
    "Elena", "Marcus", "Claire", "Julian", "Nadia", "Devon", "Hannah", "Trevor",
    "Priya", "Arthur", "Sonia", "Graham", "Maya", "Victor", "Rachel", "Owen",
    "Tessa", "Liam", "Anita", "Colin", "Leah", "Simon", "Grace", "Daniel",
]
LAST_NAMES = [
    "Vance", "Sterling", "Mercer", "Kensington", "Patel", "Whitman", "okafor", "Lindqvist",
    "Chen", "Brooks", "Alvarez", "Sinclair", "Donovan", "Kerr", "Sato", "henderson",
    "Callahan", "Nair", "Moreau", "Gallagher", "Fletcher", "Bennett", "Kim", "Wallace",
]

SEGMENTS = ["Mass Affluent", "Affluent", "High Net Worth", "Ultra High Net Worth"]
SEGMENT_PROBS = [0.42, 0.33, 0.18, 0.07]

TIER_BY_SEGMENT = {
    "Mass Affluent": ("Tier 1 (<$250K)", (85_000, 245_000)),
    "Affluent": ("Tier 2 ($250K-$1M)", (260_000, 980_000)),
    "High Net Worth": ("Tier 3 ($1M-$5M)", (1_050_000, 4_850_000)),
    "Ultra High Net Worth": ("Tier 4 ($5M+)", (5_200_000, 18_500_000)),
}

CHANNELS = [
    "Advisor Referral",
    "Private Banking",
    "Digital Wealth",
    "Institutional Partner",
    "Executive Network",
]
CHANNEL_PROBS = [0.34, 0.24, 0.20, 0.12, 0.10]

CASE_CATEGORIES = [
    "Account Servicing",
    "Portfolio & Advisory",
    "Tax & Reporting",
    "Transfer & Settlement",
    "Onboarding & KYC Support",
    "Billing & Fees",
]

SLA_POLICIES_SPEC = [
    ("POL-01", "Account Servicing", "Low", 8.0, 24.0),
    ("POL-02", "Account Servicing", "Medium", 6.0, 20.0),
    ("POL-03", "Account Servicing", "High", 4.0, 16.0),
    ("POL-04", "Portfolio & Advisory", "Low", 8.0, 24.0),
    ("POL-05", "Portfolio & Advisory", "Medium", 4.0, 16.0),
    ("POL-06", "Portfolio & Advisory", "High", 2.0, 12.0),
    ("POL-07", "Tax & Reporting", "Low", 12.0, 40.0),
    ("POL-08", "Tax & Reporting", "Medium", 8.0, 32.0),
    ("POL-09", "Tax & Reporting", "High", 4.0, 24.0),
    ("POL-10", "Transfer & Settlement", "Low", 6.0, 24.0),
    ("POL-11", "Transfer & Settlement", "Medium", 4.0, 16.0),
    ("POL-12", "Transfer & Settlement", "High", 2.0, 12.0),
    ("POL-13", "Onboarding & KYC Support", "Low", 8.0, 24.0),
    ("POL-14", "Onboarding & KYC Support", "Medium", 4.0, 16.0),
    ("POL-15", "Onboarding & KYC Support", "High", 2.0, 12.0),
    ("POL-16", "Billing & Fees", "Low", 8.0, 24.0),
    ("POL-17", "Billing & Fees", "Medium", 6.0, 20.0),
    ("POL-18", "Billing & Fees", "High", 4.0, 16.0),
]

KYC_REWORK_REASONS = [
    "Missing identity documentation",
    "Checklist clarification",
    "Incomplete address verification",
    "Document mismatch",
]

EXIT_REASONS = [
    "Fee sensitivity",
    "Service responsiveness",
    "Consolidated elsewhere",
    "Advisor relationship change",
    "Liquidity event / estate",
]


@dataclass
class GeneratedDataset:
    teams: list[dict[str, Any]]
    advisors: list[dict[str, Any]]
    sla_policies: list[dict[str, Any]]
    process_changes: list[dict[str, Any]]
    clients: list[dict[str, Any]]
    advisor_assignments: list[dict[str, Any]]
    client_accounts: list[dict[str, Any]]
    journey_stage_episodes: list[dict[str, Any]]
    journey_events: list[dict[str, Any]]
    service_cases: list[dict[str, Any]]
    service_case_events: list[dict[str, Any]]
    complaints: list[dict[str, Any]]
    client_interactions: list[dict[str, Any]]
    follow_up_tasks: list[dict[str, Any]]
    client_status_events: list[dict[str, Any]]
    recommendations: list[dict[str, Any]]
    experiments: list[dict[str, Any]]
    metric_definitions: list[dict[str, Any]]


def _clamp_dt(dt: datetime, max_dt: datetime = AS_OF_DATE) -> datetime:
    return min(dt, max_dt)


def generate_synthetic_dataset(seed: int = 20270101, scale: str = "full") -> GeneratedDataset:
    rng = np.random.default_rng(seed)
    n_clients = 12000 if scale == "full" else 2400

    # 1. Teams & Advisors
    teams: list[dict[str, Any]] = []
    advisors: list[dict[str, Any]] = []
    team_advisors_active: dict[str, list[str]] = {}
    team_region: dict[str, str] = {}

    adv_idx = 1
    for t_id, t_name, region, target_cap, headcount in TEAMS_SPEC:
        teams.append(
            {
                "team_id": t_id,
                "team_name": t_name,
                "region": region,
                "target_capacity_cases": target_cap,
                "headcount": headcount,
            }
        )
        team_region[t_id] = region
        team_advisors_active[t_id] = []
        for slot in range(6):
            adv_id = f"ADV-{adv_idx:03d}"
            fn = FIRST_NAMES[(adv_idx - 1) % len(FIRST_NAMES)].capitalize()
            ln = LAST_NAMES[((adv_idx * 3) - 1) % len(LAST_NAMES)].capitalize()
            is_departed_t3 = t_id == "T-03" and slot >= 4
            seniority = ["Associate", "Senior Advisor", "Director"][slot % 3]
            hired_at = START_DATE - timedelta(days=int(rng.integers(180, 1800)))
            advisors.append(
                {
                    "advisor_id": adv_id,
                    "advisor_code": f"MPW-{adv_idx:03d}",
                    "display_name": f"{fn} {ln}",
                    "team_id": t_id,
                    "seniority_level": seniority,
                    "max_active_cases": 35,
                    "active": not is_departed_t3,
                    "hired_at": hired_at,
                }
            )
            if not is_departed_t3:
                team_advisors_active[t_id].append(adv_id)
            adv_idx += 1

    # 2. SLA Policies
    sla_policies = [
        {
            "policy_id": pid,
            "request_category": cat,
            "complexity_level": comp,
            "first_response_business_hours": fr,
            "resolution_business_hours": res,
            "effective_from": START_DATE,
        }
        for pid, cat, comp, fr, res in SLA_POLICIES_SPEC
    ]
    sla_lookup = {(cat, comp): (fr, res) for _, cat, comp, fr, res in SLA_POLICIES_SPEC}

    # 3. Process Changes
    process_changes = [
        {
            "change_id": "PC-001",
            "change_code": "KYC-CHK-V24",
            "title": "Enhanced KYC Documentation Checklist v2.4",
            "target_stage": "KYC",
            "target_category": "Onboarding & KYC Support",
            "effective_date": KYC_CHANGE_DATE,
            "description": (
                "Introduced multi-part source-of-wealth and address verification checklist "
                "without pre-submission validation, increasing incomplete submissions and rework."
            ),
            "affected_teams": "All Regions",
        },
        {
            "change_id": "PC-002",
            "change_code": "NORTH-TEAM-REORG",
            "title": "North Region Premier Advisory Staffing Reduction",
            "target_stage": "Ongoing Service",
            "target_category": "All Service Categories",
            "effective_date": CAPACITY_CHANGE_DATE,
            "description": (
                "Two senior advisors departed T-03 without immediate backfill, reducing active "
                "team capacity by 33% and concentrating open case backlog."
            ),
            "affected_teams": "T-03",
        },
        {
            "change_id": "PC-003",
            "change_code": "CUSTODY-XFER-AUTO",
            "title": "Custodial Transfer Automation Rollout",
            "target_stage": "Ongoing Service",
            "target_category": "Transfer & Settlement",
            "effective_date": TRANSFER_CHANGE_DATE,
            "description": (
                "New automated ACATS/custodial transfer routing introduced edge-case mismatches "
                "for multi-custodian accounts, driving Transfer & Settlement complaints."
            ),
            "affected_teams": "T-01,T-02,T-03,T-05",
        },
    ]

    # Pre-allocate output lists
    clients: list[dict[str, Any]] = []
    advisor_assignments: list[dict[str, Any]] = []
    client_accounts: list[dict[str, Any]] = []
    episodes: list[dict[str, Any]] = []
    journey_events: list[dict[str, Any]] = []
    service_cases: list[dict[str, Any]] = []
    case_events: list[dict[str, Any]] = []
    complaints: list[dict[str, Any]] = []
    interactions: list[dict[str, Any]] = []
    follow_ups: list[dict[str, Any]] = []
    status_events: list[dict[str, Any]] = []

    total_span_days = (AS_OF_DATE - START_DATE).days - 2
    team_ids = [t[0] for t in TEAMS_SPEC]

    ep_counter = 1
    ev_counter = 1
    case_counter = 1
    cev_counter = 1
    cmp_counter = 1
    int_counter = 1
    fu_counter = 1
    se_counter = 1

    for idx in range(1, n_clients + 1):
        cid = f"C-{idx:06d}"
        segment = str(rng.choice(SEGMENTS, p=SEGMENT_PROBS))
        asset_tier, (aum_low, aum_high) = TIER_BY_SEGMENT[segment]
        aum_usd = round(float(rng.uniform(aum_low, aum_high)), 2)
        channel = str(rng.choice(CHANNELS, p=CHANNEL_PROBS))
        t_id = str(rng.choice(team_ids))
        region = team_region[t_id]

        # Slight upward volume trend in 2025-2026
        u_time = float(rng.random())
        day_offset = int((u_time ** 0.92) * total_span_days)
        prospect_dt = START_DATE + timedelta(
            days=day_offset,
            hours=int(rng.integers(0, 8)),
            minutes=int(rng.integers(0, 60)),
        )

        # Pick advisor (before capacity change, T-03 had 6 advisors; after, 4 active)
        adv_id = str(rng.choice(team_advisors_active[t_id]))

        advisor_assignments.append(
            {
                "assignment_id": f"ASN-{idx:06d}-01",
                "client_id": cid,
                "advisor_id": adv_id,
                "team_id": t_id,
                "assigned_at": prospect_dt,
                "unassigned_at": None,
                "is_primary": True,
                "assignment_reason": "Initial Onboarding Assignment",
            }
        )

        # Stage 1: Prospect
        prospect_dur_h = float(rng.uniform(12, 72))
        cur_dt = prospect_dt
        ep1_id = f"EP-{ep_counter:07d}"
        ep_counter += 1
        prospect_exit = cur_dt + timedelta(hours=prospect_dur_h)
        if prospect_exit > AS_OF_DATE:
            episodes.append(
                {
                    "episode_id": ep1_id,
                    "client_id": cid,
                    "stage": "Prospect",
                    "entered_at": cur_dt,
                    "exited_at": None,
                    "assigned_team_id": t_id,
                    "assigned_advisor_id": adv_id,
                    "outcome": "In Progress",
                    "rework_reason": None,
                    "previous_episode_id": None,
                }
            )
            journey_events.append(
                {
                    "event_id": f"JEV-{ev_counter:08d}",
                    "client_id": cid,
                    "episode_id": ep1_id,
                    "event_type": "Prospect created",
                    "event_timestamp": cur_dt,
                    "actor_type": "System",
                    "actor_id": adv_id,
                    "summary": f"Prospect {cid} entered {channel} pipeline ({segment}).",
                    "metadata_json": {"channel": channel},
                }
            )
            ev_counter += 1
            clients.append(
                {
                    "client_id": cid,
                    "segment": segment,
                    "asset_tier": asset_tier,
                    "region": region,
                    "acquisition_channel": channel,
                    "prospect_created_at": prospect_dt,
                    "activated_at": None,
                    "exited_at": None,
                    "exit_reason": None,
                    "lifecycle_status": "Prospect",
                    "aum_usd": aum_usd,
                }
            )
            continue

        episodes.append(
            {
                "episode_id": ep1_id,
                "client_id": cid,
                "stage": "Prospect",
                "entered_at": cur_dt,
                "exited_at": prospect_exit,
                "assigned_team_id": t_id,
                "assigned_advisor_id": adv_id,
                "outcome": "Completed",
                "rework_reason": None,
                "previous_episode_id": None,
            }
        )
        journey_events.append(
            {
                "event_id": f"JEV-{ev_counter:08d}",
                "client_id": cid,
                "episode_id": ep1_id,
                "event_type": "Prospect created",
                "event_timestamp": cur_dt,
                "actor_type": "System",
                "actor_id": adv_id,
                "summary": f"Prospect {cid} entered {channel} pipeline ({segment}).",
                "metadata_json": {"channel": channel},
            }
        )
        ev_counter += 1
        cur_dt = prospect_exit

        # Stage 2: KYC (Story A: post 2026-04-01 has higher rework & longer tail)
        post_kyc_change = cur_dt >= KYC_CHANGE_DATE
        rework_prob = 0.285 if post_kyc_change else 0.098
        # Higher asset tiers have slightly cleaner pre-submission docs
        if asset_tier in ("Tier 3 ($1M-$5M)", "Tier 4 ($5M+)"):
            rework_prob *= 0.80

        kyc_reworked = bool(rng.random() < rework_prob)
        kyc_base_days = float(rng.lognormal(mean=1.45 if post_kyc_change else 1.05, sigma=0.55))
        kyc_ep1_id = f"EP-{ep_counter:07d}"
        ep_counter += 1

        journey_events.append(
            {
                "event_id": f"JEV-{ev_counter:08d}",
                "client_id": cid,
                "episode_id": kyc_ep1_id,
                "event_type": "KYC submitted",
                "event_timestamp": cur_dt,
                "actor_type": "Client",
                "actor_id": cid,
                "summary": "Initial KYC & identity verification package submitted.",
                "metadata_json": {"checklist_version": "v2.4" if post_kyc_change else "v2.3"},
            }
        )
        ev_counter += 1

        abandoned = False
        in_progress_onboarding = False
        kyc_cycles = 1

        if kyc_reworked:
            reason = (
                str(rng.choice(KYC_REWORK_REASONS, p=[0.38, 0.34, 0.16, 0.12]))
                if post_kyc_change
                else str(rng.choice(KYC_REWORK_REASONS, p=[0.32, 0.18, 0.28, 0.22]))
            )
            rework_dt = cur_dt + timedelta(hours=max(12.0, kyc_base_days * 12.0))
            if rework_dt > AS_OF_DATE:
                episodes.append(
                    {
                        "episode_id": kyc_ep1_id,
                        "client_id": cid,
                        "stage": "KYC",
                        "entered_at": cur_dt,
                        "exited_at": None,
                        "assigned_team_id": t_id,
                        "assigned_advisor_id": adv_id,
                        "outcome": "In Progress",
                        "rework_reason": None,
                        "previous_episode_id": None,
                    }
                )
                in_progress_onboarding = True
            else:
                episodes.append(
                    {
                        "episode_id": kyc_ep1_id,
                        "client_id": cid,
                        "stage": "KYC",
                        "entered_at": cur_dt,
                        "exited_at": rework_dt,
                        "assigned_team_id": t_id,
                        "assigned_advisor_id": adv_id,
                        "outcome": "Reopened",
                        "rework_reason": reason,
                        "previous_episode_id": None,
                    }
                )
                journey_events.append(
                    {
                        "event_id": f"JEV-{ev_counter:08d}",
                        "client_id": cid,
                        "episode_id": kyc_ep1_id,
                        "event_type": "KYC returned for missing documents",
                        "event_timestamp": rework_dt,
                        "actor_type": "Compliance",
                        "actor_id": "COMP-OPS",
                        "summary": f"KYC returned: {reason}.",
                        "metadata_json": {"rework_reason": reason},
                    }
                )
                ev_counter += 1

                # Rework cycle 2
                kyc_cycles = 2
                kyc_ep2_id = f"EP-{ep_counter:07d}"
                ep_counter += 1
                resubmit_dt = rework_dt + timedelta(hours=float(rng.uniform(18, 72)))
                if resubmit_dt > AS_OF_DATE:
                    episodes.append(
                        {
                            "episode_id": kyc_ep2_id,
                            "client_id": cid,
                            "stage": "KYC",
                            "entered_at": rework_dt,
                            "exited_at": None,
                            "assigned_team_id": t_id,
                            "assigned_advisor_id": adv_id,
                            "outcome": "In Progress",
                            "rework_reason": reason,
                            "previous_episode_id": kyc_ep1_id,
                        }
                    )
                    in_progress_onboarding = True
                else:
                    journey_events.append(
                        {
                            "event_id": f"JEV-{ev_counter:08d}",
                            "client_id": cid,
                            "episode_id": kyc_ep2_id,
                            "event_type": "KYC resubmitted",
                            "event_timestamp": resubmit_dt,
                            "actor_type": "Client",
                            "actor_id": cid,
                            "summary": "Client resubmitted corrected KYC documentation.",
                            "metadata_json": {"cycle": 2},
                        }
                    )
                    ev_counter += 1

                    # Abandonment risk higher after rework
                    if rng.random() < 0.11:
                        abandon_dt = _clamp_dt(resubmit_dt + timedelta(days=float(rng.uniform(2, 6))))
                        episodes.append(
                            {
                                "episode_id": kyc_ep2_id,
                                "client_id": cid,
                                "stage": "KYC",
                                "entered_at": rework_dt,
                                "exited_at": abandon_dt,
                                "assigned_team_id": t_id,
                                "assigned_advisor_id": adv_id,
                                "outcome": "Cancelled",
                                "rework_reason": reason,
                                "previous_episode_id": kyc_ep1_id,
                            }
                        )
                        abandoned = True
                    else:
                        kyc_done_dt = resubmit_dt + timedelta(
                            hours=float(rng.uniform(24, 96 if post_kyc_change else 56))
                        )
                        if kyc_done_dt > AS_OF_DATE:
                            episodes.append(
                                {
                                    "episode_id": kyc_ep2_id,
                                    "client_id": cid,
                                    "stage": "KYC",
                                    "entered_at": rework_dt,
                                    "exited_at": None,
                                    "assigned_team_id": t_id,
                                    "assigned_advisor_id": adv_id,
                                    "outcome": "In Progress",
                                    "rework_reason": reason,
                                    "previous_episode_id": kyc_ep1_id,
                                }
                            )
                            in_progress_onboarding = True
                        else:
                            episodes.append(
                                {
                                    "episode_id": kyc_ep2_id,
                                    "client_id": cid,
                                    "stage": "KYC",
                                    "entered_at": rework_dt,
                                    "exited_at": kyc_done_dt,
                                    "assigned_team_id": t_id,
                                    "assigned_advisor_id": adv_id,
                                    "outcome": "Completed",
                                    "rework_reason": reason,
                                    "previous_episode_id": kyc_ep1_id,
                                }
                            )
                            cur_dt = kyc_done_dt
        else:
            kyc_done_dt = cur_dt + timedelta(hours=max(16.0, kyc_base_days * 24.0))
            if kyc_done_dt > AS_OF_DATE:
                episodes.append(
                    {
                        "episode_id": kyc_ep1_id,
                        "client_id": cid,
                        "stage": "KYC",
                        "entered_at": cur_dt,
                        "exited_at": None,
                        "assigned_team_id": t_id,
                        "assigned_advisor_id": adv_id,
                        "outcome": "In Progress",
                        "rework_reason": None,
                        "previous_episode_id": None,
                    }
                )
                in_progress_onboarding = True
            elif rng.random() < 0.045:
                episodes.append(
                    {
                        "episode_id": kyc_ep1_id,
                        "client_id": cid,
                        "stage": "KYC",
                        "entered_at": cur_dt,
                        "exited_at": kyc_done_dt,
                        "assigned_team_id": t_id,
                        "assigned_advisor_id": adv_id,
                        "outcome": "Cancelled",
                        "rework_reason": None,
                        "previous_episode_id": None,
                    }
                )
                abandoned = True
            else:
                episodes.append(
                    {
                        "episode_id": kyc_ep1_id,
                        "client_id": cid,
                        "stage": "KYC",
                        "entered_at": cur_dt,
                        "exited_at": kyc_done_dt,
                        "assigned_team_id": t_id,
                        "assigned_advisor_id": adv_id,
                        "outcome": "Completed",
                        "rework_reason": None,
                        "previous_episode_id": None,
                    }
                )
                cur_dt = kyc_done_dt

        if abandoned or in_progress_onboarding:
            clients.append(
                {
                    "client_id": cid,
                    "segment": segment,
                    "asset_tier": asset_tier,
                    "region": region,
                    "acquisition_channel": channel,
                    "prospect_created_at": prospect_dt,
                    "activated_at": None,
                    "exited_at": None,
                    "exit_reason": "Onboarding Abandoned" if abandoned else None,
                    "lifecycle_status": "Abandoned" if abandoned else "Onboarding",
                    "aum_usd": aum_usd,
                }
            )
            continue

        # Stages 3-6: Account Opening -> Funding -> First Advisor Meeting -> Portfolio Setup
        remaining_stages = [
            ("Account Opening", "Account opened", (18.0, 72.0), 0.025),
            ("Funding", "First funding completed", (24.0, 140.0), 0.035),
            ("First Advisor Meeting", "Advisor meeting scheduled", (24.0, 120.0), 0.015),
            ("Portfolio Setup", "Portfolio setup completed", (18.0, 96.0), 0.010),
        ]

        activated_dt: datetime | None = None
        account_opened_dt: datetime | None = None

        for stg_name, ev_name, (h_min, h_max), drop_prob in remaining_stages:
            stg_ep_id = f"EP-{ep_counter:07d}"
            ep_counter += 1
            dur_h = float(rng.uniform(h_min, h_max))
            next_dt = cur_dt + timedelta(hours=dur_h)

            if next_dt > AS_OF_DATE:
                episodes.append(
                    {
                        "episode_id": stg_ep_id,
                        "client_id": cid,
                        "stage": stg_name,
                        "entered_at": cur_dt,
                        "exited_at": None,
                        "assigned_team_id": t_id,
                        "assigned_advisor_id": adv_id,
                        "outcome": "In Progress",
                        "rework_reason": None,
                        "previous_episode_id": None,
                    }
                )
                in_progress_onboarding = True
                break

            if rng.random() < drop_prob:
                episodes.append(
                    {
                        "episode_id": stg_ep_id,
                        "client_id": cid,
                        "stage": stg_name,
                        "entered_at": cur_dt,
                        "exited_at": next_dt,
                        "assigned_team_id": t_id,
                        "assigned_advisor_id": adv_id,
                        "outcome": "Cancelled",
                        "rework_reason": None,
                        "previous_episode_id": None,
                    }
                )
                abandoned = True
                break

            episodes.append(
                {
                    "episode_id": stg_ep_id,
                    "client_id": cid,
                    "stage": stg_name,
                    "entered_at": cur_dt,
                    "exited_at": next_dt,
                    "assigned_team_id": t_id,
                    "assigned_advisor_id": adv_id,
                    "outcome": "Completed",
                    "rework_reason": None,
                    "previous_episode_id": None,
                }
            )
            journey_events.append(
                {
                    "event_id": f"JEV-{ev_counter:08d}",
                    "client_id": cid,
                    "episode_id": stg_ep_id,
                    "event_type": ev_name,
                    "event_timestamp": next_dt,
                    "actor_type": "Advisor" if "Advisor" in stg_name else "Operations",
                    "actor_id": adv_id,
                    "summary": f"{ev_name} for {cid}.",
                    "metadata_json": None,
                }
            )
            ev_counter += 1

            if stg_name == "Account Opening":
                account_opened_dt = next_dt
            if stg_name == "Funding":
                activated_dt = next_dt
            cur_dt = next_dt

        if abandoned or in_progress_onboarding or activated_dt is None:
            clients.append(
                {
                    "client_id": cid,
                    "segment": segment,
                    "asset_tier": asset_tier,
                    "region": region,
                    "acquisition_channel": channel,
                    "prospect_created_at": prospect_dt,
                    "activated_at": None,
                    "exited_at": None,
                    "exit_reason": "Onboarding Abandoned" if abandoned else None,
                    "lifecycle_status": "Abandoned" if abandoned else "Onboarding",
                    "aum_usd": aum_usd,
                }
            )
            continue

        # Client is activated! Create account
        acct_type = "Private Trust" if asset_tier in ("Tier 3 ($1M-$5M)", "Tier 4 ($5M+)") else "Managed Advisory"
        client_accounts.append(
            {
                "account_id": f"ACC-{idx:06d}-01",
                "client_id": cid,
                "account_type": acct_type,
                "opened_at": account_opened_dt or activated_dt,
                "funded_at": activated_dt,
                "closed_at": None,
                "status": "Active",
                "initial_funding_usd": aum_usd,
            }
        )

        # Stage 7: Ongoing Service Episode (entered at portfolio setup completion)
        ongoing_ep_id = f"EP-{ep_counter:07d}"
        ep_counter += 1

        # Generate service cases for this activated client
        tenure_days = max(1, (AS_OF_DATE - activated_dt).days)
        avg_cases_per_year = {
            "Tier 1 (<$250K)": 2.4,
            "Tier 2 ($250K-$1M)": 3.2,
            "Tier 3 ($1M-$5M)": 4.2,
            "Tier 4 ($5M+)": 5.4,
        }[asset_tier]
        expected_cases = max(0.4, avg_cases_per_year * (tenure_days / 365.0))
        n_cases = int(rng.poisson(expected_cases))

        # Extra onboarding support cases if KYC reworked or post-KYC change
        if kyc_reworked and rng.random() < 0.55:
            n_cases += 1

        early_breaches = 0
        early_landmark_dt = activated_dt + timedelta(days=90)
        client_cases_created: list[tuple[datetime, bool]] = []

        for c_i in range(n_cases):
            # Bias early cases for some clients
            if c_i == 0 and rng.random() < 0.45 and tenure_days > 10:
                c_day = int(rng.integers(1, min(89, tenure_days)))
            else:
                c_day = int(rng.integers(0, tenure_days))
            case_dt = activated_dt + timedelta(
                days=c_day,
                hours=int(rng.integers(9, 17)),
                minutes=int(rng.integers(0, 59)),
            )
            if case_dt > AS_OF_DATE:
                continue

            # Category probabilities (Story A & E)
            cat_probs = [0.24, 0.22, 0.16, 0.16, 0.12, 0.10]
            if case_dt >= KYC_CHANGE_DATE and c_day < 60:
                cat_probs = [0.20, 0.18, 0.14, 0.14, 0.26, 0.08]
            elif case_dt >= TRANSFER_CHANGE_DATE:
                cat_probs = [0.21, 0.20, 0.15, 0.24, 0.10, 0.10]
            cat = str(rng.choice(CASE_CATEGORIES, p=cat_probs))
            comp = str(rng.choice(["Low", "Medium", "High"], p=[0.45, 0.38, 0.17]))
            fr_sla_h, res_sla_h = sla_lookup[(cat, comp)]

            fr_due = add_business_hours(case_dt, fr_sla_h)
            res_due = add_business_hours(case_dt, res_sla_h)

            # Story D (Confounding): Higher tier clients get faster service
            base_breach_prob = {
                "Tier 1 (<$250K)": 0.21,
                "Tier 2 ($250K-$1M)": 0.16,
                "Tier 3 ($1M-$5M)": 0.09,
                "Tier 4 ($5M+)": 0.05,
            }[asset_tier]

            # Story B: T-03 capacity pressure after 2026-05-15
            is_t3_stressed = t_id == "T-03" and case_dt >= CAPACITY_CHANGE_DATE
            if is_t3_stressed:
                base_breach_prob = min(0.68, base_breach_prob + 0.30)

            will_breach_fr = bool(rng.random() < base_breach_prob)
            if will_breach_fr:
                fr_mult = float(rng.uniform(1.15, 2.8 if not is_t3_stressed else 4.2))
            else:
                fr_mult = float(rng.uniform(0.15, 0.92))

            fr_dt = add_business_hours(case_dt, fr_sla_h * fr_mult)

            # Determine if case is still open as of AS_OF_DATE
            age_days = (AS_OF_DATE - case_dt).total_seconds() / 86400.0
            open_prob = 0.0
            if age_days < 3:
                open_prob = 0.72
            elif age_days < 10:
                open_prob = 0.32 if not is_t3_stressed else 0.58
            elif age_days < 25:
                open_prob = 0.06 if not is_t3_stressed else 0.35
            elif is_t3_stressed and age_days < 60:
                open_prob = 0.18

            is_still_open = bool(rng.random() < open_prob)
            first_response_at: datetime | None = None
            resolved_at: datetime | None = None
            status = "Closed"

            if fr_dt <= AS_OF_DATE and not (is_still_open and rng.random() < 0.40):
                first_response_at = fr_dt

            fr_breached = False
            if first_response_at is not None:
                fr_breached = first_response_at > fr_due
            elif fr_due <= AS_OF_DATE:
                fr_breached = True

            if not is_still_open:
                res_mult = float(rng.uniform(0.25, 1.45 if not is_t3_stressed else 2.6))
                cand_res = add_business_hours(case_dt, res_sla_h * res_mult)
                if cand_res <= AS_OF_DATE:
                    if first_response_at is not None and cand_res < first_response_at:
                        cand_res = first_response_at + timedelta(hours=1)
                    if cand_res <= AS_OF_DATE:
                        resolved_at = cand_res
                        status = "Closed" if rng.random() < 0.78 else "Resolved"
                    else:
                        status = "In Progress"
                else:
                    status = "In Progress"
            else:
                status = "Open" if first_response_at is None else "In Progress"

            res_breached = False
            if resolved_at is not None:
                res_breached = resolved_at > res_due
            elif res_due <= AS_OF_DATE:
                res_breached = True

            reopen_count = 1 if (resolved_at and rng.random() < (0.14 if is_t3_stressed else 0.05)) else 0
            repeat_contact = 1 if (fr_breached or reopen_count > 0) and rng.random() < 0.45 else 0

            case_id = f"CAS-{case_counter:07d}"
            case_counter += 1
            channel_c = str(rng.choice(["Portal", "Email", "Phone", "Advisor"]))

            service_cases.append(
                {
                    "case_id": case_id,
                    "client_id": cid,
                    "assigned_advisor_id": adv_id,
                    "assigned_team_id": t_id,
                    "request_category": cat,
                    "complexity_level": comp,
                    "status": status,
                    "created_at": case_dt,
                    "first_response_at": first_response_at,
                    "first_response_due_at": fr_due,
                    "first_response_breached": fr_breached,
                    "resolved_at": resolved_at,
                    "resolution_due_at": res_due,
                    "resolution_breached": res_breached,
                    "reopen_count": reopen_count,
                    "repeat_contact_count": repeat_contact,
                    "channel": channel_c,
                }
            )

            case_events.append(
                {
                    "event_id": f"CEV-{cev_counter:08d}",
                    "case_id": case_id,
                    "event_type": "Case Created",
                    "event_timestamp": case_dt,
                    "actor_id": cid,
                    "notes": f"{cat} ({comp}) opened via {channel_c}.",
                }
            )
            cev_counter += 1

            if first_response_at is not None:
                case_events.append(
                    {
                        "event_id": f"CEV-{cev_counter:08d}",
                        "case_id": case_id,
                        "event_type": "First Response Sent",
                        "event_timestamp": first_response_at,
                        "actor_id": adv_id,
                        "notes": "SLA breached" if fr_breached else "Within SLA",
                    }
                )
                cev_counter += 1

            if case_dt <= early_landmark_dt and fr_breached:
                early_breaches += 1

            client_cases_created.append((case_dt, fr_breached))

            # Follow-up task for ~40% of cases
            if rng.random() < 0.40:
                fu_due = add_business_hours(case_dt, 24.0)
                fu_done = None
                fu_status = "Pending"
                if not is_t3_stressed or rng.random() < 0.45:
                    cand_fu = fu_due - timedelta(hours=float(rng.uniform(-8, 12)))
                    if cand_fu <= AS_OF_DATE and cand_fu > case_dt:
                        fu_done = cand_fu
                        fu_status = "Completed"
                elif fu_due < AS_OF_DATE:
                    fu_status = "Overdue"
                follow_ups.append(
                    {
                        "task_id": f"FUT-{fu_counter:07d}",
                        "client_id": cid,
                        "case_id": case_id,
                        "advisor_id": adv_id,
                        "due_at": fu_due,
                        "completed_at": fu_done,
                        "status": fu_status,
                        "task_type": "Post-Service Follow-Up",
                    }
                )
                fu_counter += 1

            # Story E: Complaint generation
            cmp_prob = 0.035
            if cat == "Transfer & Settlement" and case_dt >= TRANSFER_CHANGE_DATE and t_id in ("T-01", "T-02", "T-03", "T-05"):
                cmp_prob = 0.24
            elif fr_breached:
                cmp_prob = 0.11

            if rng.random() < cmp_prob:
                cmp_dt = _clamp_dt(case_dt + timedelta(hours=float(rng.uniform(4, 48))))
                cmp_res = None
                if rng.random() < (0.72 if age_days > 10 else 0.40):
                    cand_cmp_res = cmp_dt + timedelta(days=float(rng.uniform(1.5, 9.0)))
                    if cand_cmp_res <= AS_OF_DATE:
                        cmp_res = cand_cmp_res
                reopened_cmp = bool(cmp_res and rng.random() < (0.22 if cat == "Transfer & Settlement" else 0.07))
                complaints.append(
                    {
                        "complaint_id": f"CMP-{cmp_counter:06d}",
                        "client_id": cid,
                        "case_id": case_id,
                        "assigned_team_id": t_id,
                        "category": cat,
                        "severity": str(rng.choice(["Low", "Medium", "High"], p=[0.35, 0.45, 0.20])),
                        "submitted_at": cmp_dt,
                        "resolved_at": cmp_res,
                        "reopened": reopened_cmp,
                        "reopen_count": 1 if reopened_cmp else 0,
                        "repeat_contact_flag": bool(reopened_cmp or rng.random() < 0.25),
                        "root_cause_process": "Custodial Transfer Automation" if cat == "Transfer & Settlement" and case_dt >= TRANSFER_CHANGE_DATE else None,
                    }
                )
                cmp_counter += 1
                journey_events.append(
                    {
                        "event_id": f"JEV-{ev_counter:08d}",
                        "client_id": cid,
                        "episode_id": ongoing_ep_id,
                        "event_type": "Complaint submitted",
                        "event_timestamp": cmp_dt,
                        "actor_type": "Client",
                        "actor_id": cid,
                        "summary": f"Complaint filed under {cat}.",
                        "metadata_json": {"category": cat},
                    }
                )
                ev_counter += 1

        # Story C & D: Post-activation retention / exit hazard
        # Baseline annual exit hazard by tier (confounder)
        annual_hazard = {
            "Tier 1 (<$250K)": 0.105,
            "Tier 2 ($250K-$1M)": 0.072,
            "Tier 3 ($1M-$5M)": 0.042,
            "Tier 4 ($5M+)": 0.028,
        }[asset_tier]

        # Early SLA breach multiplier (Story C)
        if early_breaches == 1:
            annual_hazard *= 1.65
        elif early_breaches >= 2:
            annual_hazard *= 2.85

        # KYC rework mild carryover
        if kyc_cycles > 1:
            annual_hazard *= 1.22

        # Simulate exit probability over observed tenure
        obs_years = tenure_days / 365.0
        exit_prob = 1.0 - math.exp(-annual_hazard * obs_years)
        exited_dt: datetime | None = None
        exit_reason: str | None = None
        lifecycle_status = "Active"

        if rng.random() < exit_prob and tenure_days > 14:
            # Draw exit time within (activated_dt + 14d, AS_OF_DATE)
            ex_day = int(rng.integers(14, tenure_days))
            exited_dt = activated_dt + timedelta(days=ex_day, hours=16)
            if exited_dt <= AS_OF_DATE:
                lifecycle_status = "Exited"
                exit_reason = str(rng.choice(EXIT_REASONS, p=[0.22, 0.34 if early_breaches > 0 else 0.18, 0.22, 0.12, 0.10 if early_breaches > 0 else 0.26]))
                client_accounts[-1]["closed_at"] = exited_dt
                client_accounts[-1]["status"] = "Closed"
                journey_events.append(
                    {
                        "event_id": f"JEV-{ev_counter:08d}",
                        "client_id": cid,
                        "episode_id": ongoing_ep_id,
                        "event_type": "Client exited",
                        "event_timestamp": exited_dt,
                        "actor_type": "Client",
                        "actor_id": cid,
                        "summary": f"Account closed ({exit_reason}).",
                        "metadata_json": {"exit_reason": exit_reason},
                    }
                )
                ev_counter += 1
            else:
                exited_dt = None

        episodes.append(
            {
                "episode_id": ongoing_ep_id,
                "client_id": cid,
                "stage": "Ongoing Service",
                "entered_at": cur_dt,
                "exited_at": exited_dt,
                "assigned_team_id": t_id,
                "assigned_advisor_id": adv_id,
                "outcome": "Exited" if exited_dt else "In Progress",
                "rework_reason": None,
                "previous_episode_id": None,
            }
        )

        # Client interactions (for engagement / inactivity tracking)
        end_int_dt = exited_dt or AS_OF_DATE
        int_span_days = max(1, (end_int_dt - activated_dt).days)
        n_ints = max(1, int(rng.poisson(max(1.0, int_span_days / 75.0))))
        last_int_dt = activated_dt
        for _ in range(n_ints):
            i_dt = activated_dt + timedelta(days=int(rng.integers(0, int_span_days)), hours=11)
            if i_dt > last_int_dt:
                last_int_dt = i_dt
            interactions.append(
                {
                    "interaction_id": f"INT-{int_counter:07d}",
                    "client_id": cid,
                    "advisor_id": adv_id,
                    "interaction_type": str(rng.choice(["Portfolio Review", "Advisory Call", "Portal Check-in", "Service Touchpoint"])),
                    "qualifying_engagement": True,
                    "occurred_at": i_dt,
                    "channel": str(rng.choice(["Video", "Phone", "In-Person", "Portal"])),
                    "summary": "Scheduled wealth advisory touchpoint.",
                }
            )
            int_counter += 1

        # Deterministic At-Risk / Inactive status event
        days_since_contact = (AS_OF_DATE - last_int_dt).days
        if exited_dt is None and (early_breaches >= 2 or days_since_contact > 90):
            reasons = []
            if early_breaches >= 2:
                reasons.append(f"{early_breaches} early SLA breaches")
            if days_since_contact > 90:
                reasons.append(f"{days_since_contact}d since last qualifying contact")
            status_events.append(
                {
                    "status_event_id": f"CSE-{se_counter:07d}",
                    "client_id": cid,
                    "status_type": "Engagement",
                    "status_value": "At Risk" if early_breaches >= 2 else "Inactive",
                    "effective_at": AS_OF_DATE - timedelta(days=1),
                    "rule_reason": "; ".join(reasons),
                }
            )
            se_counter += 1

        clients.append(
            {
                "client_id": cid,
                "segment": segment,
                "asset_tier": asset_tier,
                "region": region,
                "acquisition_channel": channel,
                "prospect_created_at": prospect_dt,
                "activated_at": activated_dt,
                "exited_at": exited_dt,
                "exit_reason": exit_reason,
                "lifecycle_status": lifecycle_status,
                "aum_usd": aum_usd,
            }
        )

    # 4. Starter Recommendations & Experiments (Section 14)
    recommendations = [
        {
            "recommendation_id": "REC-001",
            "title": "KYC Pre-Submission Validation Checker",
            "target_process": "Onboarding — KYC & Documentation",
            "business_problem": "KYC rework rate rose sharply after the v2.4 checklist rollout, extending p90 onboarding duration and increasing support inquiries.",
            "supporting_evidence": "Post-2026-04-01 KYC episodes show elevated Reopened rates driven by Missing identity documentation and Checklist clarification.",
            "hypothesis": "A pre-submission document validation checklist reduces incomplete KYC applications and repeat submissions.",
            "suggested_intervention": "Deploy an interactive advisor/client pre-submission completeness check before compliance queue entry.",
            "success_metric": "KYC rework rate",
            "guardrail_metric": "Median KYC completion time, onboarding abandonment rate, advisor support burden",
            "experiment_design": "Controlled regional/team pilot (East vs. West matched cohorts) over 8 weeks with contamination monitoring.",
            "stakeholder_owner": "Operations Lead & Compliance Representative",
            "implementation_effort": "Medium",
            "estimated_impact_range": "8–14 pp reduction in KYC rework rate",
            "dependencies": "Portal form schema update; Compliance sign-off on v2.4 rules",
            "risks": "Advisors bypassing checker via offline email; initial friction for complex trust structures",
            "rice_reach": 1200,
            "rice_impact": 2.5,
            "rice_confidence": 0.85,
            "rice_effort": 3.0,
            "rice_score": 850.0,
            "priority": "P0 — Critical",
            "status": "Proposed",
            "linked_requirement_id": "FR-ONB-002",
        },
        {
            "recommendation_id": "REC-002",
            "title": "Proactive Outreach After First Early SLA Breach",
            "target_process": "Ongoing Service — Early Lifecycle (Days 1–90)",
            "business_problem": "Clients experiencing 2+ SLA breaches in their first 90 days exhibit materially lower post-90-day retention.",
            "supporting_evidence": "Day-90 landmark Kaplan-Meier and asset-tier-adjusted comparisons show elevated attrition hazard for multi-breach cohorts.",
            "hypothesis": "Prompt senior advisor outreach within 24h of a first SLA miss improves subsequent engagement and reduces repeat breaches.",
            "suggested_intervention": "Trigger a mandatory Client Service Manager outreach task whenever a new client (<90d) experiences an SLA breach.",
            "success_metric": "Post-90-day engagement & retention at 180-day horizon",
            "guardrail_metric": "Complaint rate, client contact fatigue, advisor follow-up workload",
            "experiment_design": "Randomized eligible-client holdout (50/50 within tier strata) over 90 days.",
            "stakeholder_owner": "Client Service Manager",
            "implementation_effort": "Low",
            "estimated_impact_range": "2–5 pp improvement in 180d retention among breached cohort",
            "dependencies": "CRM SLA webhook; advisor task queue integration",
            "risks": "Unwanted outreach fatigue if paired with ongoing unresolved ticket",
            "rice_reach": 650,
            "rice_impact": 2.0,
            "rice_confidence": 0.75,
            "rice_effort": 1.5,
            "rice_score": 650.0,
            "priority": "P1 — High",
            "status": "Proposed",
            "linked_requirement_id": "FR-RET-004",
        },
        {
            "recommendation_id": "REC-003",
            "title": "Capacity-Based Service Case Routing",
            "target_process": "Service Operations — Case Triage & Assignment",
            "business_problem": "Staffing reduction in T-03 caused open backlog >15 days and first-response SLA breaches to concentrate in North Region.",
            "supporting_evidence": "T-03 utilization exceeded 100% post-2026-05-15 with p90 response times more than doubling.",
            "hypothesis": "Routing new non-relationship-specific cases according to real-time advisor capacity and complexity reduces backlog aging and response delays.",
            "suggested_intervention": "Implement weighted round-robin overflow routing across regional backup pools when team utilization exceeds 90%.",
            "success_metric": "p90 first-response time and first-response SLA breach rate",
            "guardrail_metric": "Case complexity balance, client satisfaction, reopen rate",
            "experiment_design": "Phased team pilot on T-03 with T-04 as comparable North control team.",
            "stakeholder_owner": "Operations Lead",
            "implementation_effort": "Medium",
            "estimated_impact_range": "25–40% reduction in aged backlog (>8 days)",
            "dependencies": "Advisor capacity threshold definitions; cross-team licensing check",
            "risks": "Loss of relationship context on overflowed complex cases",
            "rice_reach": 900,
            "rice_impact": 2.2,
            "rice_confidence": 0.80,
            "rice_effort": 3.0,
            "rice_score": 528.0,
            "priority": "P1 — High",
            "status": "Proposed",
            "linked_requirement_id": "FR-OPS-003",
        },
        {
            "recommendation_id": "REC-004",
            "title": "Automated Follow-Up SLA Reminders",
            "target_process": "Advisor Intelligence — Follow-Up Execution",
            "business_problem": "Overloaded teams show rising overdue follow-up tasks and repeat client contacts on unresolved issues.",
            "supporting_evidence": "Follow-up completion rates dropped in capacity-constrained teams alongside higher repeat-contact flags.",
            "hypothesis": "Timely pre-due reminders reduce unresolved follow-ups and repeated client contact.",
            "suggested_intervention": "Add 4-business-hour pre-due escalation alerts and daily digest for overdue follow-up tasks.",
            "success_metric": "Follow-up completion within SLA",
            "guardrail_metric": "Notification fatigue, advisor administrative time",
            "experiment_design": "Staged rollout across 4 teams with 6-week pre/post evaluation windows.",
            "stakeholder_owner": "Relationship Manager Lead",
            "implementation_effort": "Low",
            "estimated_impact_range": "10–18 pp increase in on-time follow-up completion",
            "dependencies": "Follow-up task due-date engine",
            "risks": "Alert desensitization if thresholds are too noisy",
            "rice_reach": 800,
            "rice_impact": 1.5,
            "rice_confidence": 0.80,
            "rice_effort": 2.0,
            "rice_score": 480.0,
            "priority": "P2 — Medium",
            "status": "Proposed",
            "linked_requirement_id": "FR-ADV-002",
        },
    ]

    experiments = [
        {
            "experiment_id": "EXP-001",
            "recommendation_id": "REC-001",
            "name": "KYC Pre-Submission Checker — Regional Pilot",
            "design_type": "Controlled Team Pilot (Difference-in-Differences)",
            "primary_metric": "KYC Rework Rate",
            "guardrail_metrics": "Median KYC Duration, Onboarding Abandonment Rate",
            "target_population": "New prospects entering KYC in East Region (Treatment) vs. West Region (Control)",
            "evaluation_window_days": 56,
            "status": "Proposed",
            "notes": "Pending Compliance sign-off on v2.4 validation rules. No treatment effect claimed yet.",
        },
        {
            "experiment_id": "EXP-002",
            "recommendation_id": "REC-002",
            "name": "Early SLA Breach Outreach — Stratified Holdout",
            "design_type": "Randomized Stratified Holdout (50/50)",
            "primary_metric": "180-Day Post-Breach Retention & Qualifying Engagement",
            "guardrail_metrics": "Complaint Rate, Follow-Up Workload",
            "target_population": "Activated clients (<90d tenure) experiencing first SLA breach",
            "evaluation_window_days": 90,
            "status": "Proposed",
            "notes": "Stratified by Asset Tier to control for client value confounding.",
        },
        {
            "experiment_id": "EXP-003",
            "recommendation_id": "REC-003",
            "name": "Capacity-Based Overflow Routing — T-03 Pilot",
            "design_type": "Phased Operational Pilot",
            "primary_metric": "p90 First-Response Business Hours",
            "guardrail_metrics": "Case Reopen Rate, Complexity Mix Balance",
            "target_population": "Incoming Low/Medium complexity cases assigned to T-03",
            "evaluation_window_days": 42,
            "status": "Proposed",
            "notes": "Overflow routed to T-04 when T-03 utilization > 90%.",
        },
        {
            "experiment_id": "EXP-004",
            "recommendation_id": "REC-004",
            "name": "Follow-Up SLA Alerting — Staged Rollout",
            "design_type": "Stepped-Wedge Staged Rollout",
            "primary_metric": "Follow-Up On-Time Completion Rate",
            "guardrail_metrics": "Repeat-Contact Rate, Advisor Alert Dismissals",
            "target_population": "All active advisors with open follow-up tasks",
            "evaluation_window_days": 42,
            "status": "Proposed",
            "notes": "Requires baseline 4-week pre-period comparison.",
        },
    ]

    # 5. Authoritative KPI Definitions (Section 17)
    metric_definitions = [
        {
            "metric_key": "active_clients",
            "kpi_name": "Active Clients",
            "business_meaning": "Total activated wealth management clients who have not formally exited as of the reporting end date.",
            "formula": "COUNT(DISTINCT client_id) WHERE activated_at <= end_date AND (exited_at IS NULL OR exited_at > end_date)",
            "numerator": "Activated clients without an exit timestamp on or before the as-of date",
            "denominator": "N/A (point-in-time count)",
            "time_basis": "Point-in-time as of period end date",
            "inclusion_criteria": "Clients with completed Funding / activation timestamp",
            "exclusions": "Prospects, in-progress onboarding, and onboarding abandonments",
            "data_source": "clients",
            "sql_template": "SELECT COUNT(*) FROM clients WHERE activated_at <= :end_date AND (exited_at IS NULL OR exited_at > :end_date);",
            "known_limitations": "Does not distinguish engaged vs. inactive clients; pair with Inactivity Rate.",
        },
        {
            "metric_key": "client_retention_rate",
            "kpi_name": "Client Retention Rate",
            "business_meaning": "Share of clients active at the start of the period who remained active through the end of the period.",
            "formula": "1 - (Exited in period / Active at period start)",
            "numerator": "Clients active at period start who did not exit during the period",
            "denominator": "Clients activated before period start and not exited before period start",
            "time_basis": "Reporting window (start_date to end_date)",
            "inclusion_criteria": "Activated clients at risk of exit at period start",
            "exclusions": "Clients activated during the period (handled in Cohort Retention)",
            "data_source": "clients",
            "sql_template": "SELECT 1.0 - (COUNT(*) FILTER (WHERE exited_at BETWEEN :start_date AND :end_date)::float / NULLIF(COUNT(*), 0)) FROM clients WHERE activated_at < :start_date AND (exited_at IS NULL OR exited_at >= :start_date);",
            "known_limitations": "Period retention mixes cohort tenures; use Retention Studio for mature cohort comparison.",
        },
        {
            "metric_key": "client_attrition_rate",
            "kpi_name": "Client Attrition Rate",
            "business_meaning": "Share of clients active at period start who formally exited during the reporting window.",
            "formula": "Exited in period / Active at period start",
            "numerator": "Clients with exited_at within [start_date, end_date]",
            "denominator": "Clients active at start_date",
            "time_basis": "Reporting window",
            "inclusion_criteria": "Formal account closures only",
            "exclusions": "Inactive clients without formal exit; onboarding abandonments",
            "data_source": "clients",
            "sql_template": "SELECT COUNT(*) FILTER (WHERE exited_at BETWEEN :start_date AND :end_date)::float / NULLIF(COUNT(*), 0) FROM clients WHERE activated_at < :start_date AND (exited_at IS NULL OR exited_at >= :start_date);",
            "known_limitations": "Lag between disengagement and formal account closure.",
        },
        {
            "metric_key": "inactivity_rate",
            "kpi_name": "Client Inactivity Rate",
            "business_meaning": "Percentage of active clients with no qualifying engagement in the past 90 days.",
            "formula": "Active clients with >90 days since last qualifying interaction / Total active clients",
            "numerator": "Active clients with last qualifying_engagement > 90 days before as_of_date",
            "denominator": "Total active clients with >= 90 days tenure",
            "time_basis": "Trailing 90 days from as-of date",
            "inclusion_criteria": "Active clients activated >90 days prior",
            "exclusions": "Recently activated clients (<90 days tenure)",
            "data_source": "clients, client_interactions",
            "sql_template": "SELECT COUNT(*) FILTER (WHERE last_contact < :as_of - INTERVAL '90 days')::float / NULLIF(COUNT(*), 0) FROM (...);",
            "known_limitations": "Inactivity is not automatic churn; some HNW clients prefer quarterly/annual contact.",
        },
        {
            "metric_key": "funnel_conversion",
            "kpi_name": "Onboarding Funnel Conversion",
            "business_meaning": "Percentage of stage-entering episodes that reach Completed status.",
            "formula": "Completed episodes / (Entered episodes excluding In Progress)",
            "numerator": "Stage episodes with outcome = 'Completed'",
            "denominator": "Closed stage episodes (Completed + Cancelled + Exited)",
            "time_basis": "Episode entered_at within reporting window",
            "inclusion_criteria": "Unique clients entering stage within window",
            "exclusions": "In-progress episodes still within SLA window are separated from failures",
            "data_source": "journey_stage_episodes",
            "sql_template": "SELECT stage, COUNT(*) FILTER (WHERE outcome = 'Completed')::float / NULLIF(COUNT(*) FILTER (WHERE outcome IN ('Completed','Cancelled','Exited')), 0) FROM journey_stage_episodes GROUP BY stage;",
            "known_limitations": "Recent cohorts have higher In Progress counts.",
        },
        {
            "metric_key": "stage_completion_time",
            "kpi_name": "Median Stage Completion Time",
            "business_meaning": "50th percentile duration in days from stage entry to stage exit for completed episodes.",
            "formula": "PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (exited_at - entered_at))/86400.0)",
            "numerator": "Elapsed calendar days for completed stage episodes",
            "denominator": "Completed stage episodes",
            "time_basis": "Episode entered_at within reporting window",
            "inclusion_criteria": "Completed episodes",
            "exclusions": "In-progress episodes (tracked separately via as-of elapsed time)",
            "data_source": "journey_stage_episodes",
            "sql_template": "SELECT stage, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (exited_at - entered_at))/86400.0) FROM journey_stage_episodes WHERE outcome = 'Completed' GROUP BY stage;",
            "known_limitations": "Excludes censored in-progress episodes.",
        },
        {
            "metric_key": "p90_stage_duration",
            "kpi_name": "p90 Stage Duration",
            "business_meaning": "90th percentile completion duration in days, capturing tail delays.",
            "formula": "PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY duration_days)",
            "numerator": "Elapsed days at 90th percentile",
            "denominator": "Completed stage episodes",
            "time_basis": "Episode entered_at within reporting window",
            "inclusion_criteria": "Completed episodes",
            "exclusions": "In-progress episodes",
            "data_source": "journey_stage_episodes",
            "sql_template": "SELECT stage, PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (exited_at - entered_at))/86400.0) FROM journey_stage_episodes WHERE outcome = 'Completed' GROUP BY stage;",
            "known_limitations": "Sensitive to small sample sizes in segmented views.",
        },
        {
            "metric_key": "stage_stall_rate",
            "kpi_name": "Stage Stall Rate",
            "business_meaning": "Share of active in-progress episodes exceeding 14 days without progression.",
            "formula": "In-progress episodes >14 days old / Total in-progress episodes",
            "numerator": "Episodes with outcome = 'In Progress' and (as_of - entered_at) > 14 days",
            "denominator": "All In Progress episodes in stage",
            "time_basis": "As of reporting end date",
            "inclusion_criteria": "Open stage episodes",
            "exclusions": "Completed or cancelled episodes",
            "data_source": "journey_stage_episodes",
            "sql_template": "SELECT stage, COUNT(*) FILTER (WHERE (:as_of - entered_at) > INTERVAL '14 days')::float / NULLIF(COUNT(*), 0) FROM journey_stage_episodes WHERE outcome = 'In Progress' GROUP BY stage;",
            "known_limitations": "Depends on timely stage exit logging.",
        },
        {
            "metric_key": "kyc_rework_rate",
            "kpi_name": "KYC Rework Rate",
            "business_meaning": "Percentage of KYC episodes that were reopened/returned for missing or mismatched documentation.",
            "formula": "Reopened KYC episodes / Total initial KYC episodes",
            "numerator": "KYC episodes with outcome = 'Reopened'",
            "denominator": "Initial KYC episodes (previous_episode_id IS NULL) entered in period",
            "time_basis": "Episode entered_at within reporting window",
            "inclusion_criteria": "All initial KYC submissions",
            "exclusions": "Subsequent resubmission episodes from denominator",
            "data_source": "journey_stage_episodes",
            "sql_template": "SELECT COUNT(*) FILTER (WHERE outcome = 'Reopened')::float / NULLIF(COUNT(*) FILTER (WHERE previous_episode_id IS NULL), 0) FROM journey_stage_episodes WHERE stage = 'KYC';",
            "known_limitations": "Rework spikes may reflect stricter compliance review rather than client error alone.",
        },
        {
            "metric_key": "first_response_sla_attainment",
            "kpi_name": "First-Response SLA Attainment",
            "business_meaning": "Percentage of due service cases that received a first response within configured business-hours SLA.",
            "formula": "Due cases with first_response_at <= first_response_due_at / Cases with first_response_due_at <= as_of_date",
            "numerator": "Eligible cases with first_response_breached = FALSE and first_response_at IS NOT NULL",
            "denominator": "Cases whose first_response_due_at fell on or before as_of_date (including breached unresponded cases)",
            "time_basis": "Case created_at within reporting window; business-hours calendar (Mon-Fri 09:00-17:00 ET)",
            "inclusion_criteria": "Cases with first_response_due_at <= as_of_date",
            "exclusions": "Open cases not yet due as of as_of_date",
            "data_source": "service_cases",
            "sql_template": "SELECT COUNT(*) FILTER (WHERE NOT first_response_breached AND first_response_at IS NOT NULL)::float / NULLIF(COUNT(*) FILTER (WHERE first_response_due_at <= :as_of), 0) FROM service_cases;",
            "known_limitations": "Clock time outside business hours is excluded from SLA calculations.",
        },
        {
            "metric_key": "resolution_sla_attainment",
            "kpi_name": "Resolution SLA Attainment",
            "business_meaning": "Percentage of due service cases resolved within their business-hours resolution SLA.",
            "formula": "Due cases resolved on time / Cases with resolution_due_at <= as_of_date",
            "numerator": "Cases with resolved_at <= resolution_due_at",
            "denominator": "Cases with resolution_due_at <= as_of_date",
            "time_basis": "Case created_at within reporting window",
            "inclusion_criteria": "Cases past resolution due date",
            "exclusions": "Open cases not yet due",
            "data_source": "service_cases",
            "sql_template": "SELECT COUNT(*) FILTER (WHERE NOT resolution_breached AND resolved_at IS NOT NULL)::float / NULLIF(COUNT(*) FILTER (WHERE resolution_due_at <= :as_of), 0) FROM service_cases;",
            "known_limitations": "Complex multi-custodian transfers may pause externally.",
        },
        {
            "metric_key": "reopen_rate",
            "kpi_name": "Case Reopen Rate",
            "business_meaning": "Share of resolved/closed cases that were reopened at least once.",
            "formula": "Cases with reopen_count > 0 / Resolved or Closed cases",
            "numerator": "Cases with reopen_count > 0",
            "denominator": "Cases with status IN ('Resolved', 'Closed')",
            "time_basis": "Case created_at within reporting window",
            "inclusion_criteria": "Resolved/closed cases",
            "exclusions": "Still-open cases",
            "data_source": "service_cases",
            "sql_template": "SELECT COUNT(*) FILTER (WHERE reopen_count > 0)::float / NULLIF(COUNT(*) FILTER (WHERE status IN ('Resolved','Closed')), 0) FROM service_cases;",
            "known_limitations": "Some client follow-ups open new cases instead of reopening.",
        },
        {
            "metric_key": "repeat_contact_rate",
            "kpi_name": "Repeat-Contact Rate",
            "business_meaning": "Share of service cases involving repeated client inquiries before resolution.",
            "formula": "Cases with repeat_contact_count > 0 / Total cases",
            "numerator": "Cases with repeat_contact_count > 0",
            "denominator": "All service cases in period",
            "time_basis": "Case created_at within reporting window",
            "inclusion_criteria": "All service cases",
            "exclusions": "None",
            "data_source": "service_cases",
            "sql_template": "SELECT COUNT(*) FILTER (WHERE repeat_contact_count > 0)::float / NULLIF(COUNT(*), 0) FROM service_cases;",
            "known_limitations": "Captures intra-case repeat contacts.",
        },
        {
            "metric_key": "backlog_aging",
            "kpi_name": "Open Backlog & Aging Distribution",
            "business_meaning": "Count and share of currently open/in-progress cases segmented by age since creation (0-2d, 3-7d, 8-14d, 15+d).",
            "formula": "COUNT(*) FILTER (WHERE status IN ('Open','In Progress')) GROUP BY age_bucket",
            "numerator": "Open cases in each age bucket",
            "denominator": "Total open cases",
            "time_basis": "As of reporting end date",
            "inclusion_criteria": "Cases with status IN ('Open', 'In Progress')",
            "exclusions": "Resolved/Closed cases",
            "data_source": "service_cases",
            "sql_template": "SELECT CASE WHEN age <= 2 THEN '0-2d' WHEN age <= 7 THEN '3-7d' WHEN age <= 14 THEN '8-14d' ELSE '15+d' END, COUNT(*) FROM service_cases WHERE status IN ('Open','In Progress') GROUP BY 1;",
            "known_limitations": "Calendar-day aging rather than business-day aging.",
        },
        {
            "metric_key": "advisor_utilization",
            "kpi_name": "Advisor Capacity Utilization",
            "business_meaning": "Ratio of currently open cases to configured active case capacity (35 cases per active advisor).",
            "formula": "Open cases / (Active advisors * 35)",
            "numerator": "Cases with status IN ('Open', 'In Progress')",
            "denominator": "Active advisor headcount * max_active_cases (35)",
            "time_basis": "As of reporting end date",
            "inclusion_criteria": "Active advisors",
            "exclusions": "Departed/inactive advisors excluded from denominator",
            "data_source": "advisors, service_cases",
            "sql_template": "SELECT a.team_id, COUNT(sc.case_id)::float / NULLIF(SUM(CASE WHEN a.active THEN a.max_active_cases ELSE 0 END), 0) FROM advisors a LEFT JOIN service_cases sc ON sc.assigned_advisor_id = a.advisor_id AND sc.status IN ('Open','In Progress') GROUP BY a.team_id;",
            "known_limitations": "Equal-weight case capacity; does not weight by case complexity unless adjusted.",
        },
    ]

    return GeneratedDataset(
        teams=teams,
        advisors=advisors,
        sla_policies=sla_policies,
        process_changes=process_changes,
        clients=clients,
        advisor_assignments=advisor_assignments,
        client_accounts=client_accounts,
        journey_stage_episodes=episodes,
        journey_events=journey_events,
        service_cases=service_cases,
        service_case_events=case_events,
        complaints=complaints,
        client_interactions=interactions,
        follow_up_tasks=follow_ups,
        client_status_events=status_events,
        recommendations=recommendations,
        experiments=experiments,
        metric_definitions=metric_definitions,
    )
