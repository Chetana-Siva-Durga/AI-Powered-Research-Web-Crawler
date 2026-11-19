import React, { useState } from 'react';
import { X, UploadCloud, FileText, CheckCircle2, AlertCircle } from 'lucide-react';
import axios from 'axios';

export default function UploadModal({ isOpen, onClose, onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  if (!isOpen) return null;

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setResult(null);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setResult(response.data);
      if (onUploadSuccess) onUploadSuccess(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload and parse file.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <div className="glass-card rounded-2xl p-6 max-w-lg w-full shadow-2xl relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white p-1 rounded-lg"
        >
          <X className="w-5 h-5" />
        </button>

        <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
          <UploadCloud className="w-5 h-5 text-indigo-400" />
          Ingest Custom Research Dataset or Paper
        </h3>
        <p className="text-xs text-slate-400 mb-5">
          Upload your existing CSV, Excel (.xlsx, .xls), JSON, PDF, or TXT file. The system will parse papers and include them in subsequent analyses.
        </p>

        {/* Drag & Drop Area */}
        <div className="border-2 border-dashed border-slate-700 hover:border-indigo-500/50 rounded-xl p-6 text-center transition cursor-pointer bg-slate-900/40">
          <input
            type="file"
            id="fileInput"
            onChange={handleFileChange}
            accept=".csv,.xlsx,.xls,.json,.pdf,.txt"
            className="hidden"
          />
          <label htmlFor="fileInput" className="cursor-pointer block">
            <FileText className="w-10 h-10 text-indigo-400 mx-auto mb-2 opacity-80" />
            <p className="text-xs font-semibold text-slate-200">
              {file ? file.name : 'Click to select or drag and drop a file'}
            </p>
            <p className="text-[11px] text-slate-400 mt-1">
              Supports CSV, XLSX, JSON, PDF (max 25MB)
            </p>
          </label>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mt-4 p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Success Result */}
        {result && (
          <div className="mt-4 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs">
            <div className="flex items-center gap-1.5 font-bold mb-1">
              <CheckCircle2 className="w-4 h-4" />
              <span>{result.message}</span>
            </div>
            {result.sample_titles?.length > 0 && (
              <div className="mt-2 text-[11px] text-slate-300">
                <p className="font-semibold text-slate-400">Sample extracted papers:</p>
                <ul className="list-disc list-inside space-y-0.5 mt-1 text-slate-300">
                  {result.sample_titles.slice(0, 3).map((t, i) => (
                    <li key={i} className="truncate">{t}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Modal Buttons */}
        <div className="mt-6 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-medium text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 transition"
          >
            Close
          </button>
          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="px-5 py-2 rounded-xl text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 transition flex items-center gap-2"
          >
            {uploading ? 'Parsing Records...' : 'Upload & Parse'}
          </button>
        </div>
      </div>
    </div>
  );
}
