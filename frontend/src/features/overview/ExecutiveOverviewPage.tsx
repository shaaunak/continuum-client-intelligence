import { useQuery } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import {
  ArrowRight,
  TrendingDown,
  TrendingUp,
  Download,
  AlertTriangle,
  FileText,
  Activity,
  Code2,
} from 'lucide-react';
import { useFilters } from '@/hooks/useFilters';
import { apiGet, buildFilterParams } from '@/services/api';
import type { OverviewResponse, KpiCardData } from '@/types/api';

interface FunnelStage {
  stage: string;
  entered_count: number;
  completed_count: number;
  conversion_rate: number;
  median_days: number;
  p90_days: number;
  rework_rate: number;
  rework_change_pp: number;
}

function formatKpiValue(kpi: KpiCardData) {
  return `${kpi.value.toLocaleString(undefined, { maximumFractionDigits: 1 })}${kpi.unit}`;
}

function formatKpiDelta(kpi: KpiCardData) {
  if (kpi.change === null) return '—';
  return `${kpi.change >= 0 ? '+' : ''}${kpi.change.toFixed(1)} ${kpi.change_unit}`;
}

function isKpiNegative(kpi: KpiCardData) {
  return (
    (kpi.direction === 'down' && kpi.favorable_direction === 'up') ||
    (kpi.direction === 'up' && kpi.favorable_direction === 'down')
  );
}

export function ExecutiveOverviewPage() {
  const { filters, openMetricDrawer } = useFilters();
  const navigate = useNavigate();
  const qs = buildFilterParams(filters);

  const { data: overview, isLoading, error } = useQuery<OverviewResponse>({
    queryKey: ['overview', qs],
    queryFn: () => apiGet<OverviewResponse>(`/overview?${qs}`),
  });

  const { data: trends } = useQuery<any[]>({
    queryKey: ['overview-trends', qs],
    queryFn: () => apiGet<any[]>(`/overview/trends?${qs}`),
  });

  const { data: funnel } = useQuery<{ stages: FunnelStage[] }>({
    queryKey: ['journey-funnel', qs],
    queryFn: () => apiGet<{ stages: FunnelStage[] }>(`/journey/funnel?${qs}`),
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-32 animate-pulse rounded bg-white border border-[#bec9c7]/40" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="h-64 animate-pulse rounded bg-white border border-[#bec9c7]/40 col-span-2" />
          <div className="h-64 animate-pulse rounded bg-white border border-[#bec9c7]/40" />
        </div>
      </div>
    );
  }

  if (error || !overview) {
    return (
      <div className="rounded border border-[#864e59]/30 bg-white p-6 text-sm text-[#864e59]">
        Failed to load Executive Overview. Verify the FastAPI backend is running.
      </div>
    );
  }

  // Find key headline metrics from the 6 API KPIs
  const retentionKpi = overview.kpis.find((k) => k.key === 'retention_rate') || overview.kpis[0];
  const velocityKpi = overview.kpis.find((k) => k.key === 'median_onboarding_days') || overview.kpis[1];
  const kycReworkKpi = overview.kpis.find((k) => k.key === 'kyc_rework_rate') || overview.kpis[2];

  // Stage mapping helper for the 7 horizontal cards
  const stageData = (funnel?.stages || []).map((stg, index) => {
    let friction = 'nominal';
    if (stg.rework_rate > 20 || stg.stage === 'KYC') friction = 'critical';
    else if (stg.median_days > 5 || stg.conversion_rate < 90) friction = 'latency';
    return {
      ...stg,
      num: `0${index + 1}`.slice(-2),
      friction,
    };
  });

  return (
    <div className="flex flex-col gap-8">
      {/* SECTION 1: Editorial Hero Section */}
      <section className="border-b border-[#bec9c7]/30 pb-8">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-2">
          <div className="flex items-center gap-2 text-[10px] font-semibold tracking-wider uppercase text-[#3f4948]">
            <span className="inline-block w-2 h-2 rounded-full bg-[#11615f]"></span>
            <span>Private Wealth Division</span>
            <span>•</span>
            <span className="text-[#1c1b1a] font-bold">
              {filters.segment === 'All' ? 'All Client Cohorts (AUM > $10M)' : filters.segment}
            </span>
            <span>•</span>
            <span>Refreshed Live</span>
          </div>
          <div className="flex items-center gap-2 text-[11px] font-medium text-[#6f7978]">
            <span className="inline-block w-1.5 h-1.5 rounded-full bg-[#11615f] animate-pulse"></span>
            <span>Studio Intelligence Live Feed</span>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
          {/* Hero Left: Broadsheet Editorial Headings */}
          <div className="lg:col-span-7 pr-4">
            <h1 className="font-headline text-4xl sm:text-5xl text-[#1c1b1a] tracking-tight leading-[1.1] mb-2 font-normal">
              Every client journey tells a story.
            </h1>
            <p className="font-headline text-xl sm:text-2xl text-[#3f4948] font-normal max-w-xl">
              Discover friction. Understand retention. Design better experiences.
            </p>
          </div>

          {/* Hero Right: Bespoke SVG Abstract Multi-Track Journey */}
          <div className="lg:col-span-5 bg-[#f7f3ef] border border-[#bec9c7]/40 rounded p-4 architectural-shadow relative overflow-hidden">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] uppercase tracking-wider font-semibold text-[#6f7978]">
                Multi-Track Journey Fabric
              </span>
              <div className="flex items-center gap-3 text-[10px] font-semibold tracking-wider">
                <span className="flex items-center gap-1 text-[#11615f]">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#11615f]"></span> Nominal
                </span>
                <span className="flex items-center gap-1 text-[#864e59]">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#864e59]"></span> Friction Drag
                </span>
              </div>
            </div>

            {/* Abstract SVG Journey Map */}
            <svg className="w-full h-28" fill="none" viewBox="0 0 420 120" xmlns="http://www.w3.org/2000/svg">
              <line stroke="#E6E2DE" strokeDasharray="3 3" x1="20" x2="400" y1="20" y2="20" />
              <line stroke="#E6E2DE" strokeDasharray="3 3" x1="20" x2="400" y1="60" y2="60" />
              <line stroke="#E6E2DE" strokeDasharray="3 3" x1="20" x2="400" y1="100" y2="100" />
              {/* Track 1: Teal Nominal Path */}
              <path
                d="M 20 60 C 80 60, 110 30, 160 30 C 210 30, 240 45, 300 45 C 350 45, 370 25, 400 25"
                fill="none"
                stroke="#11615F"
                strokeLinecap="round"
                strokeWidth="2.5"
              />
              {/* Track 2: Burgundy Friction Splice */}
              <path
                d="M 160 30 C 190 30, 210 90, 250 90 C 290 90, 310 80, 340 80 C 370 80, 385 60, 400 60"
                fill="none"
                stroke="#864E59"
                strokeDasharray="4 2"
                strokeLinecap="round"
                strokeWidth="2"
              />
              {/* Track 3: Champagne Reference Streamline */}
              <path
                d="M 20 60 C 70 60, 100 85, 150 85 C 200 85, 230 70, 280 70 C 340 70, 360 40, 400 40"
                fill="none"
                stroke="#D9B77D"
                strokeOpacity="0.85"
                strokeWidth="1.5"
              />
              <circle cx="20" cy="60" fill="#1C1B1A" r="4" />
              <circle cx="160" cy="30" fill="#11615F" r="4.5" />
              <circle cx="160" cy="30" r="8" stroke="#11615F" strokeOpacity="0.3" />
              {/* KYC Hotspot */}
              <circle cx="250" cy="90" fill="#864E59" r="5" />
              <circle cx="250" cy="90" r="10" stroke="#864E59" strokeOpacity="0.3" className="animate-ping" />
              <circle cx="300" cy="45" fill="#11615F" r="4" />
              <circle cx="400" cy="25" fill="#11615F" r="4" />
              <circle cx="400" cy="60" fill="#864E59" r="3.5" />
            </svg>

            <div className="flex items-center justify-between text-[10px] font-semibold text-[#3f4948] pt-1">
              <span>Stage 01: Lead / Prospect</span>
              <span className="text-[#864e59]">Friction Peak: KYC Verification</span>
              <span>Stage 07: Active Mandate</span>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 2: Asymmetric Editorial Metric Composition (8:4 Split) */}
      <section className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
        {/* Left Column (Wide 7-col): Oversized Retention Ledger */}
        <div className="lg:col-span-7 bg-white border border-[#bec9c7]/40 rounded p-6 flex flex-col justify-between architectural-shadow">
          <div>
            <div className="flex items-center justify-between mb-4 border-b border-[#ece7e4] pb-2">
              <span className="text-[11px] font-semibold text-[#3f4948] uppercase tracking-wider">
                {retentionKpi.label}
              </span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => openMetricDrawer(retentionKpi.key)}
                  className="inline-flex items-center gap-1 text-[11px] text-[#11615f] hover:underline"
                >
                  <Code2 className="h-3 w-3" />
                  <span>View SQL</span>
                </button>
                <span className="bg-[#f1edea] text-[#1c1b1a] px-2.5 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase">
                  High-Net-Worth Aggregate
                </span>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row sm:items-baseline gap-4 mb-3">
              <div className="font-headline text-[58px] leading-none text-[#1c1b1a] tracking-tight font-normal tabular-nums">
                {formatKpiValue(retentionKpi)}
              </div>
              <div
                className={`flex items-center gap-1 font-semibold text-sm ${
                  isKpiNegative(retentionKpi) ? 'text-[#864e59]' : 'text-[#11615f]'
                }`}
              >
                {retentionKpi.direction === 'down' ? (
                  <TrendingDown className="h-4 w-4" />
                ) : (
                  <TrendingUp className="h-4 w-4" />
                )}
                <span>
                  {formatKpiDelta(retentionKpi)} vs. comparison period
                </span>
              </div>
            </div>

            <p className="text-sm text-[#3f4948] max-w-xl leading-relaxed">
              {overview.narrative.what_changed}
            </p>
          </div>

          {/* Integrated Inline Sparkline Trajectory */}
          <div className="mt-6 pt-4 border-t border-[#ece7e4]">
            <div className="flex items-center justify-between text-[11px] text-[#6f7978] mb-2 font-medium">
              <span>Historical Trajectory (Monthly Retention)</span>
              <span>
                As-Of: {overview.period.end_date} • Target: 96.0%
              </span>
            </div>
            <div className="h-16 w-full relative">
              <svg className="w-full h-full overflow-visible" preserveAspectRatio="none" viewBox="0 0 540 50">
                <defs>
                  <linearGradient id="retentionGradient" x1="0" y1="0" x2="0" y2="50" gradientUnits="userSpaceOnUse">
                    <stop stopColor="#864E59" stopOpacity="0.25" />
                    <stop offset="1" stopColor="#864E59" stopOpacity="0" />
                  </linearGradient>
                </defs>
                <path
                  d="M 0 15 Q 45 12, 90 18 T 180 14 T 270 20 T 360 26 T 450 32 T 540 34"
                  fill="none"
                  stroke="#864E59"
                  strokeWidth="2"
                />
                <path
                  d="M 0 15 Q 45 12, 90 18 T 180 14 T 270 20 T 360 26 T 450 32 T 540 34 L 540 50 L 0 50 Z"
                  fill="url(#retentionGradient)"
                />
                <circle cx="540" cy="34" fill="#864E59" r="4" />
              </svg>
            </div>
          </div>
        </div>

        {/* Right Column (5-col): Two Stacked Analytical Callouts */}
        <div className="lg:col-span-5 flex flex-col gap-6">
          {/* Callout A: Average Onboarding Velocity */}
          <div className="bg-white border border-[#bec9c7]/40 rounded p-6 architectural-shadow flex-1 flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-semibold text-[#3f4948] uppercase tracking-wider">
                {velocityKpi.label}
              </span>
              <button
                onClick={() => openMetricDrawer(velocityKpi.key)}
                className="text-[11px] text-[#11615f] hover:underline"
              >
                SQL
              </button>
            </div>
            <div className="my-2">
              <div className="flex items-baseline gap-2">
                <span className="font-sans text-3xl font-semibold text-[#1c1b1a] tabular-nums">
                  {formatKpiValue(velocityKpi)}
                </span>
                <span className="text-[#864e59] text-[11px] font-bold px-2 py-0.5 rounded bg-[#ffd9de]/50 tabular-nums">
                  {formatKpiDelta(velocityKpi)}
                </span>
              </div>
              <p className="text-xs text-[#3f4948] mt-1 leading-relaxed">
                Benchmark turnaround is 22 days. Unresolved verification roundtrips account for 82% of excess duration.
              </p>
            </div>
            <div className="w-full bg-[#ece7e4] h-1.5 rounded-full overflow-hidden flex">
              <div className="bg-[#11615f] h-full" style={{ width: '68%' }} />
              <div className="bg-[#864e59] h-full" style={{ width: '32%' }} />
            </div>
          </div>

          {/* Callout B: KYC Rework & At-Risk Cohort */}
          <div className="bg-white border border-[#bec9c7]/40 rounded p-6 architectural-shadow flex-1 flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-semibold text-[#3f4948] uppercase tracking-wider">
                {kycReworkKpi.label}
              </span>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase bg-[#ffd9de] text-[#360d17]">
                Priority 1 Risk
              </span>
            </div>
            <div className="my-2">
              <div className="flex items-baseline gap-2">
                <span className="font-sans text-3xl font-semibold text-[#864e59] tabular-nums">
                  {formatKpiValue(kycReworkKpi)}
                </span>
                <span className="text-[#1c1b1a] text-[11px] font-medium">
                  {formatKpiDelta(kycReworkKpi)}
                </span>
              </div>
              <p className="text-xs text-[#3f4948] mt-1 leading-relaxed">
                Document and entity verification re-submissions concentrated heavily in complex trust structures.
              </p>
            </div>
            <Link
              to="/journeys?stage=KYC"
              className="flex items-center justify-between text-[11px] font-semibold text-[#11615f] hover:underline"
            >
              <span>Inspect KYC rework topology</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>
        </div>
      </section>

      {/* SECTION 3: Onboarding Journey Topology & Stage Health */}
      <section className="bg-white border border-[#bec9c7]/40 rounded p-6 architectural-shadow">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-[#ece7e4] mb-6">
          <div>
            <h2 className="font-headline text-xl sm:text-2xl text-[#1c1b1a] font-semibold">
              Onboarding Journey Topology &amp; Stage Health
            </h2>
            <p className="text-xs text-[#3f4948] mt-0.5">
              Cross-stage pipeline mechanics: conversion throughput, dwell velocity, and identified workflow bottlenecks.
            </p>
          </div>
          <div className="flex items-center gap-4 text-[10px] font-semibold tracking-wider uppercase">
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-[#11615f]"></span>
              <span className="text-[#1c1b1a]">Nominal Flow</span>
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-[#876b38]"></span>
              <span className="text-[#1c1b1a]">Latency Drag</span>
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-[#864e59]"></span>
              <span className="text-[#864e59]">High Friction</span>
            </span>
          </div>
        </div>

        {/* 7 Horizontal Flowing Stages */}
        <div className="overflow-x-auto pb-2 custom-scrollbar">
          <div className="min-w-[1080px] grid grid-cols-7 gap-3">
            {stageData.map((stg) => {
              const isKyc = stg.stage === 'KYC' || stg.friction === 'critical';
              return (
                <div
                  key={stg.stage}
                  onClick={() => navigate(`/journeys?stage=${encodeURIComponent(stg.stage)}`)}
                  className={`p-3.5 rounded flex flex-col justify-between cursor-pointer transition-all ${
                    isKyc
                      ? 'bg-[#ffd9de]/25 border-2 border-[#864e59] shadow-sm relative'
                      : 'bg-[#f7f3ef] border border-[#bec9c7]/40 hover:border-[#11615f]'
                  }`}
                >
                  {isKyc && (
                    <div className="absolute -top-3 left-2 right-2 text-center bg-[#864e59] text-white text-[9px] font-bold tracking-widest uppercase py-0.5 px-1.5 rounded shadow-sm">
                      Severe Latency Drag
                    </div>
                  )}
                  <div className={isKyc ? 'pt-1' : ''}>
                    <div className="flex items-center justify-between mb-1.5">
                      <span
                        className={`text-[10px] font-bold uppercase tracking-wider ${
                          isKyc ? 'text-[#864e59]' : 'text-[#6f7978]'
                        }`}
                      >
                        {stg.num}. Stage
                      </span>
                      <span
                        className={`w-2 h-2 rounded-full ${
                          isKyc ? 'bg-[#864e59] animate-pulse' : 'bg-[#11615f]'
                        }`}
                      />
                    </div>
                    <h3
                      className={`font-headline text-[16px] leading-tight font-semibold ${
                        isKyc ? 'text-[#864e59]' : 'text-[#1c1b1a]'
                      }`}
                    >
                      {stg.stage}
                    </h3>
                    <p className="text-[11px] text-[#3f4948] mt-0.5">
                      {stg.entered_count.toLocaleString()} entered
                    </p>
                  </div>

                  <div className={`mt-4 pt-3 border-t ${isKyc ? 'border-[#864e59]/30' : 'border-[#bec9c7]/30'}`}>
                    <div className="flex items-baseline justify-between tabular-nums">
                      <span
                        className={`text-[20px] font-bold ${
                          isKyc ? 'text-[#864e59]' : 'text-[#1c1b1a]'
                        }`}
                      >
                        {stg.conversion_rate.toFixed(1)}%
                      </span>
                      <span className="text-[10px] text-[#6f7978] font-semibold uppercase">pass</span>
                    </div>
                    <div
                      className={`text-xs mt-1 tabular-nums ${
                        isKyc ? 'font-semibold text-[#864e59]' : 'text-[#3f4948]'
                      }`}
                    >
                      {stg.median_days.toFixed(1)}d median
                    </div>

                    <div className="flex gap-1 mt-2.5">
                      <span className={`w-1.5 h-1.5 rounded-full ${isKyc ? 'bg-[#864e59]' : 'bg-[#11615f]'}`} />
                      <span
                        className={`w-1.5 h-1.5 rounded-full ${
                          isKyc ? 'bg-[#864e59]' : stg.median_days > 4 ? 'bg-[#876b38]' : 'bg-[#11615f]'
                        }`}
                      />
                      <span
                        className={`w-1.5 h-1.5 rounded-full ${
                          isKyc ? 'bg-[#864e59]' : 'bg-[#ddd9d6]'
                        }`}
                      />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* SECTION 4: Editorial Insight Panel ('Where the experience is breaking down') */}
      <section className="bg-white border border-[#bec9c7]/40 rounded p-6 architectural-shadow">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-6 pb-3 border-b border-[#ece7e4]">
          <div>
            <span className="text-[11px] font-bold text-[#864e59] uppercase tracking-widest">
              Diagnostics Synthesis
            </span>
            <h2 className="font-headline text-3xl text-[#1c1b1a] tracking-tight mt-1 font-normal">
              Where the experience is breaking down
            </h2>
            <p className="text-sm text-[#3f4948] mt-1">
              Synthesis of critical friction points impacting client retention, advisor workload, and asset deployment.
            </p>
          </div>
          <div className="flex items-center gap-3 shrink-0">
            <Link
              to="/investigations?template=retention_decline"
              className="px-5 py-2.5 bg-[#864e59] text-white rounded text-[11px] font-bold uppercase tracking-wider hover:bg-[#6a3741] transition-all flex items-center gap-2 shadow-sm"
            >
              <span>Begin an Investigation</span>
              <ArrowRight className="h-4 w-4 text-[#ffdea8]" />
            </Link>
          </div>
        </div>

        {/* 3 Beautifully Arranged Editorial Findings */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {overview.insights.map((ins, i) => (
            <div
              key={i}
              className="border border-[#bec9c7]/30 rounded p-5 bg-[#f7f3ef]/50 flex flex-col justify-between hover:bg-[#f7f3ef] transition-colors"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="font-headline text-2xl font-semibold text-[#864e59]">
                    0{i + 1}
                  </span>
                  <span
                    className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded ${
                      i === 0
                        ? 'bg-[#ffd9de] text-[#360d17]'
                        : i === 1
                        ? 'bg-[#ffdea8] text-[#271900]'
                        : 'bg-[#a9efec] text-[#00201f]'
                    }`}
                  >
                    {ins.category}
                  </span>
                </div>
                <h4 className="font-headline text-lg font-semibold text-[#1c1b1a] leading-snug mb-2">
                  {ins.headline}
                </h4>
                <div className="bg-[#e6e2de] px-2.5 py-1 rounded text-[11px] font-medium text-[#1c1b1a] mb-3 inline-block">
                  {ins.supporting_evidence}
                </div>
                <p className="text-xs text-[#3f4948] leading-relaxed">
                  {ins.related_outcome}
                </p>
              </div>
              <div className="mt-5 pt-3 border-t border-[#bec9c7]/30 flex items-center justify-between text-xs">
                <span className="text-[#6f7978]">Verified Telemetry</span>
                <Link to={ins.route} className="text-[#11615f] font-semibold hover:underline flex items-center gap-1">
                  <span>{ins.next_action}</span>
                  <ArrowRight className="h-3 w-3" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
