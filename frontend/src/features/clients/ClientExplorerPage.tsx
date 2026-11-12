import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Search, ChevronLeft, ChevronRight, ArrowRight, UserCheck, AlertTriangle } from 'lucide-react';
import { useFilters } from '@/hooks/useFilters';
import { apiGet, buildFilterParams } from '@/services/api';

function StatusPill({ status }: { status: string }) {
  const styles: Record<string, string> = {
    Engaged: 'bg-[#a9efec]/40 text-[#00201f] border border-[#11615f]/30',
    'At Risk': 'bg-[#ffd9de] text-[#360d17] border border-[#864e59]/30 font-bold',
    Inactive: 'bg-[#ffdea8]/50 text-[#271900] border border-[#876b38]/30',
    Exited: 'bg-[#e6e2de] text-[#1c1b1a] border border-[#bec9c7]/40',
    Abandoned: 'bg-[#ffd9de]/50 text-[#864e59] border border-[#864e59]/30',
    Onboarding: 'bg-[#f7f3ef] text-[#11615f] border border-[#11615f]/20',
  };
  return (
    <span
      className={`rounded px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider ${
        styles[status] || 'bg-[#f7f3ef] text-[#6f7978]'
      }`}
    >
      {status}
    </span>
  );
}

export function ClientExplorerPage() {
  const { filters } = useFilters();
  const [search, setSearch] = useState('');
  const [engStatus, setEngStatus] = useState('All');
  const [page, setPage] = useState(1);

  const qs = buildFilterParams(filters, {
    search,
    engagement_status: engStatus,
    page,
    page_size: 20,
  });

  const { data, isLoading } = useQuery<any>({
    queryKey: ['clients-list', qs],
    queryFn: () => apiGet(`/clients?${qs}`),
  });

  const totalPages = data ? Math.max(1, Math.ceil(data.total / 20)) : 1;

  return (
    <div className="flex flex-col gap-8">
      {/* Header */}
      <div className="flex flex-wrap items-end justify-between gap-4 border-b border-[#bec9c7]/30 pb-4">
        <div>
          <div className="flex items-center gap-2 text-[10px] font-bold tracking-wider uppercase text-[#6f7978]">
            <span className="w-2 h-2 rounded-full bg-[#11615f]"></span>
            <span>Synthetic Client Registry</span>
          </div>
          <h1 className="font-headline text-3xl font-semibold text-[#1c1b1a] mt-1">
            Client Explorer
          </h1>
          <p className="text-xs text-[#3f4948] mt-1">
            Search synthetic client identifiers, inspect deterministic engagement flags, and drill into full lifecycle timelines.
          </p>
        </div>
      </div>

      {/* Search & Engagement Filter Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 rounded border border-[#bec9c7]/40 bg-white p-4 architectural-shadow">
        <div className="flex items-center gap-2.5 rounded border border-[#bec9c7]/60 bg-[#f7f3ef] px-3.5 py-2">
          <Search className="h-4 w-4 text-[#6f7978]" />
          <input
            type="text"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            placeholder="Search Client ID (e.g. C-000482)..."
            className="w-64 bg-transparent text-xs text-[#1c1b1a] outline-none placeholder-[#6f7978]"
          />
        </div>

        <div className="flex flex-wrap items-center gap-1.5 text-xs">
          {['All', 'At Risk', 'Inactive', 'Engaged', 'Onboarding', 'Exited'].map((st) => (
            <button
              key={st}
              onClick={() => {
                setEngStatus(st);
                setPage(1);
              }}
              className={`rounded px-3 py-1.5 text-[10px] font-bold tracking-wider uppercase transition-colors ${
                engStatus === st
                  ? 'bg-[#11615f] text-white'
                  : 'border border-[#bec9c7]/50 bg-white text-[#3f4948] hover:bg-[#f7f3ef]'
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Client Table */}
      <div className="rounded border border-[#bec9c7]/40 bg-white architectural-shadow overflow-hidden">
        <div className="overflow-x-auto custom-scrollbar">
          <table className="w-full text-left text-xs tabular-nums">
            <thead>
              <tr className="border-b border-[#bec9c7]/40 bg-[#f7f3ef] text-[10px] font-bold uppercase tracking-wider text-[#6f7978]">
                <th className="px-5 py-3">Client Identifier</th>
                <th className="px-3 py-3">Segment</th>
                <th className="px-3 py-3">Asset Tier</th>
                <th className="px-3 py-3">Advisor &amp; Team</th>
                <th className="px-3 py-3">Lifecycle Stage</th>
                <th className="px-3 py-3">Status</th>
                <th className="px-3 py-3 text-right">AUM Balance</th>
                <th className="px-5 py-3 text-right">Dossier</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#ece7e4]">
              {isLoading ? (
                <tr>
                  <td colSpan={8} className="px-5 py-12 text-center text-[#6f7978]">
                    Loading client directory...
                  </td>
                </tr>
              ) : data?.clients?.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-5 py-12 text-center text-[#6f7978]">
                    No clients match current search criteria.
                  </td>
                </tr>
              ) : (
                data?.clients?.map((c: any) => (
                  <tr key={c.client_id} className="hover:bg-[#f7f3ef]/60 transition-colors">
                    <td className="px-5 py-3.5 font-mono text-[11px] font-bold text-[#11615f]">
                      <Link to={`/clients/${c.client_id}`} className="hover:underline">
                        {c.client_id}
                      </Link>
                    </td>
                    <td className="px-3 py-3.5 text-[#1c1b1a]">{c.segment}</td>
                    <td className="px-3 py-3.5 text-[#3f4948] font-medium">{c.asset_tier}</td>
                    <td className="px-3 py-3.5 text-[#3f4948]">
                      {c.advisor_name} ({c.team_id})
                    </td>
                    <td className="px-3 py-3.5 text-[#1c1b1a]">{c.current_stage || 'Complete'}</td>
                    <td className="px-3 py-3.5">
                      <StatusPill status={c.engagement_status} />
                    </td>
                    <td className="px-3 py-3.5 text-right font-semibold text-[#1c1b1a]">
                      ${(c.current_aum_usd / 1e6).toFixed(2)}M
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <Link
                        to={`/clients/${c.client_id}`}
                        className="inline-flex items-center gap-1 text-[11px] font-bold text-[#11615f] hover:underline"
                      >
                        <span>View</span>
                        <ArrowRight className="h-3 w-3" />
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="flex items-center justify-between px-5 py-3 border-t border-[#ece7e4] bg-[#f7f3ef] text-xs">
          <span className="text-[#6f7978]">
            Showing Page <strong>{page}</strong> of <strong>{totalPages}</strong> ({data?.total || 0} Total Records)
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="p-1 rounded border border-[#bec9c7]/40 bg-white text-[#3f4948] disabled:opacity-40"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              className="p-1 rounded border border-[#bec9c7]/40 bg-white text-[#3f4948] disabled:opacity-40"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
