import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../lib/api';

export default function HistoryPage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/history/me').then((res) => setItems(res.data)).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-slate-300">Loading interview history...</div>;

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Interview History</h2>
        <Link to="/interview" className="text-sm text-cyan-400">Start new interview</Link>
      </div>
      <div className="mt-6 space-y-3">
        {items.length === 0 ? (
          <div className="rounded-xl border border-dashed border-slate-700 p-6 text-sm text-slate-400">No interviews yet.</div>
        ) : items.map((item) => (
          <div key={item.id} className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-800/70 p-4">
            <div>
              <p className="font-medium">{item.interview_type}</p>
              <p className="text-sm text-slate-400">{new Date(item.created_at).toLocaleString()}</p>
            </div>
            <div className="flex items-center gap-3">
              <span className="rounded-full bg-cyan-500/15 px-3 py-1 text-sm text-cyan-300">Score {item.score}</span>
              {item.has_report ? <Link to="/report" className="text-sm text-violet-400">Open report</Link> : null}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
