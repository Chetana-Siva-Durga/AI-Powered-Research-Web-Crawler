import React from 'react';
import { Lightbulb, Compass, ArrowRight, Sparkles, CheckCircle2 } from 'lucide-react';

export default function ResearchGapsView({ gaps = [] }) {
  return (
    <div className="glass-card rounded-2xl p-6 shadow-xl mb-8">
      {/* Header */}
      <div className="pb-5 border-b border-slate-800">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Lightbulb className="w-5 h-5 text-amber-400" />
            Potential Research Gaps & Novel Niches
          </h2>
          <span className="text-xs px-2.5 py-1 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/20 font-medium">
            {gaps.length} Actionable Directions Found
          </span>
        </div>
        <p className="text-xs text-slate-400 mt-1">
          Identified via concept co-occurrence analysis and empirical literature limitations. Points researchers to high-novelty, defensible contributions.
        </p>
      </div>

      {/* Gaps Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-5">
        {gaps.length === 0 ? (
          <div className="col-span-2 py-8 text-center text-slate-500 text-sm">
            No distinct research gaps detected for this specific configuration.
          </div>
        ) : (
          gaps.map((gap, idx) => (
            <div
              key={idx}
              className="bg-slate-900/70 border border-slate-800 hover:border-amber-500/40 rounded-xl p-5 transition flex flex-col justify-between"
            >
              <div>
                {/* Top Badge Row */}
                <div className="flex items-center justify-between gap-2 mb-3">
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs font-mono font-bold text-amber-400">
                      GAP #{gap.id || idx + 1}
                    </span>
                    {gap.feasibility && (
                      <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-medium">
                        Feasibility: {gap.feasibility}
                      </span>
                    )}
                  </div>
                  <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/20 font-mono">
                    {gap.novelty_score}% Novelty
                  </span>
                </div>

                {/* Gap Title */}
                <h3 className="text-sm font-semibold text-slate-100 mb-2">
                  {gap.gap_title}
                </h3>

                {/* Concept Pair Pills */}
                {gap.concept_a && gap.concept_b && (
                  <div className="flex items-center gap-2 mb-3 text-xs">
                    <span className="px-2 py-1 rounded-md bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 font-medium">
                      {gap.concept_a}
                    </span>
                    <span className="text-slate-500 font-bold">+</span>
                    <span className="px-2 py-1 rounded-md bg-violet-500/10 text-violet-300 border border-violet-500/20 font-medium">
                      {gap.concept_b}
                    </span>
                    <span className="text-[10px] text-slate-400 ml-auto font-mono">
                      ({gap.co_occurrence_count} co-occurring papers)
                    </span>
                  </div>
                )}

                {/* Description */}
                <p className="text-xs text-slate-300 leading-relaxed mb-4">
                  {gap.description}
                </p>
              </div>

              {/* Actionable Suggested Direction */}
              {gap.suggested_direction && (
                <div className="mt-2 pt-3 border-t border-slate-800/80 bg-slate-950/40 rounded-lg p-3">
                  <div className="flex items-center gap-1.5 text-[11px] font-semibold text-emerald-400 uppercase tracking-wider mb-1">
                    <Compass className="w-3.5 h-3.5" />
                    <span>Suggested Research Direction:</span>
                  </div>
                  <p className="text-xs text-slate-300 leading-normal">
                    {gap.suggested_direction}
                  </p>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
