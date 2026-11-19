import React from 'react';
import { Database, Filter, Layers, Globe, Server, Check } from 'lucide-react';

export default function PipelineInspector({ data }) {
  const breakdown = data.sources_breakdown || {};
  const totalRaw = data.total_papers_collected || 0;
  const uniqueCount = data.deduplicated_papers_count || 0;
  const duplicates = Math.max(0, totalRaw - uniqueCount);

  return (
    <div className="glass-card rounded-2xl p-6 shadow-xl mb-8">
      {/* Header */}
      <div className="pb-5 border-b border-slate-800">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <Database className="w-5 h-5 text-violet-400" />
          Data Collection & Processing Pipeline Inspector
        </h2>
        <p className="text-xs text-slate-400 mt-0.5">
          Auditable telemetry on multi-source ingestion, deduplication, and persistence layers.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-5">
        {/* Source Breakdown */}
        <div className="sm:col-span-2 bg-slate-900/60 border border-slate-800 rounded-xl p-4">
          <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-3 flex items-center gap-1.5">
            <Globe className="w-3.5 h-3.5 text-indigo-400" />
            Scholarly Source Distribution:
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {Object.entries(breakdown).map(([source, count]) => (
              <div key={source} className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
                <span className="text-[10px] uppercase font-mono text-slate-400 block truncate">
                  {source}
                </span>
                <div className="flex items-baseline gap-1 mt-1">
                  <span className="text-lg font-bold text-white">{count}</span>
                  <span className="text-[10px] text-slate-500">records</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Deduplication Telemetry */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-3 flex items-center gap-1.5">
              <Filter className="w-3.5 h-3.5 text-violet-400" />
              Deduplication Statistics:
            </h3>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between text-slate-400">
                <span>Total Raw Gathered:</span>
                <span className="font-mono text-white font-bold">{totalRaw}</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Canonical Deduplicated:</span>
                <span className="font-mono text-emerald-400 font-bold">{uniqueCount}</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Duplicates Purged:</span>
                <span className="font-mono text-amber-400 font-bold">{duplicates}</span>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-400 flex items-center gap-1.5">
            <Check className="w-3.5 h-3.5 text-emerald-400" />
            <span>Persistently stored in relational database.</span>
          </div>
        </div>
      </div>
    </div>
  );
}
