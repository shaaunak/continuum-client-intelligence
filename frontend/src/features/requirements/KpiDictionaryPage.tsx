import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Code2, Search } from 'lucide-react';
import { useFilters } from '@/hooks/useFilters';
import { apiGet } from '@/services/api';

export function KpiDictionaryPage() {
  const { openMetricDrawer } = useFilters();
  const [search, setSearch] = useState('');

  const { data: metrics, isLoading } = useQuery<any[]>({
    queryKey: ['metrics-dictionary'],
    queryFn: () => apiGet('/metrics/dictionary'),
  });

  const filtered = (metrics || []).filter(
    (m) =>
      m.kpi_name.toLowerCase().includes(search.toLowerCase()) ||
      m.metric_key.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-[#17242D]">KPI Dictionary &amp; SQL Lineage</h1>
          <p className="mt-1 text-sm text-[#65727A]">
            Authoritative definitions, numerator/denominator rules, exclusions, and PostgreSQL query templates.
          </p>
        </div>
        <div className="flex items-center gap-2 rounded-md border border-[#E6E9E6] bg-white px-3 py-1.5">
          <Search className="h-4 w-4 text-[#65727A]" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Filter KPIs..."
            className="w-48 bg-transparent text-xs outline-none"
          />
        </div>
      </div>

      {isLoading ? (
        <div className="h-48 animate-pulse rounded-lg bg-white" />
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          {filtered.map((m) => (
            <div key={m.metric_key} className="rounded-lg border border-[#E6E9E6] bg-white p-5">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <div className="font-mono text-[11px] text-[#176C5B]">{m.metric_key}</div>
                  <h2 className="mt-0.5 text-base font-semibold text-[#17242D]">{m.kpi_name}</h2>
                </div>
                <button
                  onClick={() => openMetricDrawer(m.metric_key)}
                  className="inline-flex items-center gap-1 rounded border border-[#E6E9E6] px-2.5 py-1 text-xs font-medium text-[#20364A] hover:bg-[#F7F8F6]"
                >
                  <Code2 className="h-3.5 w-3.5 text-[#176C5B]" /> Inspect SQL
                </button>
              </div>
              <p className="mt-2 text-xs text-[#17242D]">{m.business_meaning}</p>
              <div className="mt-3 rounded bg-[#F7F8F6] p-2.5 font-mono text-[11px] text-[#20364A]">
                {m.formula}
              </div>
              <div className="mt-3 grid grid-cols-2 gap-2 text-[11px] text-[#65727A]">
                <div>
                  <strong className="text-[#17242D]">Numerator:</strong> {m.numerator}
                </div>
                <div>
                  <strong className="text-[#17242D]">Denominator:</strong> {m.denominator}
                </div>
                <div>
                  <strong className="text-[#17242D]">Source:</strong> <span className="font-mono">{m.data_source}</span>
                </div>
                <div>
                  <strong className="text-[#17242D]">Exclusions:</strong> {m.exclusions}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
