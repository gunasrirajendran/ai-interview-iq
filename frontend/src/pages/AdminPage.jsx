import { useEffect, useState } from 'react';
import api from '../lib/api';

export default function AdminPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get('/admin/stats')
      .then((res) => setStats(res.data))
      .catch((err) => setError(err?.response?.data?.detail || 'Failed to load admin stats'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-slate-400">Loading admin stats...</div>;
  if (error) return <div className="rounded-xl border border-rose-500/40 bg-rose-500/10 p-4 text-rose-300">{error}</div>;

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Admin Console</h2>
      <div className="grid gap-4 md:grid-cols-4">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-xl">
          <p className="text-sm text-slate-400">Total Users</p>
          <p className="mt-2 text-3xl font-semibold">{stats?.total_users ?? 0}</p>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-xl">
          <p className="text-sm text-slate-400">Total Interviews</p>
          <p className="mt-2 text-3xl font-semibold">{stats?.total_interviews ?? 0}</p>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-xl">
          <p className="text-sm text-slate-400">Average Score</p>
          <p className="mt-2 text-3xl font-semibold">{stats?.average_score ?? 0}%</p>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-xl">
          <p className="text-sm text-slate-400">Daily Active Users</p>
          <p className="mt-2 text-3xl font-semibold">{stats?.daily_active_users ?? 0}</p>
        </div>
      </div>
      <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6">
        <h3 className="text-lg font-semibold">Top Weak Topics across Candidate Pool</h3>
        <ul className="mt-3 space-y-2 text-sm text-slate-300">
          {(stats?.top_weak_topics || []).map((topic) => (
            <li key={topic} className="rounded-lg bg-slate-800 p-3">• {topic}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
