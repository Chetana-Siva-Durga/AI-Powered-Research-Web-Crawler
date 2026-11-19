import React from 'react';
import { 
  BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend 
} from 'recharts';
import { TrendingUp, Flame, CheckCircle, Calendar } from 'lucide-react';

export default function TrendCharts({ trends }) {
  const yearlyData = trends?.yearly_distribution || [];
  const trajectories = trends?.keyword_trajectories || [];
  const emerging = trends?.emerging_topics || [];
  const mature = trends?.mature_topics || [];
  const cagr = trends?.cagr_growth_rate || 0;

  // Flatten keyword trajectories into chart format: [{ year: 2021, Transformer: 5, CNN: 10, ... }]
  const years = yearlyData.map(d => d.year);
  const multiLineData = years.map(y => {
    const row = { year: y };
    trajectories.forEach(t => {
      row[t.keyword] = t.trajectory?.[y] || 0;
    });
    return row;
  });

  const LINE_COLORS = ['#6366f1', '#a855f7', '#ec4899', '#06b6d4', '#10b981', '#f59e0b'];

  return (
    <div className="glass-card rounded-2xl p-6 shadow-xl mb-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-5 border-b border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-cyan-400" />
            Research Trend & Velocity Analysis
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Temporal dynamics, keyword acceleration, and lifecycle classification.
          </p>
        </div>

        {/* Growth Rate Pill */}
        <div className="flex items-center gap-2 bg-cyan-500/10 border border-cyan-500/20 px-3 py-1.5 rounded-xl">
          <span className="text-xs text-slate-300">Annual Trajectory:</span>
          <span className="text-xs font-bold text-cyan-400 font-mono">+{cagr}% CAGR</span>
        </div>
      </div>

      {/* Emerging vs Mature Badges */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 my-5">
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-3.5">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-rose-400 mb-2">
            <Flame className="w-4 h-4" />
            <span>Emerging Research Directions:</span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {emerging.length > 0 ? (
              emerging.map((topic, i) => (
                <span
                  key={i}
                  className="text-[11px] font-medium px-2.5 py-1 rounded-md bg-rose-500/10 text-rose-300 border border-rose-500/20"
                >
                  ⚡ {topic}
                </span>
              ))
            ) : (
              <span className="text-xs text-slate-500">Steady progression</span>
            )}
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-3.5">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-300 mb-2">
            <CheckCircle className="w-4 h-4 text-emerald-400" />
            <span>Established / Mature Methodologies:</span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {mature.length > 0 ? (
              mature.map((topic, i) => (
                <span
                  key={i}
                  className="text-[11px] font-medium px-2.5 py-1 rounded-md bg-slate-800 text-slate-300 border border-slate-700"
                >
                  {topic}
                </span>
              ))
            ) : (
              <span className="text-xs text-slate-500">None detected</span>
            )}
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-4">
        {/* Chart 1: Annual Publications */}
        <div className="bg-slate-950/40 rounded-xl p-4 border border-slate-800/80">
          <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-4 flex items-center gap-1.5">
            <Calendar className="w-3.5 h-3.5 text-indigo-400" />
            Publications Velocity per Year
          </h3>
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={yearlyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="year" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} allowDecimals={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} name="Papers Published" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Keyword Trajectories */}
        <div className="bg-slate-950/40 rounded-xl p-4 border border-slate-800/80">
          <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-4 flex items-center gap-1.5">
            <TrendingUp className="w-3.5 h-3.5 text-purple-400" />
            Technology & Keyword Growth Trajectories
          </h3>
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={multiLineData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="year" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} allowDecimals={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Legend wrapperStyle={{ fontSize: '10px', paddingTop: '8px' }} />
                {trajectories.slice(0, 4).map((t, idx) => (
                  <Line
                    key={t.keyword}
                    type="monotone"
                    dataKey={t.keyword}
                    stroke={LINE_COLORS[idx % LINE_COLORS.length]}
                    strokeWidth={2}
                    dot={{ r: 3 }}
                    name={t.keyword}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
