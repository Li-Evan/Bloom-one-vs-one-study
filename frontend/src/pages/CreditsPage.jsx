import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getBalance, getCreditHistory } from '../lib/api';
import { useAuth } from '../lib/AuthContext';

export default function CreditsPage() {
  const [balance, setBalance] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { user } = useAuth();

  useEffect(() => {
    Promise.all([getBalance(), getCreditHistory()])
      .then(([b, h]) => { setBalance(b.credits); setHistory(h); })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const typeLabels = {
    registration_bonus: '注册赠送',
    chat_deduction: '课文生成',
    admin_topup: '管理员充值',
    refund: '退款',
  };

  return (
    <div className="min-h-[100dvh] bg-stone-50">
      <header className="bg-white border-b border-stone-200/60 sticky top-0 z-10">
        <div className="max-w-[800px] mx-auto px-6 py-3.5 flex items-center justify-between">
          <button
            onClick={() => navigate('/')}
            className="text-stone-400 hover:text-stone-700 text-sm transition-colors flex items-center gap-1.5"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
            </svg>
            返回
          </button>
          <span className="text-xs text-stone-400 font-mono">CREDITS</span>
        </div>
      </header>

      <main className="max-w-[800px] mx-auto px-6 py-10">
        {error && (
          <div className="mb-6 bg-rose-50 text-rose-600 text-sm px-4 py-2.5 rounded-lg border border-rose-100">
            {error}
          </div>
        )}

        {/* Balance */}
        <div className="bg-stone-900 rounded-2xl p-8 mb-10">
          <p className="text-stone-500 text-xs uppercase tracking-wide mb-2">当前余额</p>
          <p className="text-4xl font-semibold text-white tracking-tight font-mono tabular-nums">
            {balance !== null ? balance.toFixed(0) : '--'}
          </p>
          <div className="mt-5 pt-4 border-t border-stone-800 flex items-center gap-2">
            <span className="text-stone-600 text-xs">{user?.username}</span>
            <span className="text-stone-700 text-xs">/</span>
            <span className="text-stone-600 text-xs">{user?.email}</span>
          </div>
        </div>

        {/* History */}
        <h2 className="text-xs font-medium text-stone-500 uppercase tracking-wide mb-4">交易记录</h2>

        {loading ? (
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <div key={i} className="bg-white rounded-lg border border-stone-200/60 p-4 animate-pulse">
                <div className="h-3 bg-stone-100 rounded w-1/4 mb-2" />
                <div className="h-2 bg-stone-50 rounded w-1/3" />
              </div>
            ))}
          </div>
        ) : history.length === 0 ? (
          <div className="py-16 text-center">
            <p className="text-stone-400 text-sm">暂无交易记录</p>
          </div>
        ) : (
          <div className="divide-y divide-stone-100">
            {history.map((tx) => (
              <div
                key={tx.id}
                className="py-3.5 flex items-center justify-between"
              >
                <div>
                  <p className="text-sm text-stone-700">
                    {typeLabels[tx.type] || tx.type}
                  </p>
                  <p className="text-xs text-stone-400 mt-0.5">{tx.description}</p>
                  <p className="text-xs text-stone-300 mt-0.5 font-mono tabular-nums">
                    {new Date(tx.created_at).toLocaleString('zh-CN')}
                  </p>
                </div>
                <div className="text-right">
                  <p className={`font-mono tabular-nums text-sm font-medium ${tx.amount > 0 ? 'text-emerald-600' : 'text-stone-600'}`}>
                    {tx.amount > 0 ? '+' : ''}{tx.amount ?? 0}
                  </p>
                  <p className="text-xs text-stone-300 font-mono tabular-nums mt-0.5">
                    {tx.balance_after ?? 0}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
