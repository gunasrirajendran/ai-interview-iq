export default function StatCard({ title, value, detail }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-xl">
      <p className="text-sm text-slate-400">{title}</p>
      <p className="mt-3 text-3xl font-semibold">{value}</p>
      <p className="mt-2 text-sm text-cyan-400">{detail}</p>
    </div>
  );
}
