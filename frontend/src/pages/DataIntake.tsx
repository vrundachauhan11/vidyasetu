import React, { useEffect, useState } from 'react';
import { UploadCloud, FileSpreadsheet, CheckCircle2, AlertCircle, RefreshCw, FileText, Download } from 'lucide-react';
import { IntakeBatch } from '../types';
import { api } from '../services/api';
import { MockBadge } from '../components/layout/MockBadge';

export const DataIntake: React.FC = () => {
  const [batches, setBatches] = useState<IntakeBatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<any | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const fetchBatches = () => {
    setLoading(true);
    api
      .getBatches()
      .then((res) => setBatches(res.data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchBatches();
  }, []);

  const handleFileUpload = async (file: File) => {
    setUploading(true);
    setErrorMsg(null);
    setUploadResult(null);

    try {
      const res = await api.uploadCSV(file);
      setUploadResult(res);
      fetchBatches();
    } catch (err: any) {
      setErrorMsg(err.message || 'CSV intake upload failed.');
    } finally {
      setUploading(false);
    }
  };

  const handlePrebuiltDemoUpload = async () => {
    setUploading(true);
    setErrorMsg(null);
    setUploadResult(null);

    try {
      const sampleText = await api.getSampleCSV();
      const blob = new Blob([sampleText], { type: 'text/csv' });
      const syntheticFile = new File([blob], 'Synthetic_Institutional_Intake_Round2.csv', {
        type: 'text/csv',
      });
      const res = await api.uploadCSV(syntheticFile);
      setUploadResult(res);
      fetchBatches();
    } catch (err: any) {
      setErrorMsg(err.message || 'Prebuilt demo upload failed.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              Institutional Data Intake Desk
            </h1>
            <MockBadge label="CSV INTAKE ENGINE" />
          </div>
          <p className="text-xs text-slate-500">
            Stage 1 & 2 of the pipeline: Ingest synthetic institutional student rosters, validate CSV schemas, and trigger automated verification.
          </p>
        </div>

        <button
          onClick={handlePrebuiltDemoUpload}
          disabled={uploading}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold flex items-center gap-2 transition-all shadow-xs disabled:opacity-50"
        >
          <FileText className="w-4 h-4" />
          {uploading ? 'Processing Intake...' : '1-Click: Test Pre-Built Synthetic CSV'}
        </button>
      </div>

      {/* Upload Dropzone */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-xl p-6 border-2 border-dashed border-slate-300 hover:border-blue-400 transition-colors flex flex-col items-center justify-center text-center space-y-4">
          <div className="w-14 h-14 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center">
            <UploadCloud className="w-7 h-7" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-800">
              Upload Institutional Admissions CSV
            </h3>
            <p className="text-xs text-slate-500 mt-1 max-w-md">
              CSV file must contain standard regulatory columns: <code className="bg-slate-100 px-1 py-0.5 rounded text-[11px] font-mono">student_name, apaar_id, dob, gender, category, quota, enrolment_number</code>.
            </p>
          </div>

          <label className="cursor-pointer px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg border border-slate-300 transition-colors">
            <span>Browse Local CSV</span>
            <input
              type="file"
              accept=".csv"
              className="hidden"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  handleFileUpload(e.target.files[0]);
                }
              }}
            />
          </label>
        </div>

        {/* Schema Info Card */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <FileSpreadsheet className="w-4 h-4 text-blue-600" />
              <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                Intake Schema Requirements
              </h3>
            </div>
            <ul className="text-xs text-slate-600 space-y-2 mt-3">
              <li className="flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-1.5" />
                <span><strong>Header row required:</strong> UTF-8 encoded.</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-1.5" />
                <span><strong>APAAR Format:</strong> Synthetic prefix or 12-digit mock code.</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-1.5" />
                <span><strong>Non-punitive handling:</strong> Empty APAAR records trigger verification triage, not rejection.</span>
              </li>
            </ul>
          </div>

          <div className="pt-3 border-t border-slate-100">
            <a
              href="/api/intake/sample-csv"
              target="_blank"
              rel="noreferrer"
              className="text-xs text-blue-600 hover:text-blue-800 font-semibold inline-flex items-center gap-1"
            >
              <Download className="w-3.5 h-3.5" /> Download Template CSV
            </a>
          </div>
        </div>
      </div>

      {/* Upload Feedback / Alerts */}
      {errorMsg && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800 flex items-start gap-3">
          <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0 mt-0.5" />
          <div>
            <span className="font-bold">Schema / Intake Error:</span> {errorMsg}
          </div>
        </div>
      )}

      {uploadResult && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-900 flex items-start gap-3">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-bold">Batch Ingestion Succeeded!</span>
            <p>{uploadResult.message}</p>
            <div className="flex gap-4 font-mono text-[11px] mt-1 text-emerald-800">
              <span>Total: {uploadResult.summary?.total_records}</span>
              <span>Valid: {uploadResult.summary?.valid_records}</span>
              <span>Signals Flagged: {uploadResult.summary?.flagged_records}</span>
            </div>
          </div>
        </div>
      )}

      {/* Batch History Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-200 bg-slate-50/50 flex items-center justify-between">
          <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
            Intake Batch History
          </h3>
          <button
            onClick={fetchBatches}
            className="text-slate-500 hover:text-slate-700 p-1 rounded"
            title="Refresh batches"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>

        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider text-[11px]">
              <th className="py-3 px-4">Batch Reference</th>
              <th className="py-3 px-4">Filename</th>
              <th className="py-3 px-4">Academic Year</th>
              <th className="py-3 px-4">Total</th>
              <th className="py-3 px-4">Valid</th>
              <th className="py-3 px-4">Flagged</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4">Timestamp</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {loading ? (
              <tr>
                <td colSpan={8} className="py-8 text-center text-slate-400">Loading batch records...</td>
              </tr>
            ) : batches.length === 0 ? (
              <tr>
                <td colSpan={8} className="py-8 text-center text-slate-400">No batch records found.</td>
              </tr>
            ) : (
              batches.map((b) => (
                <tr key={b.id} className="hover:bg-slate-50/70">
                  <td className="py-3 px-4 font-mono font-semibold text-slate-800">{b.reference}</td>
                  <td className="py-3 px-4 text-slate-600 truncate max-w-xs">{b.filename}</td>
                  <td className="py-3 px-4 text-slate-600">{b.academic_year}</td>
                  <td className="py-3 px-4 font-bold text-slate-800">{b.total_records}</td>
                  <td className="py-3 px-4 text-emerald-700 font-semibold">{b.valid_records}</td>
                  <td className="py-3 px-4 text-amber-600 font-semibold">{b.flagged_records}</td>
                  <td className="py-3 px-4">
                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                        b.status === 'COMPLETED'
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : 'bg-amber-50 text-amber-700 border border-amber-200'
                      }`}
                    >
                      {b.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-slate-400 font-mono text-[11px]">{b.uploaded_at}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
