import React from 'react';
import { Compass, BookOpen, Layers, Sparkles, Database, History } from 'lucide-react';

export default function Navbar({ onNewAnalysis, onOpenHistory, onOpenUpload, activeView }) {
  return (
    <header className="sticky top-0 z-50 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div 
          onClick={onNewAnalysis}
          className="flex items-center gap-3 cursor-pointer group"
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-violet-600 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-500/20 group-hover:scale-105 transition-transform">
            <Compass className="w-5 h-5 text-white animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-100 to-slate-400">
                Research Scope
              </span>
              <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                AI Platform
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">Automated Literature Harvesting & Analysis Pipeline</p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2 sm:gap-3">
          <button
            onClick={onOpenUpload}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-300 hover:text-white bg-slate-900 border border-slate-800 hover:border-slate-700 transition"
            title="Upload research papers or dataset"
          >
            <Database className="w-4 h-4 text-cyan-400" />
            <span className="hidden sm:inline">Upload Data</span>
          </button>

          <button
            onClick={onOpenHistory}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-300 hover:text-white bg-slate-900 border border-slate-800 hover:border-slate-700 transition"
            title="View previous analyses"
          >
            <History className="w-4 h-4 text-purple-400" />
            <span className="hidden sm:inline">History</span>
          </button>

          <button
            onClick={onNewAnalysis}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-medium text-white bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 shadow-md shadow-indigo-500/20 transition"
          >
            <Sparkles className="w-4 h-4" />
            <span>New Analysis</span>
          </button>
        </div>
      </div>
    </header>
  );
}
