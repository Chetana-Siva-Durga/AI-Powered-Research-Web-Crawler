import React from 'react';
import { 
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip 
} from 'recharts';
import { Award, GraduationCap, Briefcase, HeartHandshake, Rocket, CheckCircle2 } from 'lucide-react';

export default function RelevanceRadar({ evaluation }) {
  if (!evaluation) return null;

  const acad = evaluation.academic || { score: 0, level: 'N/A', evidence: [] };
  const ind = evaluation.industry || { score: 0, level: 'N/A', evidence: [] };
  const soc = evaluation.societal || { score: 0, level: 'N/A', evidence: [] };
  const fut = evaluation.future_potential || { score: 0, level: 'N/A', evidence: [] };
  const comp = evaluation.composite_score || 0;

  const radarData = [
    { subject: 'Academic', score: acad.score, fullMark: 100 },
    { subject: 'Industry', score: ind.score, fullMark: 100 },
    { subject: 'Societal', score: soc.score, fullMark: 100 },
    { subject: 'Future Potential', score: fut.score, fullMark: 100 },
  ];

  const DIMENSIONS = [
    {
      name: 'Academic Relevance',
      score: acad.score,
      level: acad.level,
      icon: GraduationCap,
      color: 'text-indigo-400',
      bg: 'bg-indigo-500/10',
      border: 'border-indigo-500/30',
      evidence: acad.evidence,
    },
    {
      name: 'Industry Relevance',
      score: ind.score,
      level: ind.level,
      icon: Briefcase,
      color: 'text-cyan-400',
      bg: 'bg-cyan-500/10',
      border: 'border-cyan-500/30',
      evidence: ind.evidence,
    },
    {
      name: 'Societal Relevance',
      score: soc.score,
      level: soc.level,
      icon: HeartHandshake,
      color: 'text-rose-400',
      bg: 'bg-rose-500/10',
      border: 'border-rose-500/30',
      evidence: soc.evidence,
    },
    {
      name: 'Future Potential',
      score: fut.score,
      level: fut.level,
      icon: Rocket,
      color: 'text-amber-400',
      bg: 'bg-amber-500/10',
      border: 'border-amber-500/30',
      evidence: fut.evidence,
    },
  ];

  return (
    <div className="glass-card rounded-2xl p-6 shadow-xl mb-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-5 border-b border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Award className="w-5 h-5 text-indigo-400" />
            Multi-Dimensional Relevance Evaluation
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Empirical evaluation across Academic, Industry, Societal, and Future Potential dimensions with supporting signals.
          </p>
        </div>
        <div className="flex items-center gap-2 bg-indigo-500/10 border border-indigo-500/20 px-3.5 py-1.5 rounded-xl">
          <span className="text-xs text-slate-300">Composite Viability:</span>
          <span className="text-sm font-extrabold text-white font-mono">{comp}/100</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mt-6 items-center">
        {/* Radar Chart */}
        <div className="lg:col-span-5 flex flex-col items-center justify-center bg-slate-950/40 rounded-xl p-4 border border-slate-800/80">
          <div className="w-full h-64 sm:h-72">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="75%" data={radarData}>
                <PolarGrid stroke="#334155" />
                <PolarAngleAxis dataKey="subject" stroke="#94a3b8" fontSize={11} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#475569" fontSize={10} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Radar
                  name="Score"
                  dataKey="score"
                  stroke="#6366f1"
                  fill="#6366f1"
                  fillOpacity={0.35}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
          <p className="text-[11px] text-slate-400 text-center mt-2">
            Balanced quadrilateral profile indicates robust cross-sector viability.
          </p>
        </div>

        {/* Granular Dimension Cards & Evidence */}
        <div className="lg:col-span-7 grid grid-cols-1 sm:grid-cols-2 gap-3.5">
          {DIMENSIONS.map((dim, idx) => {
            const Icon = dim.icon;
            return (
              <div
                key={idx}
                className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <div className={`p-1.5 rounded-lg ${dim.bg} ${dim.color}`}>
                        <Icon className="w-4 h-4" />
                      </div>
                      <span className="text-xs font-bold text-slate-200">{dim.name}</span>
                    </div>
                    <span className="text-sm font-extrabold text-white font-mono">{dim.score}</span>
                  </div>

                  {/* Rating Progress Bar */}
                  <div className="w-full bg-slate-800 rounded-full h-1.5 mb-2.5 overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-indigo-500 to-purple-500 h-1.5 rounded-full"
                      style={{ width: `${dim.score}%` }}
                    />
                  </div>

                  {/* Evidence Items */}
                  <ul className="space-y-1.5 text-[11px] text-slate-400">
                    {dim.evidence.slice(0, 2).map((ev, ei) => (
                      <li key={ei} className="flex items-start gap-1.5">
                        <CheckCircle2 className="w-3 h-3 text-emerald-400 shrink-0 mt-0.5" />
                        <span className="leading-tight">{ev}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
