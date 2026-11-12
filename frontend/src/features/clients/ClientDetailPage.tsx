import { useQuery } from '@tanstack/react-query';
import { Link, useParams } from 'react-router-dom';
import { AlertTriangle, ArrowLeft, CheckCircle2 } from 'lucide-react';
import { apiGet } from '@/services/api';

export function ClientDetailPage() {
  const { clientId } = useParams<{ clientId: string }>();

  const { data, isLoading, error } = useQuery<any>({
    queryKey: ['client-journey', clientId],
    queryFn: () => apiGet(`/clients/${clientId}/journey`),
    enabled: Boolean(clientId),
  });

  if (isLoading) return <div className="text-sm text-[#65727A]">Reconstructing client journey timeline...</div>;
  if (error || !data) {
    return (
      <div className="rounded-lg border border-[#BB5656]/30 bg-white p-6 text-sm text-[#BB5656]">
        Client {clientId} not found.
      </div>
    );
  }

  const c = data.client;

  return (
    <div className="space-y-6">
      <div>
        <Link to="/clients" className="inline-flex items-center gap-1 text-xs font-medium text-[#65727A] hover:text-[#17242D]">
          <ArrowLeft className="h-3.5 w-3.5" /> Back to Client Explorer
        </Link>
        <div className="mt-2 flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="font-mono text-2xl font-semibold text-[#17242D]">CLIENT {c.client_id}</h1>
            <p className="mt-1 text-sm text-[#65727A]">
              {c.segment} · {c.asset_tier} · {c.team_name} ({c.advisor_name})
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="rounded border border-[#E6E9E6] bg-white px-3 py-1 text-xs font-medium text-[#17242D]">
              Lifecycle: {c.lifecycle_status}
            </span>
            <span
              className={`rounded px-3 py-1 text-xs font-semibold ${
                c.engagement_status === 'At Risk'
                  ? 'bg-[#BB5656]/10 text-[#BB5656]'
                  : c.engagement_status === 'Engaged'
                    ? 'bg-[#E9F3EE] text-[#176C5B]'
                    : 'bg-[#BD8438]/15 text-[#BD8438]'
              }`}
            >
              Engagement: {c.engagement_status}
            </span>
          </div>
        </div>
      </div>

      {/* Summary Strip */}
      <div className="grid grid-cols-2 gap-4 md:grid-cols-5 tabular-nums">
        <div className="rounded-lg border border-[#E6E9E6] bg-white p-3.5">
          <div className="text-[11px] text-[#65727A]">Relationship Tenure</div>
          <div className="mt-1 text-lg font-semibold">
            {c.relationship_tenure_days !== null ? `${c.relationship_tenure_days}d` : 'Onboarding'}
          </div>
        </div>
        <div className="rounded-lg border border-[#E6E9E6] bg-white p-3.5">
          <div className="text-[11px] text-[#65727A]">Early SLA Breaches (90d)</div>
          <div className={`mt-1 text-lg font-semibold ${c.early_sla_breaches >= 2 ? 'text-[#BB5656]' : ''}`}>
            {c.early_sla_breaches}
          </div>
        </div>
        <div className="rounded-lg border border-[#E6E9E6] bg-white p-3.5">
          <div className="text-[11px] text-[#65727A]">Open Requests</div>
          <div className="mt-1 text-lg font-semibold">{c.open_requests}</div>
        </div>
        <div className="rounded-lg border border-[#E6E9E6] bg-white p-3.5">
          <div className="text-[11px] text-[#65727A]">KYC Rework Cycles</div>
          <div className="mt-1 text-lg font-semibold">{c.rework_cycles}</div>
        </div>
        <div className="rounded-lg border border-[#E6E9E6] bg-white p-3.5">
          <div className="text-[11px] text-[#65727A]">Days Since Contact</div>
          <div className="mt-1 text-lg font-semibold">
            {c.days_since_last_contact !== null ? `${c.days_since_last_contact}d` : '—'}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        {/* Central Reconstructed Event Timeline */}
        <section className="rounded-lg border border-[#E6E9E6] bg-white p-5 lg:col-span-7">
          <h2 className="text-base font-semibold text-[#17242D]">Reconstructed Journey Timeline</h2>
          <p className="text-xs text-[#65727A]">
            Chronological lifecycle events, onboarding rework loops, and service cases.
          </p>

          <div className="mt-5 space-y-4 border-l-2 border-[#E6E9E6] pl-4">
            {data.timeline.map((ev: any) => (
              <div key={ev.id} className="relative">
                <span
                  className={`absolute -left-[23px] top-1 flex h-3.5 w-3.5 items-center justify-center rounded-full border-2 border-white ${
                    ev.severity === 'risk'
                      ? 'bg-[#BB5656]'
                      : ev.severity === 'warning'
                        ? 'bg-[#BD8438]'
                        : 'bg-[#176C5B]'
                  }`}
                />
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="text-xs font-semibold text-[#17242D]">{ev.title}</span>
                  <span className="font-mono text-[11px] text-[#65727A]">
                    {ev.timestamp.slice(0, 16).replace('T', ' ')}
                  </span>
                </div>
                <p className="mt-0.5 text-xs text-[#65727A]">{ev.summary}</p>
                <div className="mt-0.5 text-[10px] text-[#65727A]">Actor: {ev.actor}</div>
              </div>
            ))}
          </div>
        </section>

        {/* Transparent At-Risk & Stage Episodes */}
        <section className="space-y-5 lg:col-span-5">
          <div className="rounded-lg border border-[#E6E9E6] bg-white p-5">
            <h2 className="text-base font-semibold text-[#17242D]">At-Risk Rule Assessment</h2>
            <div className="mt-1 text-xs text-[#65727A]">{data.risk_assessment.method}</div>
            {data.risk_assessment.rules_triggered.length > 0 ? (
              <ul className="mt-3 space-y-2">
                {data.risk_assessment.rules_triggered.map((rule: string, i: number) => (
                  <li
                    key={i}
                    className="flex items-start gap-2 rounded border border-[#BD8438]/30 bg-[#BD8438]/5 p-2.5 text-xs text-[#17242D]"
                  >
                    <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0 text-[#BD8438]" />
                    <span>{rule}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="mt-3 flex items-center gap-2 rounded border border-[#176C5B]/20 bg-[#E9F3EE] p-2.5 text-xs text-[#176C5B]">
                <CheckCircle2 className="h-4 w-4" /> No deterministic risk thresholds triggered.
              </div>
            )}
            <p className="mt-3 text-[11px] text-[#65727A]">{data.risk_assessment.limitation}</p>
          </div>

          <div className="rounded-lg border border-[#E6E9E6] bg-white p-5">
            <h2 className="text-base font-semibold text-[#17242D]">Stage Episodes</h2>
            <div className="mt-3 space-y-2">
              {data.stage_episodes.map((ep: any) => (
                <div key={ep.episode_id} className="flex items-center justify-between rounded border border-[#E6E9E6] px-3 py-2 text-xs">
                  <div>
                    <div className="font-medium text-[#17242D]">{ep.stage}</div>
                    <div className="font-mono text-[10px] text-[#65727A]">
                      {ep.entered_at.slice(0, 10)} → {ep.exited_at ? ep.exited_at.slice(0, 10) : 'Ongoing'}
                    </div>
                  </div>
                  <div className="text-right">
                    <span
                      className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${
                        ep.outcome === 'Reopened'
                          ? 'bg-[#BB5656]/10 text-[#BB5656]'
                          : 'bg-[#F7F8F6] text-[#17242D]'
                      }`}
                    >
                      {ep.outcome}
                    </span>
                    {ep.rework_reason && (
                      <div className="mt-0.5 text-[10px] text-[#65727A]">{ep.rework_reason}</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
