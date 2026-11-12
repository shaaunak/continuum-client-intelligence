import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Check, Copy, ExternalLink, X, Code2 } from 'lucide-react';
import { useState } from 'react';
import { useFilters } from '@/hooks/useFilters';
import { apiGet } from '@/services/api';

export function SqlEvidenceDrawer() {
  const { activeMetricKey, closeMetricDrawer } = useFilters();
  const [copied, setCopied] = useState(false);

  const { data: metricDef } = useQuery<any>({
    queryKey: ['metric-definition', activeMetricKey],
    queryFn: () => apiGet(`/governance/kpis/${activeMetricKey}`),
    enabled: Boolean(activeMetricKey),
  });

  useEffect(() => {
    setCopied(false);
  }, [activeMetricKey]);

  if (!activeMetricKey) return null;

  const handleCopy = () => {
    if (!metricDef?.sql_definition) return;
    navigator.clipboard.writeText(metricDef.sql_definition);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      className="fixed inset-0 z-50 bg-[#1c1b1a]/40 backdrop-blur-xs flex justify-end"
      onClick={closeMetricDrawer}
    >
      <div
        className="w-full max-w-xl bg-white h-full shadow-2xl flex flex-col border-l border-[#bec9c7]/50"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-[#ece7e4] px-6 py-4 bg-[#f7f3ef]">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-[#11615f] text-white flex items-center justify-center">
              <Code2 className="h-3.5 w-3.5" />
            </div>
            <div>
              <div className="text-[10px] font-bold uppercase tracking-wider text-[#6f7978]">
                Deterministic Formula
              </div>
              <h2 className="font-headline text-lg font-semibold text-[#1c1b1a]">
                {metricDef?.kpi_name || activeMetricKey}
              </h2>
            </div>
          </div>
          <button
            onClick={closeMetricDrawer}
            className="p-1 rounded text-[#6f7978] hover:text-[#1c1b1a] hover:bg-[#ece7e4]"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-5 text-xs text-[#3f4948]">
          <div>
            <div className="text-[10px] font-bold uppercase tracking-wider text-[#6f7978]">
              Business Definition
            </div>
            <p className="mt-1 text-sm text-[#1c1b1a] leading-relaxed">
              {metricDef?.business_definition || 'Transparent SQL computation extracted from database views.'}
            </p>
          </div>

          <div>
            <div className="flex items-center justify-between pb-1">
              <div className="text-[10px] font-bold uppercase tracking-wider text-[#6f7978]">
                PostgreSQL Implementation Query
              </div>
              <button
                onClick={handleCopy}
                className="inline-flex items-center gap-1 text-[11px] font-semibold text-[#11615f] hover:underline"
              >
                {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                <span>{copied ? 'Copied' : 'Copy SQL'}</span>
              </button>
            </div>
            <pre className="mt-1 rounded bg-[#1c1b1a] text-[#f4f0ec] p-4 font-mono text-[11px] leading-relaxed overflow-x-auto border border-[#31302e]">
              {metricDef?.sql_definition || '-- SQL query unavailable for this metric.'}
            </pre>
          </div>

          <div className="grid grid-cols-2 gap-3 pt-2">
            <div className="rounded border border-[#bec9c7]/30 bg-[#f7f3ef] p-3">
              <div className="text-[10px] font-bold text-[#6f7978] uppercase">Target Standard</div>
              <div className="text-sm font-semibold text-[#1c1b1a] mt-0.5">
                {metricDef?.target_sla || 'N/A'}
              </div>
            </div>
            <div className="rounded border border-[#bec9c7]/30 bg-[#f7f3ef] p-3">
              <div className="text-[10px] font-bold text-[#6f7978] uppercase">Owner</div>
              <div className="text-sm font-semibold text-[#1c1b1a] mt-0.5">
                {metricDef?.business_owner || 'Wealth Operations Committee'}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
