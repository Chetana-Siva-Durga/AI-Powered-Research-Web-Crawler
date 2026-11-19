import React from 'react';
import { Sparkles, CheckCircle, Lightbulb, Compass, FileText } from 'lucide-react';

export default function ExplanationView({ explanation }) {
  if (!explanation) return null;

  return (
    <div className="glass-card rounded-2xl p-6 shadow-xl mb-8">
      {/* Header */}
      <div className="pb-5 border-b border-slate-800">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-indigo-400" />
          Explainable Findings & Intelligence Synthesis
        </h2>
        <p className="text-xs text-slate-400 mt-0.5">
          Natural-language synthesis connecting empirical data, similarity metrics, trends, and gap discovery.
        </p>
      </div>

      {/* Executive Summary Callout */}
      <div className="mt-5 p-4 rounded-xl bg-gradient-to-r from-indigo-950/40 via-purple-950/20 to-slate-900/40 border border-indigo-500/30">
        <h3 className="text-xs font-bold text-indigo-300 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
          <FileText className="w-3.5 h-3.5 text-indigo-400" />
          Executive Synthesis:
        </h3>
        <p className="text-xs sm:text-sm text-slate-200 leading-relaxed">
          {explanation.executive_summary}
        </p>
      </div>

      {/* Deep-Dive Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
        {/* Similarity */}
        <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
          <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-wider mb-2">
            Literature Alignment
          </h4>
          <p className="text-xs text-slate-300 leading-relaxed">
            {explanation.similarity_insights}
          </p>
        </div>

        {/* Trends */}
        <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
          <h4 className="text-xs font-bold text-cyan-400 uppercase tracking-wider mb-2">
            Trend & Velocity
          </h4>
          <p className="text-xs text-slate-300 leading-relaxed">
            {explanation.trend_insights}
          </p>
        </div>

        {/* Gaps */}
        <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
          <h4 className="text-xs font-bold text-amber-400 uppercase tracking-wider mb-2">
            Strategic Niche
          </h4>
          <p className="text-xs text-slate-300 leading-relaxed">
            {explanation.gap_insights}
          </p>
        </div>
      </div>

      {/* Actionable Recommendations */}
      {explanation.actionable_recommendations && explanation.actionable_recommendations.length > 0 && (
        <div className="mt-5 p-4 rounded-xl bg-slate-900/50 border border-slate-800">
          <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
            <Compass className="w-3.5 h-3.5" />
            Recommended Next Steps for the Researcher:
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {explanation.actionable_recommendations.map((rec, idx) => (
              <div key={idx} className="flex items-start gap-2 text-xs text-slate-300">
                <CheckCircle className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                <span>{rec}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
