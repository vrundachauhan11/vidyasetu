import React, { useEffect, useState } from 'react';
import { Building2, BookOpen, CheckCircle, Shield, Search } from 'lucide-react';
import { Institution } from '../types';
import { api } from '../services/api';
import { MockBadge } from '../components/layout/MockBadge';

export const Institutions: React.FC = () => {
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    api
      .getInstitutions()
      .then((res) => setInstitutions(res.data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const filtered = institutions.filter(
    (i) =>
      i.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      i.aicte_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      i.state.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              AICTE Approved Institutions Directory
            </h1>
            <MockBadge label="DEMO DIRECTORY" />
          </div>
          <p className="text-xs text-slate-500">
            Institutional accreditation registry with sanctioned intake ceilings and programme approval quotas.
          </p>
        </div>

        <div className="w-72">
          <input
            type="text"
            placeholder="Filter by name, AICTE ID, or state..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
          />
        </div>
      </div>

      {/* Institution Cards */}
      {loading ? (
        <div className="text-center py-16 text-xs text-slate-400">Loading approved institutions...</div>
      ) : filtered.length === 0 ? (
        <div className="bg-white rounded-xl p-8 border border-slate-200 text-center text-xs text-slate-500">
          No institutions found matching '{searchTerm}'.
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {filtered.map((inst) => (
            <div
              key={inst.id}
              className="bg-white rounded-xl p-6 border border-slate-200 shadow-xs hover:border-blue-200 transition-all space-y-4"
            >
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3 pb-4 border-b border-slate-100">
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <Building2 className="w-5 h-5" />
                  </div>
                  <div>
                    <h2 className="text-base font-bold text-slate-900 leading-tight">{inst.name}</h2>
                    <div className="flex flex-wrap items-center gap-2 mt-1 text-xs text-slate-500">
                      <span className="font-mono font-medium text-slate-700 bg-slate-100 px-2 py-0.5 rounded">
                        {inst.aicte_id}
                      </span>
                      <span>•</span>
                      <span>{inst.district}, {inst.state}</span>
                      <span>•</span>
                      <span>{inst.institution_type}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                    <CheckCircle className="w-3 h-3 text-emerald-600" />
                    {inst.approval_status}
                  </span>
                </div>
              </div>

              {/* Approved Programmes List */}
              <div>
                <h3 className="text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
                  <BookOpen className="w-3.5 h-3.5 text-slate-400" />
                  Approved Programmes & Sanctioned Intake Capacity
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {inst.programmes?.map((prog) => (
                    <div
                      key={prog.id}
                      className="p-3 bg-slate-50 rounded-lg border border-slate-200/80 flex flex-col justify-between"
                    >
                      <div>
                        <div className="flex items-center justify-between text-xs mb-1">
                          <span className="font-semibold text-slate-800 truncate" title={prog.programme_name}>
                            {prog.programme_name}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-500 mb-2">
                          {prog.approved_quota_details}
                        </p>
                      </div>
                      <div className="pt-2 border-t border-slate-200/60 flex items-center justify-between text-xs">
                        <span className="text-slate-400">Sanctioned Seats</span>
                        <span className="font-bold text-blue-700 font-mono">
                          {prog.sanctioned_intake} Seats
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
