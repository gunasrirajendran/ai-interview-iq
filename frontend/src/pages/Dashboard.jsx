import { useEffect, useState } from 'react';
import { LineChart, Line, ResponsiveContainer, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';
import api from '../lib/api';

export default function Dashboard() {
  const [stats, setStats] = useState({ totalInterviews: 0, averageScore: 0, latestInterviews: [], progress: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const response = await api.get('/history/me');
        const items = response.data || [];
        const avgScore = items.length ? Math.round(items.reduce((acc, curr) => acc + (curr.score || 0), 0) / items.length) : 0;
        setStats({
          totalInterviews: items.length,
          averageScore: avgScore,
          latestInterviews: items.slice(0, 5).map((item) => ({ role: item.interview_type, score: item.score })),
          progress: items.slice(-5).map((item, idx) => ({ name: `#${idx + 1}`, score: item.score })),
        });
      } catch (err) {
        setStats({ totalInterviews: 0, averageScore: 0, latestInterviews: [], progress: [] });
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-xl">
          <p className="text-sm text-slate-400">Total Interviews</p>
          <p className="mt-3 text-3xl font-semibold">{loading ? '—' : stats.totalInterviews}</p>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-xl">
          <p className="text-sm text-slate-400">Average Score</p>
          <p className="mt-3 text-3xl font-semibold">{loading ? '—' : `${stats.averageScore}%`}</p>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-xl">
          <p className="text-sm text-slate-400">Latest Interviews</p>
          <p className="mt-3 text-lg font-semibold">{loading ? '—' : stats.latestInterviews.length}</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6">
          <h2 className="text-lg font-semibold">Progress Chart</h2>
          <div className="mt-4 h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={stats.progress}>
                <CartesianGrid stroke="#334155" strokeDasharray="5 5" />
                <XAxis dataKey="name" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip />
                <Line type="monotone" dataKey="score" stroke="#22d3ee" strokeWidth={3} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6">
          <h2 className="text-lg font-semibold">Latest Interviews</h2>
          <ul className="mt-4 space-y-3 text-sm text-slate-300">
            {stats.latestInterviews.map((item, index) => (
              <li key={`${item.role}-${index}`} className="rounded-lg bg-slate-800 p-3">{item.role} • {item.score}%</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
