import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Sparkles, Compass, AlertCircle, RefreshCw, Cpu, CheckCircle2 } from 'lucide-react';

import Navbar from './components/Navbar';
import InputSection from './components/InputSection';
import Dashboard from './components/Dashboard';
import UploadModal from './components/UploadModal';
import HistoryModal from './components/HistoryModal';

const PIPELINE_STEPS = [
  'Initiating Scholarly Data Harvester (OpenAlex, Crossref, arXiv, PubMed, Crawler)...',
  'Executing Focused Web Crawler across open-access preprints...',
  'Normalizing schema, fixing unicode encodings, and purging HTML tags...',
  'Executing Multi-Tier Deduplication & merging metadata records...',
  'Persisting canonical papers and idea session in Relational Database...',
  'Computing Dense Semantic Vector Embeddings and Cosine Similarity...',
  'Analyzing Temporal Publication Velocity & CAGR keyword trajectories...',
  'Mining Concept Co-Occurrence Matrix & Extracting Literature Limitations...',
  'Evaluating Multi-Dimensional Impact (Academic, Industry, Society, Future)...',
  'Synthesizing Explainable Findings & Assembling Dashboard...',
];

export default function App() {
  const [activeView, setActiveView] = useState('input');
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [currentStepIdx, setCurrentStepIdx] = useState(0);
  const [error, setError] = useState(null);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [historyModalOpen, setHistoryModalOpen] = useState(false);

  // Track AI model warm-up status (backend pre-warms SentenceTransformer at startup)
  const [modelReady, setModelReady] = useState(false);
  const [modelLoading, setModelLoading] = useState(true);

  // Poll /api/status until model_ready === true
  useEffect(() => {
    let pollInterval;
    const checkStatus = async () => {
      try {
        const res = await axios.get('/api/status', { timeout: 5000 });
        if (res.data.model_ready) {
          setModelReady(true);
          setModelLoading(false);
          clearInterval(pollInterval);
        } else {
          setModelLoading(res.data.model_loading ?? true);
        }
      } catch {
        // Backend might not be up yet; keep polling
      }
    };
    checkStatus(); // check immediately
    pollInterval = setInterval(checkStatus, 3000);
    return () => clearInterval(pollInterval);
  }, []);

  const handleAnalyze = async (payload) => {
    setLoading(true);
    setError(null);
    setCurrentStepIdx(0);

    // Simulate animated step progression while backend processes
    const stepInterval = setInterval(() => {
      setCurrentStepIdx((prev) => {
        if (prev < PIPELINE_STEPS.length - 1) return prev + 1;
        return prev;
      });
    }, 1800);

    try {
      const response = await axios.post('/api/analyze', payload, { timeout: 180000 });
      clearInterval(stepInterval);
      setAnalysisData(response.data);
      setActiveView('dashboard');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      clearInterval(stepInterval);
      console.error('Analysis error:', err);
      if (err.code === 'ECONNABORTED') {
        setError(
          'Analysis timed out (3 min). The embedding model may still be warming up. ' +
          'Wait for "AI Model Ready" status and try again.'
        );
      } else if (!err.response) {
        setError(
          'Cannot reach the backend API. Start it with run_backend.bat, then try again.'
        );
      } else {
        setError(
          err.response?.data?.detail ||
          'An error occurred while executing the research analysis pipeline. Please verify your connection or try again.'
        );
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSelectHistoryAnalysis = async (analysisId) => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(`/api/history/${analysisId}`);
      handleAnalyze({
        idea: res.data.idea,
        domain: res.data.domain,
        keywords: res.data.keywords || [],
      });
    } catch (err) {
      setError('Could not retrieve historical analysis.');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col selection:bg-indigo-500 selection:text-white">
      {/* Top Navigation */}
      <Navbar
        onNewAnalysis={() => {
          setActiveView('input');
          setError(null);
        }}
        onOpenHistory={() => setHistoryModalOpen(true)}
        onOpenUpload={() => setUploadModalOpen(true)}
        activeView={activeView}
      />

      {/* Model warm-up status banner */}
      {!modelReady && (
        <div className="max-w-4xl mx-auto w-full px-4 mt-4">
          <div className="flex items-center gap-3 px-4 py-2.5 rounded-xl bg-amber-500/10 border border-amber-500/25 text-amber-300 text-xs">
            <Cpu className="w-4 h-4 shrink-0 animate-pulse text-amber-400" />
            <span>
              {modelLoading
                ? 'AI embedding model is warming up in the background — analysis will be available shortly...'
                : 'Connecting to backend...'}
            </span>
            <RefreshCw className="w-3.5 h-3.5 ml-auto animate-spin opacity-60" />
          </div>
        </div>
      )}

      {modelReady && activeView === 'input' && (
        <div className="max-w-4xl mx-auto w-full px-4 mt-4">
          <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>AI Model Ready — Semantic embeddings online</span>
          </div>
        </div>
      )}

      {/* Main Body */}
      <main className="flex-1">
        {error && (
          <div className="max-w-4xl mx-auto px-4 mt-6">
            <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-5 h-5 shrink-0 text-rose-400" />
                <span>{error}</span>
              </div>
              <button
                onClick={() => setError(null)}
                className="text-xs px-2.5 py-1 rounded-md bg-rose-500/20 hover:bg-rose-500/30 text-rose-200 transition"
              >
                Dismiss
              </button>
            </div>
          </div>
        )}

        {/* Loading Overlay with Real-time Pipeline Progress */}
        {loading && (
          <div className="max-w-xl mx-auto my-20 px-4 text-center">
            <div className="glass-card rounded-3xl p-8 shadow-2xl border border-indigo-500/20">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-indigo-600 to-purple-600 mx-auto flex items-center justify-center shadow-xl shadow-indigo-600/30 mb-6 animate-pulse">
                <Compass className="w-8 h-8 text-white animate-spin" style={{ animationDuration: '4s' }} />
              </div>

              <h2 className="text-xl font-bold text-white mb-2">
                Analyzing Scholarly Landscape
              </h2>
              <p className="text-xs text-indigo-300 font-mono mb-6">
                Step {currentStepIdx + 1} of {PIPELINE_STEPS.length}
              </p>

              {/* Progress Bar */}
              <div className="w-full bg-slate-800 rounded-full h-2 mb-4 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-indigo-500 via-violet-500 to-purple-500 h-2 rounded-full transition-all duration-700"
                  style={{ width: `${((currentStepIdx + 1) / PIPELINE_STEPS.length) * 100}%` }}
                />
              </div>

              {/* Dynamic Step Text */}
              <p className="text-xs text-slate-300 min-h-[36px] flex items-center justify-center leading-relaxed">
                {PIPELINE_STEPS[currentStepIdx]}
              </p>
            </div>
          </div>
        )}

        {/* View Switching */}
        {!loading && activeView === 'input' && (
          <InputSection
            onAnalyze={handleAnalyze}
            loading={loading}
            onOpenUpload={() => setUploadModalOpen(true)}
          />
        )}

        {!loading && activeView === 'dashboard' && analysisData && (
          <Dashboard
            data={analysisData}
            onNewAnalysis={() => setActiveView('input')}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950/60 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <p>© {new Date().getFullYear()} Research Scope — AI-Powered Research Analysis & Gap Discovery Platform.</p>
          <div className="flex items-center gap-4 text-slate-400 text-[11px]">
            <span>OpenAlex</span>
            <span>Semantic Scholar</span>
            <span>Crossref</span>
            <span>arXiv</span>
            <span>PubMed</span>
            <span>Scrapy Crawler</span>
          </div>
        </div>
      </footer>

      {/* Modals */}
      <UploadModal
        isOpen={uploadModalOpen}
        onClose={() => setUploadModalOpen(false)}
        onUploadSuccess={(res) => {
          setUploadModalOpen(false);
          if (res.sample_titles && res.sample_titles.length > 0) {
            handleAnalyze({ idea: res.sample_titles[0] });
          }
        }}
      />

      <HistoryModal
        isOpen={historyModalOpen}
        onClose={() => setHistoryModalOpen(false)}
        onSelectAnalysis={handleSelectHistoryAnalysis}
      />
    </div>
  );
}
