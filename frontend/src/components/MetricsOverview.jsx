import React from 'react';
import { Target, Layers, TrendingUp, Lightbulb, CheckCircle2, Globe2 } from 'lucide-react';

export default function MetricsOverview({ data }) {
  const topSim = data.similar_papers?.[0]?.similarity_score || 0;
  const compScore = data.evaluation?.composite_score || 0;
  const rawCount = data.total_papers_collected || 0;
  const dedupCount = data.deduplicated_papers_count || 0;
  const gapsCount = data.gaps?.length || 0;
  const cagr = data.trends?.cagr_growth_rate || 0;

  return (
    <div className="grid grid-cols-2 lg:grid-cols-5 gap-3 sm:gap-4 mb-6">
      {/* 1. Overall Viability */}
      <div className="glass-card rounded-2xl p-4 sm:p-5 relative overflow-hidden">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider">Viability Score</span>
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-2xl sm:text-3xl font-extrabold text-white">{compScore}</span>
          <span className="text-xs text-slate-400">/ 100</span>
        </div>
        <p className="text-[11px] text-emerald-400 mt-1 font-medium">Multi-dimensional evaluation</p>
      </div>

      {/* 2. Top Similarity Match */}
      <div className="glass-card rounded-2xl p-4 sm:p-5 relative overflow-hidden">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider">Top Proximity</span>
          <Target className="w-4 h-4 text-indigo-400" />
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-2xl sm:text-3xl font-extrabold text-white">{topSim}%</span>
          <span className="text-xs text-slate-400">Cosine Match</span>
        </div>
        <p className="text-[11px] text-indigo-300 mt-1 font-medium">Highest literature match</p>
      </div>

      {/* 3. Harvested & Deduplicated */}
      <div className="glass-card rounded-2xl p-4 sm:p-5 relative overflow-hidden">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider">Unique Papers</span>
          <Layers className="w-4 h-4 text-violet-400" />
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-2xl sm:text-3xl font-extrabold text-white">{dedupCount}</span>
          <span className="text-xs text-slate-400">from {rawCount} raw</span>
        </div>
        <p className="text-[11px] text-violet-300 mt-1 font-medium">{rawCount - dedupCount} duplicates purged</p>
      </div>

      {/* 4. Research Gaps */}
      <div className="glass-card rounded-2xl p-4 sm:p-5 relative overflow-hidden">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider">Potential Gaps</span>
          <Lightbulb className="w-4 h-4 text-amber-400" />
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-2xl sm:text-3xl font-extrabold text-white">{gapsCount}</span>
          <span className="text-xs text-slate-400">Identified</span>
        </div>
        <p className="text-[11px] text-amber-300 mt-1 font-medium">Underexplored combinations</p>
      </div>

      {/* 5. Trajectory CAGR */}
      <div className="glass-card rounded-2xl p-4 sm:p-5 relative overflow-hidden col-span-2 lg:col-span-1">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider">Trend CAGR</span>
          <TrendingUp className="w-4 h-4 text-cyan-400" />
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-2xl sm:text-3xl font-extrabold text-white">+{cagr}%</span>
          <span className="text-xs text-slate-400">annual velocity</span>
        </div>
        <p className="text-[11px] text-cyan-300 mt-1 font-medium">Accelerating trajectory</p>
      </div>
    </div>
  );
}
