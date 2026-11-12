import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { apiGet } from '@/services/api';

export function RequirementsHubPage() {
  const { data, isLoading } = useQuery<any>({
    queryKey: ['requirements-hub'],
    queryFn: () => apiGet('/requirements'),
  });

  if (isLoading || !data) {
    return <div className="h-64 animate-pulse rounded-lg bg-white" />;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-[#17242D]">Requirements Hub</h1>
        <p className="mt-1 text-sm text-[#65727A]">
          Business Requirements Document (BRD), Stakeholder RACI Matrix, MoSCoW User Stories, UAT Edge Cases, and End-to-End Traceability.
        </p>
      </div>

      {/* BRD Summary */}
      <section className="rounded-lg border border-[#E6E9E6] bg-white p-5">
        <div className="text-xs font-semibold uppercase tracking-wider text-[#176C5B]">
          Business Requirements Document (Summary)
        </div>
        <h2 className="mt-1 text-base font-semibold text-[#17242D]">{data.brd_summary.project_name}</h2>
        <p className="mt-2 text-xs leading-relaxed text-[#17242D]">{data.brd_summary.problem_statement}</p>
        <div className="mt-4 grid gap-4 md:grid-cols-2 text-xs">
          <div>
            <div className="font-semibold text-[#17242D]">Core Objectives</div>
            <ul className="mt-1.5 list-disc space-y-1 pl-4 text-[#65727A]">
              {data.brd_summary.objectives.map((o: string, i: number) => (
                <li key={i}>{o}</li>
              ))}
            </ul>
          </div>
          <div>
            <div className="font-semibold text-[#17242D]">In-Scope Capabilities</div>
            <ul className="mt-1.5 list-disc space-y-1 pl-4 text-[#65727A]">
              {data.brd_summary.scope_in.map((s: string, i: number) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      {/* RACI Matrix */}
      <section className="rounded-lg border border-[#E6E9E6] bg-white p-5">
        <h2 className="text-base font-semibold text-[#17242D]">Stakeholder RACI Matrix</h2>
        <div className="mt-3 overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-[#E6E9E6] text-[11px] text-[#65727A]">
                <th className="py-2 pr-3">Workflow</th>
                <th className="px-2 py-2">Responsible (R)</th>
                <th className="px-2 py-2">Accountable (A)</th>
                <th className="px-2 py-2">Consulted (C)</th>
                <th className="pl-2 py-2">Informed (I)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E6E9E6]/60">
              {data.raci_matrix.map((r: any, idx: number) => (
                <tr key={idx}>
                  <td className="py-2.5 pr-3 font-medium text-[#17242D]">{r.workflow}</td>
                  <td className="px-2 py-2.5">{r.R}</td>
                  <td className="px-2 py-2.5 font-medium text-[#20364A]">{r.A}</td>
                  <td className="px-2 py-2.5 text-[#65727A]">{r.C}</td>
                  <td className="pl-2 py-2.5 text-[#65727A]">{r.I}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* User Stories & Traceability */}
      <div className="grid gap-6 lg:grid-cols-12">
        <section className="rounded-lg border border-[#E6E9E6] bg-white p-5 lg:col-span-7">
          <h2 className="text-base font-semibold text-[#17242D]">Jira-Style Backlog (MoSCoW)</h2>
          <div className="mt-3 space-y-3">
            {data.user_stories.map((us: any) => (
              <div key={us.id} className="rounded border border-[#E6E9E6] p-3.5 text-xs">
                <div className="flex items-center justify-between">
                  <span className="font-mono font-semibold text-[#176C5B]">
                    {us.id} · {us.priority}
                  </span>
                  <Link to={us.screen} className="text-[11px] font-medium text-[#20364A] hover:underline">
                    Open Screen →
                  </Link>
                </div>
                <div className="mt-1 font-semibold text-[#17242D]">{us.title}</div>
                <p className="mt-1 text-[#65727A]">{us.acceptance_criteria}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="space-y-5 lg:col-span-5">
          <div className="rounded-lg border border-[#E6E9E6] bg-white p-5">
            <h2 className="text-base font-semibold text-[#17242D]">UAT Edge-Case Scenarios</h2>
            <div className="mt-3 space-y-2 text-xs">
              {data.uat_scenarios.map((u: any) => (
                <div key={u.id} className="rounded bg-[#F7F8F6] p-2.5">
                  <div className="font-mono font-semibold text-[#20364A]">
                    {u.id} — {u.scenario}
                  </div>
                  <div className="mt-0.5 text-[#65727A]">{u.expected}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-lg border border-[#E6E9E6] bg-white p-5">
            <h2 className="text-base font-semibold text-[#17242D]">Requirement Traceability</h2>
            <div className="mt-3 space-y-2 text-[11px]">
              {data.traceability_matrix.map((t: any, i: number) => (
                <div key={i} className="rounded border border-[#E6E9E6] px-3 py-2 font-mono">
                  {t.objective} → {t.requirement} → {t.story} → <span className="text-[#176C5B]">{t.api}</span>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
