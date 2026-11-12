import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import {
  AlertTriangle,
  ArrowRight,
  Code2,
  GitCommit,
  Filter,
  History,
  Layers,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  CheckCircle2,
} from 'lucide-react';
import { useFilters } from '@/hooks/useFilters';
import { apiGet, buildFilterParams } from '@/services/api';

export function JourneyAnalyticsPage() {
  const { filters, setFilters, openMetricDrawer } = useFilters();
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const initialStage = searchParams.get('stage') || 'KYC';
  const [selectedStage, setSelectedStage] = useState(initialStage);
  const [viewMode, setViewMode] = useState<'flow' | 'latency' | 'rework'>('flow');

  useEffect(() => {
    const stg = searchParams.get('stage');
    if (stg) setSelectedStage(stg);
  }, [searchParams]);

  const qs = buildFilterParams(filters);

  const { data: funnel, isLoading } = useQuery<any>({
    queryKey: ['journey-funnel', qs],
    queryFn: () => apiGet(`/journey/funnel?${qs}`),
  });

  const { data: stageDetail } = useQuery<any>({
    queryKey: ['journey-stage', selectedStage, qs],
    queryFn: () => apiGet(`/journey/stages/${encodeURIComponent(selectedStage)}?${qs}`),
    enabled: Boolean(selectedStage),
  });

  const handleSelectStage = (stage: string) => {
    setSelectedStage(stage);
    setSearchParams({ stage });
  };

  const stagesList = funnel?.stages || [];

  return (
    <div className="flex flex-col gap-6">
      {/* SUB-HEADER CONTEXT BAR */}
      <section className="border-b border-[#bec9c7]/30 pb-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          {/* Title & Scope */}
          <div>
            <div className="flex items-center gap-3">
              <h1 className="font-headline text-3xl font-semibold text-[#1c1b1a]">Journey Explorer</h1>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase bg-[#e6e2de] text-[#11615f] border border-[#bec9c7]/40">
                ACTIVE COHORT MAP
              </span>
            </div>
            <p className="text-xs text-[#3f4948] mt-1">
              Interactive lifecycle topology across {funnel?.total_clients_in_funnel || '480+'} client journeys
            </p>
          </div>

          {/* Cohort Segment Pill Selectors */}
          <div className="flex flex-wrap items-center gap-1.5 bg-white p-1 rounded border border-[#bec9c7]/40 shadow-sm">
            {['All', 'Ultra HNW', 'Family Office', 'Private Wealth'].map((seg) => (
              <button
                key={seg}
                onClick={() => setFilters((f) => ({ ...f, segment: seg }))}
                className={`px-3 py-1 rounded text-[10px] font-bold tracking-wider uppercase transition-colors ${
                  (seg === 'All' && filters.segment === 'All') || filters.segment === seg
                    ? 'bg-[#11615f] text-white'
                    : 'text-[#3f4948] hover:text-[#1c1b1a] hover:bg-[#f7f3ef]'
                }`}
              >
                {seg === 'All' ? 'All Cohorts' : seg}
              </button>
            ))}
          </div>

          {/* View Modes & Action Tools */}
          <div className="flex items-center gap-2.5">
            <div className="flex items-center bg-white border border-[#bec9c7]/40 rounded p-0.5">
              <button
                onClick={() => setViewMode('flow')}
                className={`px-2.5 py-1 text-[11px] font-semibold rounded ${
                  viewMode === 'flow' ? 'bg-[#f1edea] text-[#1c1b1a] shadow-sm' : 'text-[#3f4948]'
                }`}
              >
                Flow View
              </button>
              <button
                onClick={() => setViewMode('latency')}
                className={`px-2.5 py-1 text-[11px] font-semibold rounded ${
                  viewMode === 'latency' ? 'bg-[#f1edea] text-[#1c1b1a] shadow-sm' : 'text-[#3f4948]'
                }`}
              >
                Latency
              </button>
              <button
                onClick={() => setViewMode('rework')}
                className={`px-2.5 py-1 text-[11px] font-semibold rounded ${
                  viewMode === 'rework' ? 'bg-[#f1edea] text-[#1c1b1a] shadow-sm' : 'text-[#3f4948]'
                }`}
              >
                Rework
              </button>
            </div>

            <button
              onClick={() => openMetricDrawer('kyc_rework_rate')}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-[#864e59] text-[#864e59] rounded text-[11px] font-bold uppercase tracking-wider hover:bg-[#ffd9de]/30 transition-colors"
            >
              <Code2 className="h-3.5 w-3.5" />
              <span>Calculation Logic</span>
            </button>
          </div>
        </div>
      </section>

      {/* MASTER WORKSPACE: 8:4 Asymmetric Split (Spatial Topology Canvas vs Active Stage Inspector) */}
      <div className="grid grid-cols-12 gap-6 items-start">
        {/* LEFT: SPATIAL JOURNEY TOPOLOGY CANVAS (Col 8) */}
        <section className="col-span-12 lg:col-span-8 bg-white border border-[#bec9c7]/40 rounded relative shadow-sm overflow-hidden flex flex-col">
          {/* Canvas Status Bar */}
          <div className="px-5 py-3 border-b border-[#bec9c7]/30 flex items-center justify-between bg-[#fdf9f5]">
            <div className="flex items-center gap-3">
              <span className="w-2.5 h-2.5 rounded-full bg-[#11615f] animate-pulse"></span>
              <span className="text-[11px] font-bold uppercase tracking-wider text-[#1c1b1a]">
                Multi-Track Lifecycle Topology
              </span>
              <span className="text-xs text-[#3f4948]">
                — 7 Milestone Stages, 2 Diversion Rework Loops
              </span>
            </div>
            <div className="flex items-center gap-4 text-[10px] font-semibold uppercase tracking-wider text-[#3f4948]">
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-[#11615f]"></span> Nominal
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-[#876b38]"></span> Delay
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-[#864e59]"></span> Critical Rework
              </span>
            </div>
          </div>

          {/* Interactive Spatial Map Canvas */}
          <div className="w-full overflow-x-auto custom-scrollbar topology-grid p-6 min-h-[580px] relative select-none">
            {/* SVG Directed Path Connections */}
            <svg
              className="absolute inset-0 w-[1140px] h-[580px] pointer-events-none z-0"
              xmlns="http://www.w3.org/2000/svg"
            >
              <defs>
                <marker id="arrowTeal" markerHeight="6" markerWidth="6" orient="auto" refX="5" refY="3">
                  <path d="M0,0 L6,3 L0,6 Z" fill="#11615f" />
                </marker>
                <marker id="arrowBurgundy" markerHeight="6" markerWidth="6" orient="auto" refX="5" refY="3">
                  <path d="M0,0 L6,3 L0,6 Z" fill="#864e59" />
                </marker>
              </defs>
              {/* 1 -> 2 Main Track */}
              <path d="M 135 125 L 205 125" fill="none" markerEnd="url(#arrowTeal)" stroke="#11615f" strokeWidth="2.5" />
              {/* 2 Direct Pass -> 3 Main Track */}
              <path d="M 345 125 L 405 125" fill="none" markerEnd="url(#arrowTeal)" stroke="#11615f" strokeWidth="2.5" />
              {/* 2 Diversion Loop -> Downward curved path into Rework Loop */}
              <path
                d="M 275 185 C 275 250, 240 280, 290 280 L 370 280"
                fill="none"
                stroke="#864e59"
                strokeDasharray="4,4"
                strokeWidth="2"
              />
              {/* Rework Loop back to Stage 2 */}
              <path
                d="M 470 310 C 510 330, 210 360, 220 200"
                fill="none"
                markerEnd="url(#arrowBurgundy)"
                stroke="#864e59"
                strokeWidth="2"
              />
              {/* 3 -> 4 Main Track */}
              <path d="M 525 125 L 585 125" fill="none" markerEnd="url(#arrowTeal)" stroke="#11615f" strokeWidth="2.5" />
              {/* 4 Branching paths: Wire Transfer vs In-Kind Securities */}
              <path d="M 705 110 C 730 85, 740 75, 775 75 L 810 75" fill="none" stroke="#11615f" strokeWidth="2" />
              <path
                d="M 705 140 C 730 165, 740 175, 775 175 L 810 175"
                fill="none"
                stroke="#876b38"
                strokeDasharray="3,3"
                strokeWidth="2"
              />
              {/* Re-convergence to Stage 5 */}
              <path d="M 875 75 C 910 75, 905 125, 935 125" fill="none" stroke="#11615f" strokeWidth="2" />
              <path
                d="M 875 175 C 910 175, 905 125, 935 125"
                fill="none"
                markerEnd="url(#arrowTeal)"
                stroke="#876b38"
                strokeWidth="2"
              />
              {/* 5 -> 6 Main Track */}
              <path d="M 1045 125 L 1075 125" fill="none" markerEnd="url(#arrowTeal)" stroke="#11615f" strokeWidth="2.5" />
            </svg>

            {/* Nodes & Stage Blocks Container */}
            <div className="relative w-[1140px] h-[520px]">
              {/* STAGE 01: Prospect Qualification */}
              <div
                onClick={() => handleSelectStage('Prospect')}
                className={`absolute left-0 top-12 w-[135px] bg-white border rounded p-3 shadow-sm cursor-pointer transition-all ${
                  selectedStage === 'Prospect' ? 'border-[#11615f] ring-2 ring-[#11615f]/20' : 'border-[#bec9c7]/50 hover:border-[#11615f]'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] font-bold text-[#6f7978] uppercase">Stage 01</span>
                  <span className="w-1.5 h-1.5 rounded-full bg-[#11615f]"></span>
                </div>
                <h3 className="font-headline text-[15px] leading-tight text-[#1c1b1a] font-medium">Prospect</h3>
                <div className="mt-3 pt-2 border-t border-[#bec9c7]/30 tabular-nums">
                  <div className="text-[16px] font-bold text-[#1c1b1a]">
                    {stagesList[0]?.entered_count || 480}{' '}
                    <span className="text-[11px] font-normal text-[#6f7978]">Entered</span>
                  </div>
                  <div className="text-[11px] font-semibold text-[#11615f]">100% Entry Rate</div>
                </div>
                <div className="mt-2 text-[10px] text-[#6f7978] tabular-nums">
                  Avg {stagesList[0]?.median_days?.toFixed(1) || 1.8}d
                </div>
              </div>

              {/* STAGE 02: Verification & Due Diligence (ACTIVE / KYC) */}
              <div
                onClick={() => handleSelectStage('KYC')}
                className={`absolute left-[205px] top-6 w-[140px] bg-white rounded p-3 shadow-md transition-all cursor-pointer ${
                  selectedStage === 'KYC'
                    ? 'border-2 border-[#864e59] ring-4 ring-[#864e59]/10'
                    : 'border border-[#864e59]/60 hover:border-[#864e59]'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] font-bold text-[#864e59] uppercase tracking-wider">
                    Stage 02 • KYC
                  </span>
                  <span className="w-2 h-2 rounded-full bg-[#864e59] animate-ping"></span>
                </div>
                <h3 className="font-headline text-[15px] leading-tight text-[#1c1b1a] font-bold">
                  Identity &amp; KYC
                </h3>
                <div className="mt-2 pt-2 border-t border-[#864e59]/20 tabular-nums">
                  <div className="flex justify-between items-baseline">
                    <span className="text-[17px] text-[#1c1b1a] font-bold">
                      {stagesList[1]?.entered_count || 480}
                    </span>
                    <span className="text-[11px] font-bold text-[#864e59]">
                      {stagesList[1]?.rework_rate ? `${stagesList[1].rework_rate.toFixed(1)}% Rework` : '37.2% Divert'}
                    </span>
                  </div>
                  <div className="text-[10px] text-[#6f7978]">
                    Median: {stagesList[1]?.median_days?.toFixed(1) || 11.4}d
                  </div>
                </div>
                {/* Inline Friction Highlight Pill */}
                <div className="mt-2 py-0.5 px-1.5 bg-[#ffd9de]/50 text-[#360d17] text-[10px] font-bold rounded flex items-center gap-1">
                  <AlertTriangle className="h-3 w-3 text-[#864e59]" />
                  <span>Critical Friction</span>
                </div>
              </div>

              {/* VISIBLE REWORK BRANCH LOOP */}
              <div className="absolute left-[250px] top-[240px] w-[220px] bg-[#ffd9de]/20 border border-[#864e59]/40 rounded p-3 shadow-sm">
                <div className="flex items-center gap-1.5 text-[#864e59]">
                  <RotateCcw className="h-3.5 w-3.5" />
                  <span className="text-[10px] font-bold uppercase tracking-wider">
                    Visible Rework Loopback
                  </span>
                </div>
                <div className="mt-1 text-xs text-[#1c1b1a] font-medium leading-snug">
                  Beneficial Ownership &amp; Verification Resubmissions
                </div>
                <div className="mt-2 flex items-center justify-between pt-1 border-t border-[#864e59]/20 text-[11px] tabular-nums">
                  <span className="text-[#864e59] font-bold">
                    {stagesList[1]?.rework_rate ? `${Math.round(stagesList[1].rework_rate)}% of Volume` : '179 Accounts'}
                  </span>
                  <span className="text-[#6f7978]">Avg 14.2d Loopback</span>
                </div>
              </div>

              {/* STAGE 03: Account Opening */}
              <div
                onClick={() => handleSelectStage('Account Opening')}
                className={`absolute left-[405px] top-12 w-[120px] bg-white border rounded p-3 shadow-sm cursor-pointer transition-all ${
                  selectedStage === 'Account Opening'
                    ? 'border-[#11615f] ring-2 ring-[#11615f]/20'
                    : 'border-[#bec9c7]/50 hover:border-[#11615f]'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] font-bold text-[#6f7978] uppercase">Stage 03</span>
                  <span className="w-1.5 h-1.5 rounded-full bg-[#11615f]"></span>
                </div>
                <h3 className="font-headline text-[15px] leading-tight text-[#1c1b1a]">Account Opening</h3>
                <div className="mt-3 pt-2 border-t border-[#bec9c7]/30 tabular-nums">
                  <div className="text-[16px] font-bold text-[#1c1b1a]">
                    {stagesList[2]?.entered_count || 462}
                  </div>
                  <div className="text-[11px] font-semibold text-[#11615f]">
                    {stagesList[2]?.conversion_rate?.toFixed(1) || '96.2'}% Yield
                  </div>
                </div>
                <div className="mt-2 text-[10px] text-[#6f7978] tabular-nums">
                  Avg {stagesList[2]?.median_days?.toFixed(1) || 3.2}d
                </div>
              </div>

              {/* STAGE 04: Funding */}
              <div
                onClick={() => handleSelectStage('Funding')}
                className={`absolute left-[585px] top-12 w-[120px] bg-white border rounded p-3 shadow-sm cursor-pointer transition-all ${
                  selectedStage === 'Funding'
                    ? 'border-[#11615f] ring-2 ring-[#11615f]/20'
                    : 'border-[#bec9c7]/50 hover:border-[#11615f]'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] font-bold text-[#6f7978] uppercase">Stage 04</span>
                  <span className="w-1.5 h-1.5 rounded-full bg-[#11615f]"></span>
                </div>
                <h3 className="font-headline text-[15px] leading-tight text-[#1c1b1a]">Funding</h3>
                <div className="mt-3 pt-2 border-t border-[#bec9c7]/30 tabular-nums">
                  <div className="text-[16px] font-bold text-[#1c1b1a]">
                    {stagesList[3]?.entered_count || 448}
                  </div>
                  <div className="text-[11px] font-semibold text-[#11615f]">
                    {stagesList[3]?.conversion_rate?.toFixed(1) || '97.0'}% Converted
                  </div>
                </div>
                <div className="mt-2 text-[10px] text-[#6f7978]">Split Transfer Protocols</div>
              </div>

              {/* Branch Split Upper: Wire Transfer */}
              <div className="absolute left-[745px] top-7 w-[130px] bg-[#f7f3ef] border border-[#bec9c7]/50 rounded p-2 text-left">
                <div className="flex items-center justify-between text-[10px] font-bold">
                  <span className="text-[#11615f] uppercase">Wire Transfer</span>
                  <span className="text-[#11615f]">2.1d</span>
                </div>
                <div className="text-xs font-semibold text-[#1c1b1a] mt-0.5">310 Accounts</div>
              </div>

              {/* Branch Split Lower: In-Kind ACATS */}
              <div className="absolute left-[745px] top-[145px] w-[130px] bg-[#f7f3ef] border border-[#876b38]/40 rounded p-2 text-left">
                <div className="flex items-center justify-between text-[10px] font-bold">
                  <span className="text-[#876b38] uppercase">In-Kind Transfer</span>
                  <span className="text-[#876b38]">8.4d</span>
                </div>
                <div className="text-xs font-semibold text-[#1c1b1a] mt-0.5">138 Accounts</div>
              </div>

              {/* STAGE 05: Advisor Meeting */}
              <div
                onClick={() => handleSelectStage('Advisor Meeting')}
                className={`absolute left-[935px] top-12 w-[110px] bg-white border rounded p-2.5 shadow-sm cursor-pointer transition-all ${
                  selectedStage === 'Advisor Meeting'
                    ? 'border-[#11615f] ring-2 ring-[#11615f]/20'
                    : 'border-[#bec9c7]/50 hover:border-[#11615f]'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] font-bold text-[#6f7978] uppercase">Stage 05</span>
                  <span className="w-1.5 h-1.5 rounded-full bg-[#11615f]"></span>
                </div>
                <h3 className="font-headline text-[14px] leading-tight text-[#1c1b1a]">Advisor Sync</h3>
                <div className="mt-2 pt-1 border-t border-[#bec9c7]/30 tabular-nums">
                  <div className="text-[15px] font-bold text-[#1c1b1a]">
                    {stagesList[4]?.entered_count || 432}
                  </div>
                  <div className="text-[10px] text-[#6f7978]">Strategy Review</div>
                </div>
              </div>

              {/* STAGE 06: Portfolio Setup */}
              <div
                onClick={() => handleSelectStage('Portfolio Setup')}
                className={`absolute left-[1075px] top-12 w-[110px] bg-white border rounded p-2.5 shadow-sm cursor-pointer transition-all ${
                  selectedStage === 'Portfolio Setup'
                    ? 'border-[#11615f] ring-2 ring-[#11615f]/20'
                    : 'border-[#bec9c7]/50 hover:border-[#11615f]'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] font-bold text-[#6f7978] uppercase">Stage 06</span>
                  <span className="w-1.5 h-1.5 rounded-full bg-[#11615f]"></span>
                </div>
                <h3 className="font-headline text-[14px] leading-tight text-[#1c1b1a]">Portfolio</h3>
                <div className="mt-2 pt-1 border-t border-[#bec9c7]/30 tabular-nums">
                  <div className="text-[15px] font-bold text-[#1c1b1a]">
                    {stagesList[5]?.entered_count || 418}
                  </div>
                  <div className="text-[10px] text-[#6f7978]">Discretionary</div>
                </div>
              </div>

              {/* Retention Target Pill (End Milestone) */}
              <div className="absolute left-[950px] top-[260px] bg-[#f7f3ef] border border-[#11615f]/40 rounded p-3 flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-[#11615f]/10 flex items-center justify-center text-[#11615f]">
                  <CheckCircle2 className="h-5 w-5" />
                </div>
                <div>
                  <div className="text-[10px] font-bold uppercase tracking-wider text-[#6f7978]">
                    Ongoing Retention Output
                  </div>
                  <div className="text-xs font-bold text-[#1c1b1a]">
                    {funnel?.total_clients_in_funnel || '410'} Accounts Retained
                  </div>
                  <div className="text-[10px] text-[#11615f] font-semibold">Active Relationship Lifecycle</div>
                </div>
              </div>
            </div>
          </div>

          {/* Canvas Footer Metrics Strip */}
          <div className="px-5 py-3 border-t border-[#bec9c7]/30 bg-[#f7f3ef] flex flex-wrap items-center justify-between gap-4 text-xs">
            <div className="flex flex-wrap items-center gap-6 tabular-nums">
              <span className="text-[#3f4948]">
                Funnel Throughput:{' '}
                <strong className="text-[#1c1b1a]">
                  {stagesList[stagesList.length - 1]?.conversion_rate?.toFixed(1) || '85.4'}% Overall
                </strong>
              </span>
              <span className="text-[#3f4948]">
                Median Duration:{' '}
                <strong className="text-[#1c1b1a]">
                  {stagesList.reduce((acc: number, s: any) => acc + (s.median_days || 0), 0).toFixed(1)} Days
                </strong>
              </span>
              <span className="text-[#3f4948]">
                KYC Rework Drag:{' '}
                <strong className="text-[#864e59]">
                  {stagesList[1]?.rework_rate ? `+${stagesList[1].rework_rate.toFixed(1)}% Surge` : '+14.2% Variance'}
                </strong>
              </span>
            </div>
            <Link
              to="/clients"
              className="text-[11px] font-bold uppercase tracking-wider text-[#11615f] hover:underline"
            >
              Explore Client Cohorts →
            </Link>
          </div>
        </section>

        {/* RIGHT: ACTIVE STAGE INSPECTOR (Dossier Drawer, Col 4) */}
        <aside className="col-span-12 lg:col-span-4 bg-white border border-[#bec9c7]/50 rounded shadow-sm flex flex-col divide-y divide-[#bec9c7]/30">
          {/* Drawer Header */}
          <div className="p-5 bg-[#f7f3ef]/60 rounded-t">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#ffd9de] text-[#360d17] tracking-wider uppercase">
                  Selected Stage
                </span>
                {selectedStage === 'KYC' && (
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#ffdad6] text-[#ba1a1a] uppercase">
                    Critical Friction
                  </span>
                )}
              </div>
            </div>
            <h2 className="font-headline text-2xl text-[#1c1b1a] leading-tight font-semibold">
              {selectedStage}
            </h2>
            <p className="text-xs text-[#3f4948] mt-1">
              Detailed turnaround duration, rework driver attribution, and case-level drilldowns.
            </p>
          </div>

          {/* Core Numerical Metrics Panel */}
          <div className="p-5 grid grid-cols-3 gap-3 bg-white tabular-nums">
            <div className="flex flex-col">
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#6f7978]">
                Stage Median
              </span>
              <span className="text-xl font-bold text-[#864e59] mt-1">
                {stageDetail?.summary?.median_days?.toFixed(1) || '11.4'}d
              </span>
              <span className="text-[10px] text-[#6f7978] leading-none mt-0.5">
                p90: {stageDetail?.summary?.p90_days?.toFixed(1) || '24.2'}d
              </span>
            </div>
            <div className="flex flex-col border-l border-[#bec9c7]/30 pl-3">
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#6f7978]">
                Yield
              </span>
              <span className="text-xl font-bold text-[#1c1b1a] mt-1">
                {stageDetail?.summary?.conversion_rate?.toFixed(1) || '62.8'}%
              </span>
              <span className="text-[10px] text-[#6f7978] leading-none mt-0.5">Completion</span>
            </div>
            <div className="flex flex-col border-l border-[#bec9c7]/30 pl-3">
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#6f7978]">
                Rework
              </span>
              <span className="text-xl font-bold text-[#864e59] mt-1">
                {stageDetail?.summary?.rework_rate?.toFixed(1) || '37.2'}%
              </span>
              <span className="text-[10px] text-[#864e59] leading-none mt-0.5">Secondary loop</span>
            </div>
          </div>

          {/* Root Friction Attribution Breakdown */}
          {stageDetail?.rework_reasons?.length > 0 && (
            <div className="p-5 flex flex-col gap-3">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold uppercase tracking-wider text-[#1c1b1a]">
                  Root Friction Attribution
                </span>
                <span className="text-[10px] text-[#6f7978]">Case Share</span>
              </div>
              <div className="space-y-3">
                {stageDetail.rework_reasons.slice(0, 3).map((item: any, idx: number) => {
                  const pct = Math.min(100, Math.round((item.count / 40) * 100));
                  return (
                    <div key={idx} className="flex flex-col gap-1">
                      <div className="flex justify-between text-xs">
                        <span className="text-[#1c1b1a] font-medium truncate max-w-[200px]">
                          {item.reason}
                        </span>
                        <span className="font-bold text-[#864e59] tabular-nums">{item.count} cases</span>
                      </div>
                      <div className="w-full h-1.5 bg-[#f1edea] rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${idx === 0 ? 'bg-[#864e59]' : 'bg-[#6f7978]'}`}
                          style={{ width: `${Math.max(15, pct)}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Affected Client Cohorts Breakdown */}
          <div className="p-5 bg-[#f7f3ef]/30">
            <span className="text-[10px] font-bold uppercase tracking-wider text-[#1c1b1a] mb-2.5 block">
              Recent Case Telemetry
            </span>
            <div className="space-y-2">
              {(stageDetail?.sample_episodes || []).slice(0, 3).map((ep: any) => (
                <div
                  key={ep.episode_id}
                  onClick={() => navigate(`/clients/${ep.client_id}`)}
                  className="flex items-center justify-between p-2 rounded bg-white border border-[#bec9c7]/30 text-xs cursor-pointer hover:border-[#11615f] transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <span
                      className={`w-1.5 h-1.5 rounded-full ${
                        ep.outcome === 'Reopened' ? 'bg-[#864e59]' : 'bg-[#11615f]'
                      }`}
                    />
                    <span className="font-mono text-[11px] font-bold text-[#1c1b1a]">{ep.client_id}</span>
                    <span className="text-[#6f7978]">{ep.segment}</span>
                  </div>
                  <span
                    className={`font-semibold text-[10px] ${
                      ep.outcome === 'Reopened' ? 'text-[#864e59]' : 'text-[#11615f]'
                    }`}
                  >
                    {ep.outcome}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Inspector Action Center */}
          <div className="p-5 flex flex-col gap-2.5 bg-white rounded-b">
            <Link
              to="/investigations?template=kyc_rework_investigation"
              className="w-full py-2.5 px-4 bg-[#864e59] text-white rounded text-[11px] font-bold uppercase tracking-wider hover:bg-[#6a3741] transition-colors flex items-center justify-center gap-2 shadow-sm"
            >
              <span>Isolate in Investigation Studio</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
            <Link
              to="/clients"
              className="w-full py-2 px-4 bg-white border border-[#bec9c7]/60 text-[#1c1b1a] rounded text-[11px] font-bold uppercase tracking-wider hover:bg-[#f7f3ef] transition-colors flex items-center justify-center gap-2"
            >
              <span>View Client Directory</span>
            </Link>
          </div>
        </aside>
      </div>

      {/* BELOW-MAP TIMELINE & PROCESS EVOLUTION SECTION */}
      <section className="w-full bg-white border border-[#bec9c7]/40 rounded p-6 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-[#bec9c7]/30 gap-2">
          <div>
            <div className="flex items-center gap-2">
              <History className="h-5 w-5 text-[#11615f]" />
              <h3 className="font-headline text-xl text-[#1c1b1a] font-semibold">
                Process Interventions &amp; Policy Changes
              </h3>
            </div>
            <p className="text-xs text-[#3f4948] mt-0.5">
              Operational causality markers mapped directly against journey variance telemetry.
            </p>
          </div>
          <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-[#a9efec]/30 border border-[#11615f]/30 rounded text-[#11615f] text-xs font-semibold">
            <span>Pre-submission validation checker proposed to reduce KYC rework by <strong>18.5 pp</strong>.</span>
          </div>
        </div>

        {/* Process Interventions Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
          {(funnel?.process_changes || [
            {
              change_id: 1,
              effective_date: '2024-08-12',
              change_code: 'REG-2024-08',
              title: 'FinCEN CDD Rule Checklist Implemented',
              description:
                'Updated mandatory compliance questionnaire introduced directly into portal. Induced initial +2.8 day friction surge on foreign trusts.',
              impact_area: 'Stage 02 (KYC)',
              impact_metric: '+18.5% Rework',
            },
            {
              change_id: 2,
              effective_date: '2024-09-01',
              change_code: 'OPS-2024-09',
              title: 'Dedicated Onboarding Concierge for >$25M',
              description:
                'Introduced high-touch bilateral team to directly handle cross-border notary apostilles and custodian alignment meetings.',
              impact_area: 'Stage 04 & 05',
              impact_metric: '-4.1 Days Latency',
            },
            {
              change_id: 3,
              effective_date: '2024-10-15',
              change_code: 'SYS-2024-10',
              title: 'Third-Party KYC API Timeout Reduced to 30s',
              description:
                'Re-architected asynchronous verification webhook handlers to prevent interface freezing during European registry queries.',
              impact_area: 'Portal Auth',
              impact_metric: '-82% Timeouts',
            },
          ]).map((pc: any, i: number) => (
            <div
              key={pc.change_id || i}
              className="flex flex-col bg-[#f7f3ef]/50 border border-[#bec9c7]/30 rounded p-4 hover:border-[#11615f]/50 transition-colors"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-[11px] font-bold text-[#864e59] uppercase tracking-wider">
                  {pc.effective_date}
                </span>
                <span className="px-1.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider bg-[#e6e2de] text-[#3f4948]">
                  {pc.change_code || 'Policy Change'}
                </span>
              </div>
              <h4 className="font-headline text-[16px] leading-snug text-[#1c1b1a] font-semibold">
                {pc.title}
              </h4>
              <p className="text-xs text-[#3f4948] mt-2 leading-relaxed">
                {pc.description}
              </p>
              <div className="mt-4 pt-2 border-t border-[#bec9c7]/20 flex items-center justify-between text-[11px]">
                <span className="text-[#6f7978]">Impact: {pc.impact_area || 'Stage 02'}</span>
                <span className="text-[#11615f] font-bold">{pc.impact_metric || '-4.1d Latency'}</span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
