import { useQuery } from '@tanstack/react-query';
import { CheckCircle2, XCircle } from 'lucide-react';
import { apiGet } from '@/services/api';

export function DataQualityPage() {
  const { data, isLoading } = useQuery<any>({
    queryKey: ['data-quality'],
    queryFn: () => apiGet('/data-quality'),
  });

  if (isLoading || !data) {
    return <div className="h-48 animate-pulse rounded-lg bg-white" />;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-[#17242D]">
            Data Quality &amp; Reconciliation
          </h1>
          <p className="mt-1 text-sm text-[#65727A]">
            Automated PostgreSQL integrity checks verifying chronology, SLA boundaries, and referential consistency.
          </p>
        </div>
        <div className="rounded-md border border-[#E6E9E6] bg-white px-3 py-1.5 font-mono text-xs text-[#20364A]">
          Seed: {data.seed} · Scale: {data.dataset_scale} · As-Of: {data.as_of_date}
        </div>
      </div>

      {/* Integrity Checks */}
      <section className="rounded-lg border border-[#E6E9E6] bg-white p-5">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold text-[#17242D]">Automated Integrity Audit</h2>
          <span
            className={`rounded px-2.5 py-0.5 text-xs font-semibold ${
              data.all_passed ? 'bg-[#E9F3EE] text-[#176C5B]' : 'bg-[#BB5656]/10 text-[#BB5656]'
            }`}
          >
            {data.all_passed ? 'ALL CHECKS PASSED' : 'ISSUES DETECTED'}
          </span>
        </div>

        <div className="mt-4 divide-y divide-[#E6E9E6]/60 text-xs">
          {data.checks.map((c: any) => (
            <div key={c.check_name} className="flex items-center justify-between py-3">
              <div className="flex items-start gap-2.5">
                {c.status === 'PASS' ? (
                  <CheckCircle2 className="mt-0.5 h-4 w-4 text-[#176C5B]" />
                ) : (
                  <XCircle className="mt-0.5 h-4 w-4 text-[#BB5656]" />
                )}
                <div>
                  <div className="font-semibold text-[#17242D]">{c.check_name}</div>
                  <div className="text-[#65727A]">{c.detail}</div>
                </div>
              </div>
              <div className="font-mono text-xs">
                Violations: <strong>{c.observed_value}</strong>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Table Record Counts */}
      <section className="rounded-lg border border-[#E6E9E6] bg-white p-5">
        <h2 className="text-base font-semibold text-[#17242D]">PostgreSQL Table Volumes</h2>
        <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5 tabular-nums">
          {Object.entries(data.table_counts).map(([tbl, cnt]: [string, any]) => (
            <div key={tbl} className="rounded border border-[#E6E9E6] bg-[#F7F8F6] p-3">
              <div className="font-mono text-[11px] text-[#65727A]">{tbl}</div>
              <div className="mt-1 text-lg font-semibold text-[#17242D]">{Number(cnt).toLocaleString()}</div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
