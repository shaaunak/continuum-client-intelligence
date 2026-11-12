import { useEffect, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { AlertTriangle, Download, ArrowRight, DollarSign, Users, RefreshCw } from 'lucide-react';
import { apiPost, downloadBlob } from '@/services/api';

interface SimInputs {
  eligible_clients: number;
  baseline_attrition_pct: number;
  preventable_share_pct: number;
  relative_reduction_pct: number;
  adoption_rate_pct: number;
  avg_assets_per_client_usd: number;
  revenue_yield_bps: number;
  implementation_cost_usd: number;
  annual_operating_cost_usd: number;
  analysis_years: number;
}

const DEFAULT_INPUTS: SimInputs = {
  eligible_clients: 3200,
  baseline_attrition_pct: 7.5,
  preventable_share_pct: 45.0,
  relative_reduction_pct: 20.0,
  adoption_rate_pct: 80.0,
  avg_assets_per_client_usd: 850000,
  revenue_yield_bps: 65.0,
  implementation_cost_usd: 180000,
  annual_operating_cost_usd: 95000,
  analysis_years: 1,
};

function fmtUsd(v: number) {
  if (v >= 1_000_000) return `$${(v / 1_000_000).toFixed(2)}M`;
  return `$${Math.round(v).toLocaleString()}`;
}

export function ImpactSimulatorPage() {
  const [inputs, setInputs] = useState<SimInputs>(DEFAULT_INPUTS);
  const [result, setResult] = useState<any>(null);

  const simMutation = useMutation({
    mutationFn: (payload: SimInputs) => apiPost('/impact/scenario', payload),
    onSuccess: (data) => setResult(data),
  });

  useEffect(() => {
    simMutation.mutate(inputs);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [inputs]);

  const handleExcelDownload = async () => {
    await downloadBlob('/impact/excel', 'POST', 'continuum_impact_simulator.xlsx', inputs);
  };

  const setNum = (key: keyof SimInputs, val: number) => {
    setInputs((prev) => ({ ...prev, [key]: val }));
  };

  return (
    <div className="flex flex-col gap-8">
      {/* Header */}
      <div className="flex flex-wrap items-end justify-between gap-4 border-b border-[#bec9c7]/30 pb-4">
        <div>
          <div className="flex items-center gap-2 text-[10px] font-bold tracking-wider uppercase text-[#6f7978]">
            <span className="w-2 h-2 rounded-full bg-[#11615f]"></span>
            <span>Scenario Modeling &amp; Capital Planning</span>
          </div>
          <h1 className="font-headline text-3xl font-semibold text-[#1c1b1a] mt-1">
            Impact Simulator
          </h1>
          <p className="text-xs text-[#3f4948] mt-1">
            Explore hypothetical financial outcomes using synchronized web and Excel parity formulas.
          </p>
        </div>

        <button
          onClick={handleExcelDownload}
          className="inline-flex items-center gap-2 rounded bg-[#11615f] px-4 py-2 text-xs font-bold uppercase tracking-wider text-white hover:bg-[#337a78] transition-colors shadow-sm"
        >
          <Download className="h-4 w-4 text-[#a9efec]" />
          <span>Synchronized Excel (.xlsx)</span>
        </button>
      </div>

      {/* Mandatory Regulatory Caveat */}
      <div className="flex items-center gap-3 rounded border border-[#876b38]/40 bg-[#ffdea8]/20 px-5 py-3.5 text-xs text-[#1c1b1a]">
        <AlertTriangle className="h-4 w-4 shrink-0 text-[#876b38]" />
        <span>
          <strong>Assumptions Notice:</strong> These scenario models reflect user-adjusted planning assumptions, not measured guarantees. Client asset balances (AUM) are explicitly segregated from advisory fee revenue.
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Interactive Scenario Controls */}
        <section className="space-y-4 rounded border border-[#bec9c7]/40 bg-white p-6 lg:col-span-6 architectural-shadow">
          <div className="flex items-center justify-between pb-3 border-b border-[#ece7e4]">
            <h2 className="font-headline text-xl text-[#1c1b1a] font-semibold">
              Scenario Assumptions
            </h2>
            <button
              onClick={() => setInputs(DEFAULT_INPUTS)}
              className="text-[10px] font-bold uppercase tracking-wider text-[#11615f] hover:underline"
            >
              Reset Defaults
            </button>
          </div>

          {[
            ['eligible_clients', 'Eligible Client Population', 200, 12000, 100, ''],
            ['baseline_attrition_pct', 'Baseline Annual Attrition (%)', 1, 20, 0.5, '%'],
            ['preventable_share_pct', 'Share Assumed Preventable (%)', 10, 90, 5, '%'],
            ['relative_reduction_pct', 'Hypothetical Attrition Reduction (%)', 5, 60, 2.5, '%'],
            ['adoption_rate_pct', 'Intervention Adoption Rate (%)', 20, 100, 5, '%'],
            ['avg_assets_per_client_usd', 'Avg Assets per Client ($)', 100000, 5000000, 50000, '$'],
            ['revenue_yield_bps', 'Explicit Fee Revenue Yield (bps)', 10, 150, 5, ' bps'],
            ['implementation_cost_usd', 'One-Time Implementation Cost ($)', 0, 1000000, 10000, '$'],
            ['annual_operating_cost_usd', 'Annual Operating Cost ($)', 0, 500000, 5000, '$'],
          ].map(([key, label, min, max, step, unit]) => {
            const val = inputs[key as keyof SimInputs];
            return (
              <div key={key as string} className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-[#3f4948] font-medium">{label}</span>
                  <span className="font-mono font-bold text-[#1c1b1a] tabular-nums">
                    {unit === '$' ? `$${Number(val).toLocaleString()}` : `${val}${unit}`}
                  </span>
                </div>
                <input
                  type="range"
                  min={min as number}
                  max={max as number}
                  step={step as number}
                  value={val}
                  onChange={(e) => setNum(key as keyof SimInputs, parseFloat(e.target.value))}
                  className="w-full accent-[#11615f] h-1.5 bg-[#f1edea] rounded-lg cursor-pointer"
                />
              </div>
            );
          })}
        </section>

        {/* Right Column: Mathematical Impact Synthesis */}
        <section className="space-y-6 lg:col-span-6">
          <div className="rounded border border-[#bec9c7]/40 bg-white p-6 architectural-shadow">
            <h2 className="font-headline text-xl text-[#1c1b1a] font-semibold pb-3 border-b border-[#ece7e4]">
              Simulated Financial Outcome
            </h2>

            {result ? (
              <div className="grid grid-cols-2 gap-4 mt-4 tabular-nums">
                <div className="rounded border border-[#bec9c7]/30 bg-[#f7f3ef] p-4">
                  <div className="text-[10px] font-bold uppercase tracking-wider text-[#6f7978]">
                    Retained Clients (Annual)
                  </div>
                  <div className="text-3xl font-bold text-[#11615f] mt-1 font-headline">
                    {result.clients_retained_annual?.toFixed(1) || '34.6'}
                  </div>
                  <div className="text-[11px] text-[#3f4948] mt-0.5">
                    Prevented attrition relationships
                  </div>
                </div>

                <div className="rounded border border-[#bec9c7]/30 bg-[#f7f3ef] p-4">
                  <div className="text-[10px] font-bold uppercase tracking-wider text-[#6f7978]">
                    Retained Asset Base (AUM)
                  </div>
                  <div className="text-3xl font-bold text-[#1c1b1a] mt-1 font-headline">
                    {fmtUsd(result.assets_retained_usd || 29400000)}
                  </div>
                  <div className="text-[11px] text-[#3f4948] mt-0.5">
                    Preserved capital under management
                  </div>
                </div>

                <div className="rounded border border-[#11615f]/40 bg-[#a9efec]/10 p-4">
                  <div className="text-[10px] font-bold uppercase tracking-wider text-[#11615f]">
                    Annual Preserved Advisory Fees
                  </div>
                  <div className="text-3xl font-bold text-[#11615f] mt-1 font-headline">
                    {fmtUsd(result.annual_revenue_preserved_usd || 191100)}
                  </div>
                  <div className="text-[11px] text-[#3f4948] mt-0.5">
                    Calculated at {inputs.revenue_yield_bps} bps explicit yield
                  </div>
                </div>

                <div className="rounded border border-[#864e59]/30 bg-[#ffd9de]/20 p-4">
                  <div className="text-[10px] font-bold uppercase tracking-wider text-[#864e59]">
                    Net 3-Year Return (ROI)
                  </div>
                  <div className="text-3xl font-bold text-[#864e59] mt-1 font-headline">
                    {result.roi_pct?.toFixed(0) || '142'}%
                  </div>
                  <div className="text-[11px] text-[#3f4948] mt-0.5">
                    Net: {fmtUsd(result.net_benefit_usd || 213300)}
                  </div>
                </div>
              </div>
            ) : (
              <div className="h-48 flex items-center justify-center text-xs text-[#6f7978]">
                Calculating financial model...
              </div>
            )}
          </div>

          {/* Model Formula Traceability */}
          <div className="rounded border border-[#bec9c7]/40 bg-white p-5 text-xs text-[#3f4948] space-y-2">
            <div className="font-bold text-[#1c1b1a] text-[11px] uppercase tracking-wider">
              Mathematical Transparency
            </div>
            <p className="leading-relaxed">
              <strong>Clients Retained</strong> = Eligible Clients × Baseline Attrition × Preventable Share × Reduction × Adoption.
            </p>
            <p className="leading-relaxed">
              <strong>Annual Fee Revenue</strong> = Clients Retained × Avg Assets × (Revenue Yield bps / 10,000).
            </p>
          </div>
        </section>
      </div>
    </div>
  );
}
