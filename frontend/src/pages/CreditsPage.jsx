import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getBalance, getCreditHistory } from '../lib/api';
import { useAuth } from '../lib/AuthContext';

export default function CreditsPage() {
  const [balance, setBalance] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { user } = useAuth();

  useEffect(() => {
    Promise.all([getBalance(), getCreditHistory()])
      .then(([b, h]) => {
        setBalance(b.credits);
        setHistory(h);
      })
      .finally(() => setLoading(false));
  }, []);

  const typeLabels = {
    registration_bonus: '注册赠送',
    chat_deduction: '对话消耗',
    admin_topup: '管理员充值',
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <button onClick={() => navigate('/')} className="text-gray-600 hover:text-gray-900">
            &larr; 返回
          </button>
          <h1 className="text-lg font-bold text-gray-900">积分明细</h1>
          <div className="w-16" />
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Balance card */}
        <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl p-6 text-white mb-8">
          <p className="text-sm opacity-80">当前积分余额</p>
          <p className="text-4xl font-bold mt-1">{balance !== null ? balance.toFixed(0) : '...'}</p>
          <p className="text-xs opacity-60 mt-2">{user?.username} · {user?.email}</p>
        </div>

        {/* History */}
        <h2 className="text-lg font-semibold text-gray-800 mb-4">交易记录</h2>
        {loading ? (
          <p className="text-gray-400 text-center py-8">加载中...</p>
        ) : history.length === 0 ? (
          <p className="text-gray-400 text-center py-8">暂无交易记录</p>
        ) : (
          <div className="space-y-2">
            {history.map((tx) => (
              <div
                key={tx.id}
                className="bg-white rounded-lg p-4 border border-gray-200 flex items-center justify-between"
              >
                <div>
                  <p className="text-sm font-medium text-gray-800">
                    {typeLabels[tx.type] || tx.type}
                  </p>
                  <p className="text-xs text-gray-400">{tx.description}</p>
                  <p className="text-xs text-gray-400 mt-1">
                    {new Date(tx.created_at).toLocaleString('zh-CN')}
                  </p>
                </div>
                <div className="text-right">
                  <p className={`font-semibold ${tx.amount > 0 ? 'text-green-600' : 'text-red-500'}`}>
                    {tx.amount > 0 ? '+' : ''}{tx.amount.toFixed(0)}
                  </p>
                  <p className="text-xs text-gray-400">余额 {tx.balance_after.toFixed(0)}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
