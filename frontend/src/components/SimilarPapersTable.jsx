import React, { useState } from 'react';
import { ExternalLink, ChevronDown, ChevronUp, BookOpen, Award, Filter } from 'lucide-react';

export default function SimilarPapersTable({ papers = [] }) {
  const [expandedId, setExpandedId] = useState(null);
  const [filterTier, setFilterTier] = useState('ALL');

  const filteredPapers = papers.filter(p => {
    if (filterTier === 'ALL') return true;
    return p.relevance_tier?.toUpperCase() === filterTier;
  });

  const toggleExpand = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <div className="glass-card rounded-2xl p-6 shadow-xl mb-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-5 border-b border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-indigo-400" />
            Similar Research & Prior Art
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Ranked by embedding cosine proximity. Helps answer: "Has someone already researched this?"
          </p>
        </div>

        {/* Filter Tabs */}
        <div className="flex items-center gap-1 bg-slate-900/90 p-1 rounded-xl border border-slate-800 text-xs">
          {['ALL', 'HIGH', 'MEDIUM', 'LOW'].map((tier) => (
            <button
              key={tier}
              onClick={() => setFilterTier(tier)}
              className={`px-3 py-1 rounded-lg font-medium transition ${
                filterTier === tier
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {tier}
            </button>
          ))}
        </div>
      </div>

      {/* Papers List */}
      <div className="divide-y divide-slate-800/60 mt-2">
        {filteredPapers.length === 0 ? (
          <div className="py-12 text-center text-slate-500 text-sm">
            No papers match the selected filter tier.
          </div>
        ) : (
          filteredPapers.map((paper) => {
            const isExpanded = expandedId === paper.id;
            const tierColor =
              paper.similarity_score >= 70
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                : paper.similarity_score >= 50
                ? 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20'
                : 'bg-slate-800 text-slate-400 border-slate-700';

            return (
              <div key={paper.id} className="py-4 hover:bg-slate-900/40 rounded-xl px-3 -mx-3 transition">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    {/* Top Metadata Badges */}
                    <div className="flex flex-wrap items-center gap-2 mb-1.5">
                      <span className="text-xs font-mono font-bold text-slate-400">
                        #{paper.rank}
                      </span>
                      <span className={`text-[11px] font-bold px-2 py-0.5 rounded-full border ${tierColor}`}>
                        {paper.similarity_score}% Match
                      </span>
                      {paper.publication_year && (
                        <span className="text-[11px] px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 font-medium">
                          {paper.publication_year}
                        </span>
                      )}
                      {paper.venue && (
                        <span className="text-[11px] px-2 py-0.5 rounded-md bg-slate-800/80 text-slate-400 max-w-[200px] truncate">
                          {paper.venue}
                        </span>
                      )}
                      <span className="text-[10px] px-2 py-0.5 rounded-md bg-violet-500/10 text-violet-300 border border-violet-500/20 font-mono">
                        {paper.source}
                      </span>
                      {paper.citations > 0 && (
                        <span className="text-[11px] text-amber-400 flex items-center gap-1 font-medium">
                          <Award className="w-3 h-3" />
                          {paper.citations} citations
                        </span>
                      )}
                    </div>

                    {/* Paper Title */}
                    <h3 
                      onClick={() => toggleExpand(paper.id)}
                      className="text-sm font-semibold text-slate-100 hover:text-indigo-400 cursor-pointer transition leading-snug"
                    >
                      {paper.title}
                    </h3>

                    {/* Authors */}
                    {paper.authors && paper.authors.length > 0 && (
                      <p className="text-xs text-slate-400 mt-1 truncate">
                        {paper.authors.join(', ')}
                      </p>
                    )}

                    {/* Matching Concepts */}
                    {paper.matching_concepts && paper.matching_concepts.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 mt-2">
                        {paper.matching_concepts.map((concept, ci) => (
                          <span
                            key={ci}
                            className="text-[10px] font-medium px-2 py-0.5 rounded-md bg-indigo-500/10 text-indigo-300 border border-indigo-500/20"
                          >
                            {concept}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Actions (Link & Expand) */}
                  <div className="flex items-center gap-2 pt-1">
                    {paper.url && (
                      <a
                        href={paper.url}
                        target="_blank"
                        rel="noreferrer"
                        className="p-1.5 text-slate-400 hover:text-indigo-400 hover:bg-slate-800 rounded-lg transition"
                        title="View scholarly publication"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    )}
                    <button
                      onClick={() => toggleExpand(paper.id)}
                      className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition"
                      title={isExpanded ? 'Collapse abstract' : 'Read abstract'}
                    >
                      {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                {/* Collapsible Abstract Content */}
                {isExpanded && (
                  <div className="mt-3.5 pt-3 border-t border-slate-800/80 bg-slate-950/40 rounded-xl p-4 text-xs text-slate-300 leading-relaxed space-y-2">
                    <p className="font-semibold text-slate-400 uppercase tracking-wider text-[10px]">Abstract & Synthesis:</p>
                    <p>{paper.abstract || 'No abstract text available for this publication record.'}</p>
                    {paper.doi && (
                      <p className="text-[11px] text-slate-500 font-mono pt-1">
                        DOI: <a href={`https://doi.org/${paper.doi}`} target="_blank" rel="noreferrer" className="text-indigo-400 hover:underline">{paper.doi}</a>
                      </p>
                    )}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
