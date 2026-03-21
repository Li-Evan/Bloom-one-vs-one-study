import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { login, getMe } from '../lib/api';
import { useAuth } from '../lib/AuthContext';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { setUser } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      const user = await getMe();
      setUser(user);
      navigate('/');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[100dvh] grid md:grid-cols-5">
      {/* Left — branding */}
      <div className="hidden md:flex md:col-span-2 bg-stone-950 flex-col justify-between p-10">
        <div>
          <h2 className="text-lg font-semibold text-white tracking-tight">Bloom</h2>
          <p className="text-stone-500 text-sm mt-1">2-Sigma Learning System</p>
        </div>
        <div>
          <p className="text-stone-400 text-sm leading-relaxed max-w-[30ch]">
            一对一 AI 导师，基于 Bloom 的 2-Sigma 研究，让每个人都能达到前 2% 的学习效果。
          </p>
          <div className="mt-6 h-px bg-stone-800" />
          <p className="text-stone-600 text-xs mt-4">Benjamin Bloom, 1984</p>
        </div>
      </div>

      {/* Right — form */}
      <div className="md:col-span-3 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-sm">
          <div className="md:hidden mb-10">
            <h2 className="text-lg font-semibold text-stone-900 tracking-tight">Bloom</h2>
            <p className="text-stone-400 text-sm mt-0.5">2-Sigma Learning System</p>
          </div>

          <h1 className="text-2xl font-semibold tracking-tight text-stone-900">登录</h1>
          <p className="text-stone-500 text-sm mt-1.5 mb-8">输入你的邮箱和密码</p>

          {error && (
            <div className="bg-rose-50 text-rose-600 px-4 py-2.5 rounded-lg mb-6 text-sm border border-rose-100">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1.5">邮箱</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-3.5 py-2.5 bg-white border border-stone-200 rounded-lg text-sm transition-colors hover:border-stone-300 focus:border-emerald-600 outline-none"
                placeholder="your@email.com"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1.5">密码</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full px-3.5 py-2.5 bg-white border border-stone-200 rounded-lg text-sm transition-colors hover:border-stone-300 focus:border-emerald-600 outline-none"
                placeholder="输入密码"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-emerald-600 text-white py-2.5 rounded-lg text-sm font-medium hover:bg-emerald-700 disabled:opacity-50 transition-all duration-200 cursor-pointer"
            >
              {loading ? '登录中...' : '登录'}
            </button>
          </form>

          <p className="mt-8 text-center text-sm text-stone-400">
            还没有账号？{' '}
            <Link to="/register" className="text-emerald-600 hover:text-emerald-700 font-medium transition-colors">
              注册
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
