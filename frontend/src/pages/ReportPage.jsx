import { useEffect, useState } from 'react';
import api from '../lib/api';

export default function ReportPage() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const historyRes = await api.get('/history/me');
        const latestWithReport = (historyRes.data || []).find((item) => item.has_report);
        if (latestWithReport) {
          const response = await api.get(`/report/${latestWithReport.id}`);
          setReport(response.data);
        } else {
          setReport(null);
        }
      } catch (err) {
        setReport(null);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) return <div className="text-slate-400">Loading report...</div>;
  if (!report) return <div className="rounded-xl border border-dashed border-slate-700 p-8 text-center text-slate-400">No report available yet. Complete an interview session to generate your report.</div>;

  const score = report?.scores?.[0] || {};
  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6">
        <h2 className="text-xl font-semibold">Final AI Report</h2>
        <p className="mt-2 text-sm text-slate-400">{report?.summary}</p>
        <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {[
            ['Overall Score', `${Math.round((score.technical_score + score.communication_score + score.confidence_score) / 3)}%`],
            ['Technical Score', `${score.technical_score ?? 0}%`],
            ['Communication Score', `${score.communication_score ?? 0}%`],
            ['Eye Contact Score', `${score.eye_contact_score ?? 0}%`],
          ].map(([label, value]) => (
            <div key={label} className="rounded-xl bg-slate-800 p-4">
              <p className="text-sm text-slate-400">{label}</p>
              <p className="mt-2 text-2xl font-semibold">{value}</p>
            </div>
          ))}
        </div>
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6">
          <h3 className="text-lg font-semibold">Strengths</h3>
          <ul className="mt-3 space-y-2 text-sm text-slate-300">
            <li>• Structured thinking</li>
            <li>• Clear communication</li>
          </ul>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6">
          <h3 className="text-lg font-semibold">Weaknesses</h3>
          <ul className="mt-3 space-y-2 text-sm text-slate-300">
            <li>• Concurrency</li>
            <li>• System Design</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
