import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Code2, Info, Users, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { useFilters } from '@/hooks/useFilters';
import { apiGet, buildFilterParams } from '@/services/api';

export function AdvisorIntelligencePage() {
  const { filters, openMetricDrawer } = useFilters();
  const [selectedAdvisorId, setSelectedAdvisorId] = useState<string | null>(null);
  const [supportFilter, setSupportFilter] = useState(false);

  const qs = buildFilterParams(filters);
  const { data, isLoading } = useQuery<any>({
    queryKey: ['advisors-list', qs],
    queryFn: () => apiGet(`/advisors?${qs}`),
  });

  const { data: detail } = useQuery<any>({
    queryKey: ['advisor-detail', selectedAdvisorId],
    queryFn: () => apiGet(`/advisors/${selectedAdvisorId}`),
    enabled: Boolean(selectedAdvisorId),
  });

  const rows = (data?.advisors || []).filter((a: any) =>
    supportFilter ? a.support_needed : true
  );

  return (
    <div className="flex flex-col gap-8">
      {/* Header */}
      <div className="flex flex-wrap items-end justify-between gap-4 border-b border-[#bec9c7]/30 pb-4">
        <div>
          <div className="flex items-center gap-2 text-[10px] font-bold tracking-wider uppercase text-[#6f7978]">
            <span className="w-2 h-2 rounded-full bg-[#11615f]"></span>
            <span>Case-Mix Adjusted Workload Analytics</span>
          </div>
          <h1 className="font-headline text-3xl font-semibold text-[#1c1b1a] mt-1">
            Advisor Intelligence
          </h1>
          <p className="text-xs text-[#3f4948] mt-1">
            Observed-vs-Expected (O/E) complexity-adjusted workload metrics to support capacity planning.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <label className="inline-flex cursor-pointer items-center gap-2 rounded border border-[#bec9c7]/50 bg-white px-3 py-1.5 text-xs font-medium text-[#1c1b1a]">
            <input
              type="checkbox"
              checked={supportFilter}
              onChange={(e) => setSupportFilter(e.target.checked)}
              className="accent-[#11615f]"
            />
            <span>High Utilization Only (≥95%)</span>
          </label>
          <button
            onClick={() => openMetricDrawer('advisor_utilization')}
            className="inline-flex items-center gap-1.5 rounded border border-[#bec9c7]/60 bg-white px-3 py-1.5 text-xs font-semibold text-[#11615f] hover:bg-[#f7f3ef] transition-colors"
          >
            <Code2 className="h-3.5 w-3.5" /> Utilization SQL
          </button>
        </div>
      </div>

      {/* Fairness & Case-Mix Notice */}
      <div className="rounded border border-[#bec9c7]/40 bg-[#f7f3ef] p-4 text-xs text-[#3f4948] flex items-start gap-3">
        <Info className="h-4 w-4 shrink-0 text-[#11615f] mt-0.5" />
        <span className="leading-relaxed">
          <strong>Fairness &amp; Governance Standard:</strong> Raw breach rates unfairly penalize advisors managing complex offshore trusts. CONTINUUM normalizes operational metrics against expected case complexity (O/E breach ratio) to identify teams requiring additional paraplanner support.
        </span>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">
        {/* Left Column: Advisor Ledger Table (Col 8) */}
        <section className="rounded border border-[#bec9c7]/40 bg-white architectural-shadow xl:col-span-8 overflow-hidden">
          <div className="overflow-x-auto custom-scrollbar">
            <table className="w-full text-left text-xs tabular-nums">
              <thead>
                <tr className="border-b border-[#bec9c7]/40 bg-[#f7f3ef] text-[10px] font-bold uppercase tracking-wider text-[#6f7978]">
                  <th className="px-5 py-3">Advisor</th>
                  <th className="px-3 py-3">Team</th>
                  <th className="px-3 py-3 text-right">Clients</th>
                  <th className="px-3 py-3 text-right">Active Cases</th>
                  <th className="px-3 py-3 text-right">Util %</th>
                  <th className="px-3 py-3 text-right">SLA %</th>
                  <th className="px-5 py-3 text-right">O/E Ratio</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#ece7e4]">
                {isLoading ? (
                  <tr>
                    <td colSpan={7} className="px-5 py-12 text-center text-[#6f7978]">
                      Loading advisor performance telemetry...
                    </td>
                  </tr>
                ) : (
                  rows.map((a: any) => {
                    const isSelected = selectedAdvisorId === a.advisor_id;
                    const highUtil = a.utilization_pct >= 95;
                    return (
                      <tr
                        key={a.advisor_id}
                        onClick={() => setSelectedAdvisorId(a.advisor_id)}
                        className={`cursor-pointer transition-colors ${
                          isSelected ? 'bg-[#a9efec]/20' : 'hover:bg-[#f7f3ef]/60'
                        }`}
                      >
                        <td className="px-5 py-3.5">
                          <div className="font-semibold text-[#1c1b1a]">{a.display_name}</div>
                          <div className="text-[10px] text-[#6f7978]">{a.advisor_id}</div>
                        </td>
                        <td className="px-3 py-3.5 text-[#3f4948] font-medium">{a.team_id}</td>
                        <td className="px-3 py-3.5 text-right font-medium text-[#1c1b1a]">
                          {a.active_client_count}
                        </td>
                        <td className="px-3 py-3.5 text-right text-[#3f4948]">{a.open_cases_count}</td>
                        <td className="px-3 py-3.5 text-right">
                          <span
                            className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                              highUtil ? 'bg-[#ffd9de] text-[#864e59]' : 'bg-[#f7f3ef] text-[#1c1b1a]'
                            }`}
                          >
                            {a.utilization_pct?.toFixed(0)}%
                          </span>
                        </td>
                        <td className="px-3 py-3.5 text-right font-medium text-[#1c1b1a]">
                          {a.first_response_sla_pct?.toFixed(1)}%
                        </td>
                        <td className="px-5 py-3.5 text-right font-mono font-bold text-[#864e59]">
                          {a.oe_breach_ratio?.toFixed(2) || '1.00'}x
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </section>

        {/* Right Column: Selected Advisor Capacity Dossier (Col 4) */}
        <aside className="rounded border border-[#bec9c7]/40 bg-white p-6 architectural-shadow xl:col-span-4 flex flex-col gap-4">
          <div className="pb-3 border-b border-[#ece7e4]">
            <span className="text-[10px] font-bold uppercase tracking-wider text-[#11615f]">
              Workload Dossier
            </span>
            <h3 className="font-headline text-2xl font-semibold text-[#1c1b1a] mt-0.5">
              {detail?.display_name || 'Select an Advisor'}
            </h3>
            <p className="text-xs text-[#6f7978]">
              {detail ? `${detail.title || 'Senior Wealth Partner'} · Team ${detail.team_id}` : 'Click any row in the ledger to inspect capacity.'}
            </p>
          </div>

          {detail && (
            <div className="space-y-4 tabular-nums text-xs">
              <div className="rounded border border-[#bec9c7]/30 bg-[#f7f3ef] p-4 flex justify-between items-center">
                <span className="text-[#3f4948]">Capacity Utilization</span>
                <span className="text-lg font-bold text-[#864e59]">
                  {detail.utilization_pct?.toFixed(0)}%
                </span>
              </div>

              <div className="rounded border border-[#bec9c7]/30 bg-[#f7f3ef] p-4 flex justify-between items-center">
                <span className="text-[#3f4948]">Managed Client Relationships</span>
                <span className="text-lg font-bold text-[#1c1b1a]">
                  {detail.active_client_count}
                </span>
              </div>

              <div className="rounded border border-[#bec9c7]/30 bg-[#f7f3ef] p-4 flex justify-between items-center">
                <span className="text-[#3f4948]">Observed vs Expected Breaches</span>
                <span className="text-lg font-mono font-bold text-[#864e59]">
                  {detail.oe_breach_ratio?.toFixed(2)}x
                </span>
              </div>

              {detail.support_needed && (
                <div className="rounded border border-[#864e59]/30 bg-[#ffd9de]/30 p-3 text-[11px] text-[#864e59]">
                  <strong>Support Recommended:</strong> Advisor exceeds recommended 85% capacity threshold. Case re-balancing suggested.
                </div>
              )}
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}
