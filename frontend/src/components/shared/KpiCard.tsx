import { Code2, TrendingDown, TrendingUp } from 'lucide-react';
import { useFilters } from '@/hooks/useFilters';
import type { KpiCardData } from '@/types/api';

export function KpiCard({ kpi }: { kpi: KpiCardData }) {
  const { openMetricDrawer } = useFilters();

  const isNeg =
    (kpi.direction === 'down' && kpi.favorable_direction === 'up') ||
    (kpi.direction === 'up' && kpi.favorable_direction === 'down');

  const fmtVal = `${kpi.value.toLocaleString(undefined, { maximumFractionDigits: 1 })}${kpi.unit}`;
  const deltaStr =
    kpi.change !== null
      ? `${kpi.change >= 0 ? '+' : ''}${kpi.change.toFixed(1)} ${kpi.change_unit}`
      : '—';

  return (
    <div className="rounded border border-[#bec9c7]/40 bg-white p-5 architectural-shadow flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between text-[10px] font-bold uppercase tracking-wider text-[#6f7978]">
          <span className="truncate pr-1">{kpi.label}</span>
          <button
            onClick={() => openMetricDrawer(kpi.key)}
            className="text-[#11615f] hover:underline"
            title="View calculation SQL"
          >
            <Code2 className="h-3.5 w-3.5" />
          </button>
        </div>
        <div className="mt-2 text-2xl font-bold text-[#1c1b1a] tabular-nums font-headline">
          {fmtVal}
        </div>
      </div>

      <div className="mt-3 pt-2 border-t border-[#ece7e4] flex items-center justify-between text-[11px] tabular-nums">
        <span
          className={`flex items-center gap-1 font-semibold ${
            isNeg ? 'text-[#864e59]' : 'text-[#11615f]'
          }`}
        >
          {kpi.direction === 'down' ? (
            <TrendingDown className="h-3 w-3" />
          ) : (
            <TrendingUp className="h-3 w-3" />
          )}
          <span>{deltaStr}</span>
        </span>
        <span className="text-[10px] text-[#6f7978]">vs prior</span>
      </div>
    </div>
  );
}
