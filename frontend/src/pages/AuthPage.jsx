import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function AuthPage() {
  const [mode, setMode] = useState('login');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (mode === 'register') {
        await register(fullName, email, password);
      } else {
        await login(email, password);
      }
      navigate('/');
    } catch (err) {
      setError(err?.response?.data?.detail || 'Authentication failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-xl rounded-2xl border border-slate-800 bg-slate-900/80 p-8 shadow-2xl">
      <div className="flex gap-2">
        <button onClick={() => setMode('login')} className={`rounded-full px-4 py-2 ${mode === 'login' ? 'bg-cyan-600' : 'bg-slate-800'}`}>
          Login
        </button>
        <button onClick={() => setMode('register')} className={`rounded-full px-4 py-2 ${mode === 'register' ? 'bg-cyan-600' : 'bg-slate-800'}`}>
          Register
        </button>
      </div>
      <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
        {mode === 'register' && (
          <input value={fullName} onChange={(e) => setFullName(e.target.value)} className="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3" placeholder="Full name" />
        )}
        <input value={email} onChange={(e) => setEmail(e.target.value)} className="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3" placeholder="Email" type="email" />
        <input value={password} onChange={(e) => setPassword(e.target.value)} className="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3" placeholder="Password" type="password" />
        {error ? <div className="rounded-lg border border-rose-500/40 bg-rose-500/10 p-3 text-sm text-rose-300">{error}</div> : null}
        <button className="w-full rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 px-4 py-3 font-semibold" disabled={loading}>
          {loading ? 'Working...' : mode === 'login' ? 'Sign In' : 'Create Account'}
        </button>
      </form>
      <p className="mt-4 text-center text-sm text-slate-400">Forgot password? Use the reset endpoint in the API.</p>
    </div>
  );
}
