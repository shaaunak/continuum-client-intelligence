import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import {
  Columns3,
  List,
  ArrowRight,
  TrendingUp,
  SlidersHorizontal,
  FileCheck2,
  AlertCircle,
  CheckCircle2,
} from 'lucide-react';
import { apiGet, apiPatch } from '@/services/api';

export function ImprovementRoadmapPage() {
  const [viewMode, setViewMode] = useState<'list' | 'kanban'>('list');
  const [selectedRec, setSelectedRec] = useState<any>(null);
  const queryClient = useQueryClient();

  const { data: recs, isLoading } = useQuery<any[]>({
    queryKey: ['recommendations'],
    queryFn: () => apiGet('/recommendations'),
  });

  const updateStatus = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      apiPatch(`/recommendations/${id}`, { status }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['recommendations'] }),
  });

  const statuses = ['Proposed', 'In Pilot Design', 'Approved', 'Completed'];

  return (
    <div className="flex flex-col gap-8">
      {/* Header */}
      <div className="flex flex-wrap items-end justify-between gap-4 border-b border-[#bec9c7]/30 pb-4">
        <div>
          <div className="flex items-center gap-2 text-[10px] font-bold tracking-wider uppercase text-[#6f7978]">
            <span className="w-2 h-2 rounded-full bg-[#11615f]"></span>
            <span>Strategic Execution &amp; Pilot Prioritization</span>
          </div>
          <h1 className="font-headline text-3xl font-semibold text-[#1c1b1a] mt-1">
            Improvement Roadmap
          </h1>
          <p className="text-xs text-[#3f4948] mt-1">
            Evidence-backed operational initiatives prioritized by RICE scoring framework.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/simulator"
            className="inline-flex items-center gap-1.5 rounded border border-[#bec9c7]/60 bg-white px-3 py-1.5 text-xs font-semibold text-[#11615f] hover:bg-[#f7f3ef] transition-colors"
          >
            <SlidersHorizontal className="h-3.5 w-3.5" />
            <span>Launch Impact Simulator</span>
          </Link>

          <div className="flex items-center gap-1 rounded border border-[#bec9c7]/50 bg-white p-0.5 text-xs">
            <button
              onClick={() => setViewMode('list')}
              className={`inline-flex items-center gap-1.5 rounded px-2.5 py-1 text-[11px] font-semibold transition-colors ${
                viewMode === 'list' ? 'bg-[#11615f] text-white' : 'text-[#3f4948] hover:text-[#1c1b1a]'
              }`}
            >
              <List className="h-3.5 w-3.5" /> List
            </button>
            <button
              onClick={() => setViewMode('kanban')}
              className={`inline-flex items-center gap-1.5 rounded px-2.5 py-1 text-[11px] font-semibold transition-colors ${
                viewMode === 'kanban' ? 'bg-[#11615f] text-white' : 'text-[#3f4948] hover:text-[#1c1b1a]'
              }`}
            >
              <Columns3 className="h-3.5 w-3.5" /> Kanban
            </button>
          </div>
        </div>
      </div>

      {/* RICE Prioritization Explanatory Note */}
      <div className="rounded border border-[#bec9c7]/40 bg-[#f7f3ef] px-5 py-3.5 text-xs text-[#3f4948] flex items-center justify-between">
        <div>
          <strong className="text-[#1c1b1a]">RICE Scoring Formulation:</strong>{' '}
          <span className="font-mono text-[#11615f] font-semibold">
            (Reach × Impact × Confidence) / Effort
          </span>
          . Reach = quarterly affected clients; Impact = 0.5–3.0 multiplier; Confidence = 0.0–1.0; Effort = person-months.
        </div>
        <span className="text-[10px] font-bold uppercase tracking-wider text-[#864e59] bg-[#ffd9de]/50 px-2 py-0.5 rounded">
          All Pilots Marked Proposed
        </span>
      </div>

      {/* Main List / Kanban View */}
      {isLoading ? (
        <div className="h-64 rounded bg-white border border-[#bec9c7]/40 animate-pulse" />
      ) : viewMode === 'list' ? (
        <div className="grid gap-6 lg:grid-cols-2">
          {recs?.map((r) => (
            <div
              key={r.recommendation_id}
              onClick={() => setSelectedRec(r)}
              className="cursor-pointer rounded border border-[#bec9c7]/40 bg-white p-6 transition-all hover:border-[#11615f] architectural-shadow flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <span className="font-mono text-[11px] font-bold text-[#11615f]">
                      {r.recommendation_id} · Priority {r.priority}
                    </span>
                    <h3 className="font-headline text-lg font-semibold text-[#1c1b1a] mt-1">
                      {r.title}
                    </h3>
                    <div className="text-xs text-[#6f7978] mt-0.5">{r.target_process}</div>
                  </div>
                  <div className="text-right tabular-nums">
                    <div className="rounded bg-[#a9efec]/40 text-[#00201f] px-2.5 py-1 text-xs font-bold font-mono">
                      RICE {r.rice_score}
                    </div>
                    <div className="mt-1 text-[10px] font-bold uppercase tracking-wider text-[#864e59]">
                      {r.status}
                    </div>
                  </div>
                </div>

                <p className="mt-3 text-xs leading-relaxed text-[#3f4948]">
                  <strong className="text-[#1c1b1a]">Hypothesis:</strong> {r.hypothesis}
                </p>
              </div>

              <div className="mt-4 pt-3 border-t border-[#ece7e4] grid grid-cols-2 gap-2 text-[11px] text-[#6f7978]">
                <div>
                  <strong className="text-[#1c1b1a]">Success Metric:</strong> {r.success_metric}
                </div>
                <div>
                  <strong className="text-[#1c1b1a]">Owner:</strong> {r.stakeholder_owner}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        /* Kanban View */
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {statuses.map((status) => {
            const items = (recs || []).filter((r) => r.status === status);
            return (
              <div
                key={status}
                className="bg-[#f7f3ef] rounded border border-[#bec9c7]/40 p-4 flex flex-col gap-3 min-h-[400px]"
              >
                <div className="flex items-center justify-between pb-2 border-b border-[#bec9c7]/30">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-[#1c1b1a]">
                    {status}
                  </span>
                  <span className="text-xs font-semibold text-[#6f7978] tabular-nums">
                    {items.length}
                  </span>
                </div>
                <div className="space-y-3">
                  {items.map((r) => (
                    <div
                      key={r.recommendation_id}
                      onClick={() => setSelectedRec(r)}
                      className="bg-white p-3.5 rounded border border-[#bec9c7]/40 shadow-sm cursor-pointer hover:border-[#11615f] transition-colors"
                    >
                      <div className="flex items-center justify-between text-[10px] text-[#11615f] font-mono font-bold">
                        <span>{r.recommendation_id}</span>
                        <span>RICE {r.rice_score}</span>
                      </div>
                      <h4 className="font-headline text-sm font-semibold text-[#1c1b1a] mt-1 leading-snug">
                        {r.title}
                      </h4>
                      <p className="text-[11px] text-[#6f7978] mt-1 line-clamp-2">{r.hypothesis}</p>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Selected Recommendation Detail Drawer / Modal */}
      {selectedRec && (
        <div
          className="fixed inset-0 z-50 bg-[#1c1b1a]/40 flex items-center justify-center p-4 backdrop-blur-xs"
          onClick={() => setSelectedRec(null)}
        >
          <div
            className="bg-white rounded border border-[#bec9c7]/60 max-w-2xl w-full p-6 architectural-shadow space-y-4"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between">
              <div>
                <span className="text-[10px] font-mono font-bold text-[#11615f]">
                  {selectedRec.recommendation_id} · Priority {selectedRec.priority}
                </span>
                <h2 className="font-headline text-2xl font-semibold text-[#1c1b1a] mt-0.5">
                  {selectedRec.title}
                </h2>
                <div className="text-xs text-[#6f7978]">{selectedRec.target_process}</div>
              </div>
              <button
                onClick={() => setSelectedRec(null)}
                className="text-xs text-[#6f7978] hover:text-[#1c1b1a] px-2 py-1 rounded border border-[#bec9c7]/40"
              >
                Close
              </button>
            </div>

            <div className="space-y-3 text-xs leading-relaxed text-[#3f4948]">
              <div>
                <strong className="text-[#1c1b1a]">Hypothesis:</strong> {selectedRec.hypothesis}
              </div>
              <div>
                <strong className="text-[#1c1b1a]">Proposed Experiment:</strong>{' '}
                {selectedRec.proposed_experiment}
              </div>
              <div>
                <strong className="text-[#1c1b1a]">Target Metric:</strong> {selectedRec.success_metric}
              </div>
            </div>

            <div className="pt-4 border-t border-[#ece7e4] flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-xs text-[#6f7978]">Status:</span>
                <select
                  value={selectedRec.status}
                  onChange={(e) =>
                    updateStatus.mutate({
                      id: selectedRec.recommendation_id,
                      status: e.target.value,
                    })
                  }
                  className="rounded border border-[#bec9c7]/50 bg-white px-2 py-1 text-xs font-semibold text-[#1c1b1a] outline-none"
                >
                  {statuses.map((st) => (
                    <option key={st} value={st}>
                      {st}
                    </option>
                  ))}
                </select>
              </div>

              <Link
                to="/simulator"
                className="inline-flex items-center gap-1.5 rounded bg-[#11615f] text-white px-4 py-2 text-xs font-bold tracking-wider uppercase hover:bg-[#337a78] transition-colors"
              >
                <span>Simulate ROI in Studio</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
