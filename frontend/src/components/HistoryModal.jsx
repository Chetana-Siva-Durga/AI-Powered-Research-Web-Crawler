import React, { useState, useEffect } from 'react';
import { X, History, ArrowRight, Clock, Trash2 } from 'lucide-react';
import api from '../api';

export default function HistoryModal({ isOpen, onClose, onSelectAnalysis }) {
  const [historyItems, setHistoryItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [deletingId, setDeletingId] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen) {
      fetchHistory();
    }
  }, [isOpen]);

  const fetchHistory = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await api.get('/api/history');
      setHistoryItems(res.data);
    } catch (err) {
      console.error('Failed to fetch history:', err);
      setError(err.response?.data?.detail || 'Could not load analysis history.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAnalysis = async (event, item) => {
    event.stopPropagation();
    if (!window.confirm('Delete this saved analysis? This cannot be undone.')) return;

    setDeletingId(item.analysis_id);
    setError('');
    try {
      await api.delete(`/api/history/${item.analysis_id}`);
      setHistoryItems((items) => items.filter((historyItem) => historyItem.analysis_id !== item.analysis_id));
    } catch (err) {
      console.error('Failed to delete analysis:', err);
      setError(err.response?.data?.detail || 'Could not delete this analysis. Please try again.');
    } finally {
      setDeletingId(null);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <div className="glass-card rounded-2xl p-6 max-w-2xl w-full shadow-2xl relative max-h-[85vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <History className="w-5 h-5 text-purple-400" />
            <h3 className="text-base font-bold text-white">Previous Research Analyses</h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white p-1 rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* List Content */}
        <div className="flex-1 overflow-y-auto py-4 divide-y divide-slate-800/60">
          {error && (
            <p role="alert" className="mb-3 rounded-lg border border-rose-500/30 bg-rose-500/10 px-3 py-2 text-xs text-rose-300">
              {error}
            </p>
          )}
          {loading ? (
            <div className="py-12 text-center text-slate-400 text-xs flex items-center justify-center gap-2">
              <div className="w-4 h-4 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin" />
              <span>Loading historical runs...</span>
            </div>
          ) : historyItems.length === 0 ? (
            <div className="py-12 text-center text-slate-500 text-xs">
              No saved analyses yet. Submit a research hypothesis to save your first run!
            </div>
          ) : (
            historyItems.map((item) => (
              <div
                key={item.analysis_id}
                onClick={() => {
                  onSelectAnalysis(item.analysis_id);
                  onClose();
                }}
                className="py-3 px-3 hover:bg-slate-900/60 rounded-xl transition cursor-pointer flex items-center justify-between gap-4 group"
              >
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                      {item.domain}
                    </span>
                    <span className="text-[11px] text-slate-500 flex items-center gap-1 font-mono">
                      <Clock className="w-3 h-3" />
                      {new Date(item.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <p className="text-xs font-semibold text-slate-200 group-hover:text-indigo-400 transition truncate">
                    "{item.idea}"
                  </p>
                  <p className="text-[11px] text-slate-400 mt-0.5">
                    {item.deduplicated_papers} unique papers • Viability: <span className="text-emerald-400 font-bold">{item.composite_score}/100</span>
                  </p>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <button
                    type="button"
                    onClick={(event) => handleDeleteAnalysis(event, item)}
                    disabled={deletingId === item.analysis_id}
                    aria-label={`Delete analysis: ${item.idea}`}
                    title="Delete analysis"
                    className="rounded-lg p-2 text-slate-500 hover:bg-rose-500/10 hover:text-rose-400 disabled:cursor-wait disabled:opacity-50 transition"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                  <ArrowRight className="w-4 h-4 text-slate-600 group-hover:text-indigo-400 transition" />
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
