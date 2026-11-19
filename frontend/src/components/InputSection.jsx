import React, { useState } from 'react';
import { 
  Sparkles, Search, Layers, X, Plus, Globe, 
  Cpu, FileText, UploadCloud, ShieldCheck, CheckSquare, Square
} from 'lucide-react';

const PRESET_IDEAS = [
  {
    title: "Transformer Brain Tumor Detection",
    idea: "Using Transformer models for early detection of brain tumors from MRI images",
    domain: "Healthcare AI & Medical Imaging",
    keywords: ["MRI", "Transformer", "Brain Tumor", "Early Detection"]
  },
  {
    title: "IoT Zero Trust Architecture",
    idea: "Zero trust architecture and anomaly detection for resource-constrained IoT edge networks",
    domain: "Cybersecurity & Privacy",
    keywords: ["Zero Trust", "IoT", "Anomaly Detection", "Edge Computing"]
  },
  {
    title: "Quantum ML Drug Discovery",
    idea: "Quantum machine learning algorithms for molecular docking and accelerated drug discovery",
    domain: "Quantum Computing",
    keywords: ["Quantum Machine Learning", "Drug Discovery", "Molecular Docking"]
  },
  {
    title: "Privacy-Preserving EHR",
    idea: "Federated learning with differential privacy for cross-institutional electronic health records",
    domain: "Healthcare AI & Medical Imaging",
    keywords: ["Federated Learning", "Differential Privacy", "EHR", "Healthcare"]
  }
];

const DOMAINS = [
  "Auto-detect",
  "Healthcare AI & Medical Imaging",
  "Computer Vision",
  "Natural Language Processing",
  "Cybersecurity & Privacy",
  "IoT & Edge Computing",
  "Cloud & Distributed Systems",
  "Quantum Computing",
  "Deep Learning & Machine Learning",
  "General Computer Science"
];

const ALL_SOURCES = [
  { id: "openalex", name: "OpenAlex API", badge: "Global Works & Citations" },
  { id: "semanticscholar", name: "Semantic Scholar", badge: "Citation Graph" },
  { id: "crossref", name: "Crossref API", badge: "Peer-Reviewed DOIs" },
  { id: "arxiv", name: "arXiv API", badge: "Preprints & AI/CS" },
  { id: "pubmed", name: "PubMed E-utilities", badge: "Biomedical & Clinical" },
  { id: "crawler", name: "Web Crawler (Scrapy/BS4)", badge: "Mandatory Web Harvester" },
];

export default function InputSection({ onAnalyze, loading, onOpenUpload }) {
  const [idea, setIdea] = useState("Using Transformer models for early detection of brain tumors from MRI images");
  const [domain, setDomain] = useState("Healthcare AI & Medical Imaging");
  const [keywords, setKeywords] = useState(["MRI", "Transformer", "Brain Tumor", "Early Detection"]);
  const [newKeyword, setNewKeyword] = useState("");
  const [sources, setSources] = useState(["openalex", "semanticscholar", "crossref", "arxiv", "pubmed", "crawler"]);

  const handleAddKeyword = () => {
    const trimmed = newKeyword.trim();
    if (trimmed && !keywords.includes(trimmed)) {
      setKeywords([...keywords, trimmed]);
      setNewKeyword("");
    }
  };

  const handleRemoveKeyword = (kw) => {
    setKeywords(keywords.filter(k => k !== kw));
  };

  const toggleSource = (sourceId) => {
    if (sources.includes(sourceId)) {
      if (sources.length > 1) {
        setSources(sources.filter(s => s !== sourceId));
      }
    } else {
      setSources([...sources, sourceId]);
    }
  };

  const applyPreset = (preset) => {
    setIdea(preset.idea);
    setDomain(preset.domain);
    setKeywords(preset.keywords);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!idea.trim()) return;
    onAnalyze({
      idea: idea.trim(),
      domain: domain === "Auto-detect" ? "" : domain,
      keywords,
      sources,
      max_papers: 50,
    });
  };

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6">
      {/* Hero Header */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold mb-4">
          <Sparkles className="w-3.5 h-3.5" />
          Autonomous Scholarly Literature Harvesting & Intelligence
        </div>
        <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-white mb-3">
          Evaluate & Discover <br className="hidden sm:block" />
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-violet-400 to-purple-400">
            Unexplored Research Frontiers
          </span>
        </h1>
        <p className="text-slate-400 text-sm sm:text-base max-w-2xl mx-auto">
          Enter your research hypothesis. Research Scope concurrently harvests scholarly APIs and web crawls preprint indices, performs semantic deduplication, discovers research gaps, and predicts multi-dimensional impact.
        </p>
      </div>

      {/* Preset Pills */}
      <div className="mb-6">
        <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
          <span>Explore sample research hypotheses:</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {PRESET_IDEAS.map((preset, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => applyPreset(preset)}
              className="text-xs px-3 py-1.5 rounded-lg bg-slate-900/90 hover:bg-slate-800 border border-slate-800 hover:border-indigo-500/40 text-slate-300 hover:text-white transition flex items-center gap-1.5"
            >
              <Cpu className="w-3.5 h-3.5 text-indigo-400" />
              {preset.title}
            </button>
          ))}
        </div>
      </div>

      {/* Main Form Card */}
      <form onSubmit={handleSubmit} className="glass-card rounded-2xl p-6 sm:p-8 shadow-2xl space-y-6">
        {/* Research Idea Textarea */}
        <div>
          <label className="block text-sm font-semibold text-slate-200 mb-2 flex items-center justify-between">
            <span>Research Idea / Hypothesis:</span>
            <span className="text-xs font-normal text-slate-400">Natural language concept description</span>
          </label>
          <textarea
            value={idea}
            onChange={(e) => setIdea(e.target.value)}
            rows={3}
            className="w-full bg-slate-900/90 border border-slate-700/80 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition text-sm leading-relaxed"
            placeholder="e.g., Using Transformer models for early detection of brain tumors from MRI images..."
            required
          />
        </div>

        {/* Domain & Keywords Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Domain Dropdown */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Research Domain:
            </label>
            <select
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              className="w-full bg-slate-900/90 border border-slate-700/80 rounded-xl px-3.5 py-2.5 text-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition"
            >
              {DOMAINS.map((d) => (
                <option key={d} value={d} className="bg-slate-900 text-slate-200">
                  {d}
                </option>
              ))}
            </select>
          </div>

          {/* Keywords Input */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Add Key Concepts / Keywords:
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={newKeyword}
                onChange={(e) => setNewKeyword(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleAddKeyword();
                  }
                }}
                placeholder="Type and press Enter..."
                className="flex-1 bg-slate-900/90 border border-slate-700/80 rounded-xl px-3.5 py-2 text-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition"
              />
              <button
                type="button"
                onClick={handleAddKeyword}
                className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-medium border border-slate-700 transition"
              >
                <Plus className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Active Keyword Chips */}
        {keywords.length > 0 && (
          <div className="flex flex-wrap gap-2 pt-1">
            {keywords.map((kw, i) => (
              <span
                key={i}
                className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-medium"
              >
                {kw}
                <button
                  type="button"
                  onClick={() => handleRemoveKeyword(kw)}
                  className="text-indigo-400 hover:text-white"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
          </div>
        )}

        {/* Data Source Toggles */}
        <div className="pt-2 border-t border-slate-800">
          <label className="block text-xs font-semibold text-slate-300 mb-2.5 flex items-center justify-between">
            <span className="flex items-center gap-1.5">
              <Globe className="w-3.5 h-3.5 text-indigo-400" />
              Data Collection Sources (APIs & Mandatory Web Crawler):
            </span>
            <span className="text-[11px] font-normal text-slate-400">
              {sources.length} active collectors
            </span>
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
            {ALL_SOURCES.map((s) => {
              const active = sources.includes(s.id);
              return (
                <div
                  key={s.id}
                  onClick={() => toggleSource(s.id)}
                  className={`p-2.5 rounded-xl border cursor-pointer transition flex items-start gap-2 ${
                    active
                      ? 'bg-indigo-950/40 border-indigo-500/50 text-slate-200'
                      : 'bg-slate-900/40 border-slate-800 text-slate-500 hover:border-slate-700'
                  }`}
                >
                  <div className="mt-0.5">
                    {active ? (
                      <CheckSquare className="w-4 h-4 text-indigo-400" />
                    ) : (
                      <Square className="w-4 h-4 text-slate-600" />
                    )}
                  </div>
                  <div className="overflow-hidden">
                    <p className="text-xs font-medium truncate">{s.name}</p>
                    <p className="text-[10px] text-slate-400 truncate">{s.badge}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Action Button & Dataset Trigger */}
        <div className="pt-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <button
            type="button"
            onClick={onOpenUpload}
            className="w-full sm:w-auto text-xs text-slate-400 hover:text-slate-200 flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg hover:bg-slate-900 border border-transparent hover:border-slate-800 transition"
          >
            <UploadCloud className="w-4 h-4 text-slate-400" />
            <span>Have your own papers/dataset? Ingest CSV or PDF</span>
          </button>

          <button
            type="submit"
            disabled={loading}
            className="w-full sm:w-auto px-8 py-3.5 rounded-xl font-bold text-sm text-white bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600 hover:from-indigo-500 hover:to-purple-500 shadow-xl shadow-indigo-600/25 disabled:opacity-50 transition flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Harvesting & Analyzing...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Analyze Research</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
