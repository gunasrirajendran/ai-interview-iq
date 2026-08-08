import { Routes, Route, NavLink, Navigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import InterviewPage from './pages/InterviewPage';
import ReportPage from './pages/ReportPage';
import AuthPage from './pages/AuthPage';
import HistoryPage from './pages/HistoryPage';
import AdminPage from './pages/AdminPage';
import { useAuth } from './contexts/AuthContext';

function App() {
  const { user, loading, logout } = useAuth();

  if (loading) {
    return <div className="flex min-h-screen items-center justify-center text-slate-300">Loading your workspace...</div>;
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <nav className="border-b border-slate-800 bg-slate-900/80 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div className="text-xl font-semibold">InterviewIQ</div>
          <div className="flex items-center gap-4 text-sm">
            <NavLink to="/" className={({ isActive }) => isActive ? 'text-cyan-400' : 'text-slate-300'}>Dashboard</NavLink>
            <NavLink to="/interview" className={({ isActive }) => isActive ? 'text-cyan-400' : 'text-slate-300'}>Interview</NavLink>
            <NavLink to="/report" className={({ isActive }) => isActive ? 'text-cyan-400' : 'text-slate-300'}>Report</NavLink>
            <NavLink to="/history" className={({ isActive }) => isActive ? 'text-cyan-400' : 'text-slate-300'}>History</NavLink>
            <NavLink to="/admin" className={({ isActive }) => isActive ? 'text-cyan-400' : 'text-slate-300'}>Admin</NavLink>
            {user ? (
              <button onClick={logout} className="rounded-full border border-slate-700 px-3 py-1 text-slate-300">Logout</button>
            ) : (
              <NavLink to="/auth" className={({ isActive }) => isActive ? 'text-cyan-400' : 'text-slate-300'}>Auth</NavLink>
            )}
          </div>
        </div>
      </nav>
      <main className="mx-auto max-w-7xl px-6 py-8">
        <Routes>
          <Route path="/" element={user ? <Dashboard /> : <Navigate to="/auth" replace />} />
          <Route path="/interview" element={user ? <InterviewPage /> : <Navigate to="/auth" replace />} />
          <Route path="/report" element={user ? <ReportPage /> : <Navigate to="/auth" replace />} />
          <Route path="/history" element={user ? <HistoryPage /> : <Navigate to="/auth" replace />} />
          <Route path="/admin" element={user ? <AdminPage /> : <Navigate to="/auth" replace />} />
          <Route path="/auth" element={!user ? <AuthPage /> : <Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;

