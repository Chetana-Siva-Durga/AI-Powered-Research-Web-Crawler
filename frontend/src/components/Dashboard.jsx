import React, { useState } from 'react';
import { 
  Download, ArrowLeft, Layers, Sparkles, BookOpen, 
  TrendingUp, Lightbulb, Award, Database, Share2, Check 
} from 'lucide-react';

import api from '../api';
import MetricsOverview from './MetricsOverview';
import ExplanationView from './ExplanationView';
import RelevanceRadar from './RelevanceRadar';
import TrendCharts from './TrendCharts';
import ResearchGapsView from './ResearchGapsView';
import SimilarPapersTable from './SimilarPapersTable';
import PipelineInspector from './PipelineInspector';

export default function Dashboard({ data, onNewAnalysis }) {
  const [downloading, setDownloading] = useState(false);
  const [copied, setCopied] = useState(false);

  if (!data) return null;

  const handleExport = async (format = 'markdown') => {
    setDownloading(true);
    try {
      const response = await api.post('/api/export', {
        analysis_data: data,
        format: format,
      }, {
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `research_scope_report.${format === 'json' ? 'json' : 'md'}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Export failed:', err);
    } finally {
      setDownloading(false);
    }
  };

  const handleShare = () => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(window.location.href);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      {/* Top Navigation & Actions Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <button
          onClick={onNewAnalysis}
          className="inline-flex items-center gap-2 text-xs font-medium text-slate-400 hover:text-white transition"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Analysis Input</span>
        </button>

        <div className="flex items-center gap-2">
          <button
            onClick={handleShare}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 text-xs font-medium text-slate-300 hover:text-white transition"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Share2 className="w-3.5 h-3.5" />}
            <span>{copied ? 'Link Copied' : 'Share'}</span>
          </button>

          <button
            onClick={() => handleExport('markdown')}
            disabled={downloading}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-md shadow-indigo-600/20 transition disabled:opacity-50"
          >
            <Download className="w-3.5 h-3.5" />
            <span>{downloading ? 'Generating...' : 'Export Report (MD)'}</span>
          </button>
        </div>
      </div>

      {/* Idea Banner Card */}
      <div className="glass-card rounded-2xl p-6 sm:p-7 shadow-xl mb-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 -mr-16 -mt-16 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-wrap items-center gap-2 mb-2.5">
          <span className="text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
            {data.detected_domain || 'Computer Science'}
          </span>
          <span className="text-xs text-slate-500 font-mono">
            ID: #{data.analysis_id} • {new Date(data.created_at).toLocaleDateString()}
          </span>
        </div>

        <h1 className="text-xl sm:text-2xl font-extrabold text-white leading-snug">
          "{data.idea}"
        </h1>

        {/* Extracted Concept Badges */}
        {data.keywords && data.keywords.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-3 pt-3 border-t border-slate-800/80">
            <span className="text-xs text-slate-400 mr-1 self-center">Identified Concepts:</span>
            {data.keywords.map((kw, idx) => (
              <span
                key={idx}
                className="text-[11px] px-2.5 py-0.5 rounded-md bg-slate-800 text-slate-300 font-medium"
              >
                {kw}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* 1. Scorecard Overview */}
      <MetricsOverview data={data} />

      {/* 2. Explainable Findings Synthesis */}
      <ExplanationView explanation={data.explanation} />

      {/* 3. Multi-Dimensional Evaluation (Radar) */}
      <RelevanceRadar evaluation={data.evaluation} />

      {/* 4. Research Trends & Velocity */}
      <TrendCharts trends={data.trends} />

      {/* 5. Identified Research Gaps */}
      <ResearchGapsView gaps={data.gaps} />

      {/* 6. Ranked Similar Literature */}
      <SimilarPapersTable papers={data.similar_papers} />

      {/* 7. Data Collection Inspector */}
      <PipelineInspector data={data} />
    </div>
  );
}
