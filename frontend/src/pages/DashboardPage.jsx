import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getCourses, createCourse } from '../lib/api';
import { useAuth } from '../lib/AuthContext';

export default function DashboardPage() {
  const [courses, setCourses] = useState([]);
  const [newCourseName, setNewCourseName] = useState('');
  const [showCreate, setShowCreate] = useState(false);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  useEffect(() => {
    getCourses()
      .then(setCourses)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!newCourseName.trim() || creating) return;
    setError('');
    setCreating(true);
    try {
      const course = await createCourse(newCourseName.trim());
      setCourses([course, ...courses]);
      setNewCourseName('');
      setShowCreate(false);
      navigate(`/course/${course.id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setCreating(false);
    }
  };

  const statusLabel = (status) => {
    if (status === 'completed') return { text: '已完成', color: 'bg-green-100 text-green-700' };
    return { text: '学习中', color: 'bg-indigo-100 text-indigo-700' };
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-900">Bloom 学习系统</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-500">
              {user?.username} · <span className="text-indigo-600 font-medium">{user?.credits} 积分</span>
            </span>
            <button onClick={() => navigate('/credits')} className="text-sm text-gray-600 hover:text-indigo-600">
              积分明细
            </button>
            <button onClick={() => { logout(); navigate('/login'); }} className="text-sm text-red-500 hover:text-red-600">
              退出
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-800">我的课程</h2>
          <button
            onClick={() => setShowCreate(!showCreate)}
            className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-indigo-700 transition-colors"
          >
            + 新课程
          </button>
        </div>

        {error && (
          <div className="mb-4 bg-red-50 text-red-600 text-sm px-4 py-2 rounded-lg">{error}</div>
        )}

        {showCreate && (
          <form onSubmit={handleCreate} className="mb-6 flex gap-2">
            <input
              type="text"
              value={newCourseName}
              onChange={(e) => setNewCourseName(e.target.value)}
              placeholder="输入课题名称，例如「博弈论基础」"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
              autoFocus
              disabled={creating}
            />
            <button
              type="submit"
              disabled={creating}
              className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-indigo-700 disabled:opacity-50"
            >
              {creating ? '创建中...' : '创建'}
            </button>
          </form>
        )}

        {loading ? (
          <p className="text-gray-400 text-center py-12">加载中...</p>
        ) : courses.length === 0 ? (
          <div className="text-center py-16">
            <p className="text-gray-400 mb-4">还没有课程</p>
            <p className="text-gray-500 text-sm">点击「+ 新课程」开始你的第一次一对一学习</p>
          </div>
        ) : (
          <div className="grid gap-3">
            {courses.map((course) => {
              const s = statusLabel(course.status);
              return (
                <button
                  key={course.id}
                  onClick={() => navigate(`/course/${course.id}`)}
                  className="bg-white rounded-xl p-4 text-left border border-gray-200 hover:border-indigo-300 hover:shadow-sm transition-all"
                >
                  <div className="flex items-center justify-between">
                    <h3 className="font-medium text-gray-800">{course.name}</h3>
                    <div className="flex items-center gap-2">
                      <span className={`text-xs px-2 py-0.5 rounded-full ${s.color}`}>{s.text}</span>
                      <span className="text-xs text-gray-400">{course.lesson_count} 篇课文</span>
                    </div>
                  </div>
                  <p className="text-xs text-gray-400 mt-1">
                    创建于 {new Date(course.created_at).toLocaleDateString('zh-CN')}
                  </p>
                </button>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}
