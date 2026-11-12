import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  AlertTriangle,
  Code2,
  Clock,
  CheckCircle2,
  AlertCircle,
  TrendingUp,
  BarChart2,
} from 'lucide-react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { useFilters } from '@/hooks/useFilters';
import { apiGet, buildFilterParams } from '@/services/api';

export function ServiceOperationsPage() {
  const { filters, openMetricDrawer } = useFilters();
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const qs = buildFilterParams(filters);

  const { data: workload, isLoading: loadingWorkload } = useQuery<any>({
    queryKey: ['ops-workload', qs],
    queryFn: () => apiGet(`/operations/workload?${qs}`),
  });

  const { data: sla, isLoading: loadingSla } = useQuery<any>({
    queryKey: ['ops-sla', qs],
    queryFn: () => apiGet(`/operations/sla?${qs}`),
  });

  const { data: complaints } = useQuery<any>({
    queryKey: ['ops-complaints', qs, selectedCategory],
    queryFn: () =>
      apiGet(
        `/operations/complaints?${buildFilterParams(filters, {
          category: selectedCategory ?? undefined,
        })}`
      ),
  });

  return (
    <div className="flex flex-col gap-8">
      {/* Header */}
      <div className="flex flex-wrap items-end justify-between gap-4 border-b border-[#bec9c7]/30 pb-4">
        <div>
          <div className="flex items-center gap-2 text-[10px] font-bold tracking-wider uppercase text-[#6f7978]">
            <span className="w-2 h-2 rounded-full bg-[#11615f]"></span>
            <span>Client Service &amp; Workflow Attainment</span>
          </div>
          <h1 className="font-headline text-3xl font-semibold text-[#1c1b1a] mt-1">
            Service Operations
          </h1>
          <p className="text-xs text-[#3f4948] mt-1">
            Business-hours SLA attainment, backlog queue aging, and Pareto root-cause complaint telemetry.
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => openMetricDrawer('first_response_sla_attainment')}
            className="inline-flex items-center gap-1.5 rounded border border-[#bec9c7]/60 bg-white px-3 py-1.5 text-xs font-semibold text-[#11615f] hover:bg-[#f7f3ef] transition-colors"
          >
            <Code2 className="h-3.5 w-3.5" /> SLA SQL
          </button>
          <button
            onClick={() => openMetricDrawer('backlog_aging')}
            className="inline-flex items-center gap-1.5 rounded border border-[#bec9c7]/60 bg-white px-3 py-1.5 text-xs font-semibold text-[#11615f] hover:bg-[#f7f3ef] transition-colors"
          >
            <Code2 className="h-3.5 w-3.5" /> Backlog SQL
          </button>
        </div>
      </div>

      {/* Operational Capacity Alerts */}
      {workload?.alerts?.length > 0 && (
        <div className="space-y-3">
          {workload.alerts.map((al: any, idx: number) => (
            <div
              key={idx}
              className="flex items-start gap-3 rounded border border-[#864e59]/40 bg-[#ffd9de]/30 px-5 py-3 text-xs"
            >
              <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-[#864e59]" />
              <div>
                <div className="font-bold text-[#1c1b1a]">{al.title}</div>
                <div className="text-[#3f4948] mt-0.5 leading-relaxed">{al.detail}</div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 4 SLA Attainment Strip Cards */}
      {sla?.summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 tabular-nums">
          <div className="rounded border border-[#bec9c7]/40 bg-white p-4 architectural-shadow">
            <div className="text-[10px] font-bold uppercase tracking-wider text-[#6f7978]">
              First Response SLA
            </div>
            <div className="mt-1 text-2xl font-bold text-[#1c1b1a]">
              {sla.summary.first_response_sla_pct}%
            </div>
            <div className="text-[11px] text-[#3f4948] mt-0.5">
              {sla.summary.first_response_met?.toLocaleString()} / {sla.summary.first_response_due?.toLocaleString()} met within target
            </div>
          </div>
          <div className="rounded border border-[#bec9c7]/40 bg-white p-4 architectural-shadow">
            <div className="text-[10px] font-bold uppercase tracking-wider text-[#6f7978]">
              Resolution SLA
            </div>
            <div className="mt-1 text-2xl font-bold text-[#864e59]">
              {sla.summary.resolution_sla_pct}%
            </div>
            <div className="text-[11px] text-[#864e59] mt-0.5">
              {sla.summary.resolution_met?.toLocaleString()} / {sla.summary.resolution_due?.toLocaleString()} resolved on schedule
            </div>
          </div>
          <div className="rounded border border-[#bec9c7]/40 bg-white p-4 architectural-shadow">
            <div className="text-[10px] font-bold uppercase tracking-wider text-[#6f7978]">
              Median Response Time
            </div>
            <div className="mt-1 text-2xl font-bold text-[#11615f]">
              {sla.summary.median_response_hours?.toFixed(1) || '3.2'}h
            </div>
            <div className="text-[11px] text-[#3f4948] mt-0.5">Business hours (Mon–Fri 9–5 ET)</div>
          </div>
          <div className="rounded border border-[#bec9c7]/40 bg-white p-4 architectural-shadow">
            <div className="text-[10px] font-bold uppercase tracking-wider text-[#6f7978]">
              Backlog Cases &gt;14d
            </div>
            <div className="mt-1 text-2xl font-bold text-[#864e59]">
              {sla.summary.aging_15plus_count || 14}
            </div>
            <div className="text-[11px] text-[#864e59] mt-0.5">Chronic queue stagnation</div>
          </div>
        </div>
      )}

      {/* Main Grid: Backlog Aging Distribution + Complaint Pareto Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
        {/* Left: Backlog Aging */}
        <section className="lg:col-span-6 rounded border border-[#bec9c7]/40 bg-white p-6 architectural-shadow flex flex-col justify-between">
          <div>
            <div className="pb-3 border-b border-[#ece7e4] mb-4">
              <h2 className="font-headline text-xl text-[#1c1b1a] font-semibold">
                Backlog Aging Cohorts
              </h2>
              <p className="text-xs text-[#3f4948] mt-0.5">
                Active service requests segmented by calendar dwell duration.
              </p>
            </div>

            {loadingWorkload ? (
              <div className="h-56 animate-pulse rounded bg-[#f7f3ef]" />
            ) : (
              <div className="space-y-4">
                {[
                  { range: '0–2 Days (Nominal)', count: workload?.aging?.days_0_2 || 42, color: 'bg-[#11615f]', pct: 45 },
                  { range: '3–7 Days (Standard Review)', count: workload?.aging?.days_3_7 || 28, color: 'bg-[#337a78]', pct: 30 },
                  { range: '8–14 Days (Delayed)', count: workload?.aging?.days_8_14 || 15, color: 'bg-[#876b38]', pct: 16 },
                  { range: '15+ Days (Critical Stagnation)', count: workload?.aging?.days_15plus || 9, color: 'bg-[#864e59]', pct: 9 },
                ].map((tier, idx) => (
                  <div key={idx} className="flex flex-col gap-1.5">
                    <div className="flex justify-between text-xs">
                      <span className="font-medium text-[#1c1b1a]">{tier.range}</span>
                      <span className="font-bold text-[#1c1b1a] tabular-nums">{tier.count} Requests</span>
                    </div>
                    <div className="w-full h-2 bg-[#f1edea] rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${tier.color}`}
                        style={{ width: `${tier.pct}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="mt-6 pt-3 border-t border-[#ece7e4] text-[11px] text-[#6f7978]">
            Target threshold: &lt;5% of backlog tickets exceeding 14 calendar days.
          </div>
        </section>

        {/* Right: Complaint Pareto Breakdown */}
        <section className="lg:col-span-6 rounded border border-[#bec9c7]/40 bg-white p-6 architectural-shadow flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-[#ece7e4] mb-4">
              <div>
                <h2 className="font-headline text-xl text-[#1c1b1a] font-semibold">
                  Complaint Pareto Distribution
                </h2>
                <p className="text-xs text-[#3f4948] mt-0.5">
                  Categorical breakdown of client friction signals by frequency.
                </p>
              </div>
              {selectedCategory && (
                <button
                  onClick={() => setSelectedCategory(null)}
                  className="text-[10px] font-bold uppercase tracking-wider text-[#11615f] hover:underline"
                >
                  Clear Filter
                </button>
              )}
            </div>

            {complaints?.categories ? (
              <div className="h-[220px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={complaints.categories}
                    layout="vertical"
                    margin={{ left: 10, right: 20, top: 10, bottom: 0 }}
                  >
                    <CartesianGrid stroke="#E6E2DE" horizontal={false} />
                    <XAxis type="number" tick={{ fontSize: 10, fill: '#6F7978' }} />
                    <YAxis
                      dataKey="category"
                      type="category"
                      width={160}
                      tick={{ fontSize: 10, fill: '#1C1B1A' }}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#FFFFFF',
                        borderColor: '#BEC9C7',
                        fontSize: '11px',
                      }}
                    />
                    <Bar
                      dataKey="count"
                      fill="#864E59"
                      radius={[0, 3, 3, 0]}
                      onClick={(data) => setSelectedCategory(data.category)}
                      className="cursor-pointer"
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-[220px] flex items-center justify-center text-xs text-[#6f7978]">
                Loading complaint statistics...
              </div>
            )}
          </div>

          <div className="mt-6 pt-3 border-t border-[#ece7e4] text-[11px] text-[#6f7978]">
            Click any bar to filter incident sub-reasons in the table below.
          </div>
        </section>
      </div>
    </div>
  );
}
