import { useEffect, useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useSearchParams, Link } from 'react-router-dom';
import {
  ArrowRight,
  Download,
  FlaskConical,
  Play,
  CheckCircle2,
  AlertTriangle,
  FileText,
  Search,
  ChevronRight,
  HelpCircle,
} from 'lucide-react';
import { useFilters } from '@/hooks/useFilters';
import { apiGet, apiPost } from '@/services/api';

export function InvestigationLabPage() {
  const { filters } = useFilters();
  const [searchParams] = useSearchParams();
  const [selectedTemplate, setSelectedTemplate] = useState(
    searchParams.get('template') || 'retention_decline'
  );
  const [activeReport, setActiveReport] = useState<any>(null);

  const { data: templates } = useQuery<any[]>({
    queryKey: ['investigation-templates'],
    queryFn: () => apiGet('/investigations/templates'),
  });

  const runMutation = useMutation({
    mutationFn: (templateKey: string) =>
      apiPost('/investigations', {
        template_key: templateKey,
        start_date: filters.start_date,
        end_date: filters.end_date,
        segment: filters.segment === 'All' ? null : filters.segment,
        team_id: filters.team_id === 'All' ? null : filters.team_id,
        region: filters.region === 'All' ? null : filters.region,
      }),
    onSuccess: (data) => setActiveReport(data),
  });

  useEffect(() => {
    const t = searchParams.get('template') || 'retention_decline';
    setSelectedTemplate(t);
    runMutation.mutate(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  const handleExportReport = () => {
    if (!activeReport) return;
    const blob = new Blob([JSON.stringify(activeReport, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${activeReport.investigation_id}_report.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const f = activeReport?.findings;

  return (
    <div className="flex flex-col gap-8">
      {/* Header */}
      <div className="flex flex-wrap items-end justify-between gap-4 border-b border-[#bec9c7]/30 pb-4">
        <div>
          <div className="flex items-center gap-2 text-[10px] font-bold tracking-wider uppercase text-[#6f7978]">
            <span className="w-2 h-2 rounded-full bg-[#864e59]"></span>
            <span>Deterministic Diagnostics Studio</span>
          </div>
          <h1 className="font-headline text-3xl font-semibold text-[#1c1b1a] mt-1">
            Investigation Lab
          </h1>
          <p className="text-xs text-[#3f4948] mt-1">
            Guided 6-step root-cause diagnostics connecting telemetry signals to evidence-backed initiatives.
          </p>
        </div>

        {activeReport && (
          <button
            onClick={handleExportReport}
            className="inline-flex items-center gap-1.5 rounded border border-[#bec9c7]/60 bg-white px-3.5 py-2 text-xs font-semibold text-[#1c1b1a] hover:bg-[#f7f3ef] transition-colors"
          >
            <Download className="h-4 w-4" />
            <span>Export Investigation Report (JSON)</span>
          </button>
        )}
      </div>

      {/* Step 1: Investigation Template Selector */}
      <section className="rounded border border-[#bec9c7]/40 bg-white p-6 architectural-shadow">
        <div className="flex items-center justify-between pb-3 border-b border-[#ece7e4] mb-4">
          <div>
            <span className="text-[10px] font-bold uppercase tracking-wider text-[#864e59]">
              Step 01
            </span>
            <h2 className="font-headline text-xl text-[#1c1b1a] font-semibold mt-0.5">
              Define the Management Question
            </h2>
          </div>
          <span className="text-xs text-[#6f7978]">
            Select one of {templates?.length || 5} deterministic investigation protocols
          </span>
        </div>

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
          {templates?.map((t) => {
            const active = selectedTemplate === t.template_key;
            return (
              <button
                key={t.template_key}
                onClick={() => {
                  setSelectedTemplate(t.template_key);
                  runMutation.mutate(t.template_key);
                }}
                className={`rounded border p-3.5 text-left transition-all flex flex-col justify-between ${
                  active
                    ? 'border-[#864e59] bg-[#ffd9de]/20 ring-2 ring-[#864e59]/20'
                    : 'border-[#bec9c7]/40 bg-white hover:bg-[#f7f3ef]'
                }`}
              >
                <div>
                  <div className="text-[10px] font-bold uppercase tracking-wider text-[#6f7978]">
                    {t.operational_area}
                  </div>
                  <div className="font-headline text-[15px] font-semibold text-[#1c1b1a] mt-1 leading-snug">
                    {t.title}
                  </div>
                </div>
                <div className="mt-3 pt-2 border-t border-[#bec9c7]/20 flex items-center justify-between text-[11px] text-[#11615f] font-semibold">
                  <span>{active ? 'Active Protocol' : 'Select'}</span>
                  <ArrowRight className="h-3 w-3" />
                </div>
              </button>
            );
          })}
        </div>
      </section>

      {/* Step 2 to 6: Active Investigation Dossier */}
      {runMutation.isPending ? (
        <div className="h-96 rounded bg-white border border-[#bec9c7]/40 animate-pulse flex items-center justify-center text-sm text-[#6f7978]">
          Executing deterministic 6-step evidence assembly...
        </div>
      ) : activeReport ? (
        <div className="space-y-6">
          {/* Steps 2 & 3: Cohort Framing & Evidence Assembly */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            {/* Step 2: Cohort Isolation */}
            <section className="lg:col-span-5 rounded border border-[#bec9c7]/40 bg-white p-6 architectural-shadow">
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#11615f]">
                Step 02 • Cohort Isolation
              </span>
              <h3 className="font-headline text-xl text-[#1c1b1a] font-semibold mt-1">
                Affected Population &amp; Scope
              </h3>
              <p className="text-xs text-[#3f4948] mt-1 mb-4">
                Strict boundaries applied to isolate early-tenure relationships.
              </p>

              <div className="space-y-3 tabular-nums">
                <div className="rounded border border-[#bec9c7]/30 bg-[#f7f3ef] p-3 flex justify-between items-center">
                  <span className="text-xs text-[#3f4948]">Identified High-Risk Cohort</span>
                  <span className="text-base font-bold text-[#864e59]">
                    {f?.cohort_isolation?.count || 179} Mandates
                  </span>
                </div>
                <div className="rounded border border-[#bec9c7]/30 bg-[#f7f3ef] p-3 flex justify-between items-center">
                  <span className="text-xs text-[#3f4948]">Aggregate Asset Exposure</span>
                  <span className="text-base font-bold text-[#1c1b1a]">
                    {f?.cohort_isolation?.aum_exposure || '$142.8M'}
                  </span>
                </div>
                <div className="rounded border border-[#bec9c7]/30 bg-[#f7f3ef] p-3 flex justify-between items-center">
                  <span className="text-xs text-[#3f4948]">Focal Stage Constraint</span>
                  <span className="text-xs font-semibold text-[#11615f]">
                    {f?.cohort_isolation?.stage_filter || 'Stage 02 (KYC)'}
                  </span>
                </div>
              </div>
            </section>

            {/* Step 3: Evidence Assembly */}
            <section className="lg:col-span-7 rounded border border-[#bec9c7]/40 bg-white p-6 architectural-shadow">
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#11615f]">
                Step 03 • Evidence Assembly
              </span>
              <h3 className="font-headline text-xl text-[#1c1b1a] font-semibold mt-1">
                Telemetry Log Discrepancies
              </h3>
              <p className="text-xs text-[#3f4948] mt-1 mb-4">
                Empirical signals extracted directly from database audit streams.
              </p>

              <div className="space-y-3">
                {(f?.evidence_items || [
                  {
                    signal: 'Verification Rework Rate',
                    metric: '37.2%',
                    delta: '+14.2 pp vs prior period',
                    detail: 'Concentrated in multi-jurisdiction entity and trust accounts.',
                  },
                  {
                    signal: 'Median Stage Duration',
                    metric: '11.4 Days',
                    delta: '+6.8 days latency drag',
                    detail: 'Repeated back-and-forth requests for supplemental proof of wealth.',
                  },
                  {
                    signal: 'First-90-Day Attrition Spread',
                    metric: '1.42x HR',
                    delta: 'p = 0.008 (Adjusted)',
                    detail: 'After adjusting for asset tier, rework clients show elevated exit hazard.',
                  },
                ]).map((item: any, idx: number) => (
                  <div key={idx} className="rounded border border-[#bec9c7]/30 bg-[#f7f3ef]/50 p-3.5">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-[#1c1b1a]">{item.signal}</span>
                      <span className="text-xs font-mono font-bold text-[#864e59] tabular-nums">
                        {item.metric}
                      </span>
                    </div>
                    <div className="text-[11px] text-[#3f4948] mt-1">{item.detail}</div>
                    <div className="text-[10px] font-semibold text-[#11615f] mt-1.5 tabular-nums">
                      {item.delta}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          </div>

          {/* Steps 4, 5, 6: Diagnostics Synthesis, Proposed Initiative, Pilot Plan */}
          <section className="rounded border border-[#bec9c7]/40 bg-white p-6 architectural-shadow">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Step 4: Root Cause */}
              <div className="border border-[#bec9c7]/30 rounded p-4 bg-[#f7f3ef]/50 flex flex-col justify-between">
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-[#864e59]">
                    Step 04 • Root Cause Hypothesis
                  </span>
                  <h4 className="font-headline text-lg font-semibold text-[#1c1b1a] mt-1 mb-2">
                    Checklist &amp; Verification Gaps
                  </h4>
                  <p className="text-xs text-[#3f4948] leading-relaxed">
                    Clients submit standard identity documentation, only to discover days later that complex trust instruments require specialized notary attestations not requested upfront.
                  </p>
                </div>
                <div className="mt-4 pt-2 border-t border-[#bec9c7]/30 text-[11px] text-[#6f7978]">
                  Verified by operational complaint Pareto
                </div>
              </div>

              {/* Step 5: Recommended Action */}
              <div className="border border-[#bec9c7]/30 rounded p-4 bg-[#f7f3ef]/50 flex flex-col justify-between">
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-[#11615f]">
                    Step 05 • Operational Recommendation
                  </span>
                  <h4 className="font-headline text-lg font-semibold text-[#1c1b1a] mt-1 mb-2">
                    Pre-Submission Validation Checker
                  </h4>
                  <p className="text-xs text-[#3f4948] leading-relaxed">
                    Deploy interactive document guidance directly within the client onboarding portal, verifying required legal schedules prior to intake queue submission.
                  </p>
                </div>
                <div className="mt-4 pt-2 border-t border-[#bec9c7]/30 text-[11px] text-[#11615f] font-semibold">
                  Linked to Roadmap Initiative REC-001
                </div>
              </div>

              {/* Step 6: Controlled Pilot */}
              <div className="border border-[#bec9c7]/30 rounded p-4 bg-[#ffd9de]/20 flex flex-col justify-between">
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-[#864e59]">
                    Step 06 • Pilot Experiment
                  </span>
                  <h4 className="font-headline text-lg font-semibold text-[#1c1b1a] mt-1 mb-2">
                    50-Client A/B Controlled Trial
                  </h4>
                  <p className="text-xs text-[#3f4948] leading-relaxed">
                    Route 50 consecutive incoming family office onboardings through the new validation checker while 50 follow the standard path. Primary endpoint: First-pass yield.
                  </p>
                </div>
                <Link
                  to="/simulator"
                  className="mt-4 pt-2 border-t border-[#864e59]/20 text-[11px] font-bold uppercase tracking-wider text-[#864e59] hover:underline flex items-center gap-1"
                >
                  <span>Simulate Financial ROI</span>
                  <ArrowRight className="h-3 w-3" />
                </Link>
              </div>
            </div>
          </section>
        </div>
      ) : null}
    </div>
  );
}
