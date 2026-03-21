import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getCourses, createCourse } from '../lib/api';

export default function DashboardPage() {
  const [courses, setCourses] = useState([]);
  const [newCourseName, setNewCourseName] = useState('');
  const [newCourseRef, setNewCourseRef] = useState('');
  const [showCreate, setShowCreate] = useState(false);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

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
      const course = await createCourse(newCourseName.trim(), newCourseRef.trim());
      setCourses([course, ...courses]);
      setNewCourseName('');
      setNewCourseRef('');
      setShowCreate(false);
      navigate(`/course/${course.id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="min-h-[100dvh] bg-stone-50">
      {/* Header — dark */}
      <header className="bg-stone-900 sticky top-0 z-10">
        <div className="max-w-[1100px] mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h1 className="text-base font-semibold text-white tracking-tight">Bloom</h1>
            <span className="text-stone-600 text-xs font-mono">2-Sigma Learning</span>
          </div>
        </div>
      </header>

      <main className="max-w-[1100px] mx-auto px-6 py-10">
        {/* Page title + action */}
        <div className="flex items-end justify-between mb-8">
          <div>
            <h2 className="text-2xl font-semibold tracking-tight text-stone-900">我的课程</h2>
            <p className="text-sm text-stone-400 mt-1">点击课程卡片进入学习</p>
          </div>
          <button
            onClick={() => setShowCreate(!showCreate)}
            className="bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-emerald-700 transition-all duration-200 cursor-pointer"
          >
            新建课程
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-rose-50 text-rose-600 text-sm px-4 py-2.5 rounded-lg mb-6 border border-rose-100">
            {error}
          </div>
        )}

        {/* Create form */}
        {showCreate && (
          <form onSubmit={handleCreate} className="mb-8 bg-white rounded-xl border border-stone-200/60 p-5 space-y-4">
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1.5">课题名称</label>
              <input
                type="text"
                value={newCourseName}
                onChange={(e) => setNewCourseName(e.target.value)}
                placeholder="例如「博弈论基础」「Python 装饰器」"
                className="w-full px-3.5 py-2.5 bg-white border border-stone-200 rounded-lg text-sm transition-colors hover:border-stone-300 focus:border-emerald-600 outline-none"
                autoFocus
                disabled={creating}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1.5">
                参考材料
                <span className="text-stone-400 font-normal ml-1">（可选）</span>
              </label>
              <textarea
                value={newCourseRef}
                onChange={(e) => setNewCourseRef(e.target.value)}
                placeholder="粘贴课本章节、论文摘要、笔记、或任何你希望 AI 参考的内容..."
                className="w-full border border-stone-200 rounded-lg p-3.5 text-sm resize-none h-28 transition-colors hover:border-stone-300 focus:border-emerald-600 outline-none"
                disabled={creating}
              />
              <p className="text-xs text-stone-400 mt-1">AI 会根据这些材料设计课程大纲和课文内容</p>
            </div>
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={creating}
                className="bg-stone-900 text-white px-5 py-2.5 rounded-lg text-sm font-medium hover:bg-stone-800 disabled:opacity-50 transition-all duration-200 cursor-pointer"
              >
                {creating ? '创建中...' : '创建课程'}
              </button>
            </div>
          </form>
        )}

        {/* Course list */}
        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="bg-white rounded-xl border border-stone-200/60 p-5 animate-pulse">
                <div className="h-4 bg-stone-100 rounded w-1/3 mb-3" />
                <div className="h-3 bg-stone-50 rounded w-1/5" />
              </div>
            ))}
          </div>
        ) : courses.length === 0 ? (
          <div className="py-20 text-center">
            <div className="w-12 h-12 rounded-full bg-stone-100 mx-auto mb-4 flex items-center justify-center">
              <svg className="w-5 h-5 text-stone-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
              </svg>
            </div>
            <p className="text-stone-400 text-sm mb-1">还没有课程</p>
            <p className="text-stone-300 text-xs">点击「新建课程」开始你的第一次一对一学习</p>
          </div>
        ) : (
          <div className="space-y-2">
            {courses.map((course) => (
              <button
                key={course.id}
                onClick={() => navigate(`/course/${course.id}`)}
                className="w-full bg-white rounded-xl p-5 text-left border border-stone-200/60 hover:border-stone-300 hover:shadow-[0_2px_12px_-4px_rgba(0,0,0,0.06)] transition-all duration-200 group cursor-pointer"
              >
                <div className="flex items-center justify-between">
                  <h3 className="font-medium text-stone-800 group-hover:text-stone-900 transition-colors">
                    {course.name}
                  </h3>
                  <div className="flex items-center gap-3">
                    {course.status === 'completed' ? (
                      <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-600 border border-emerald-100">
                        已完成
                      </span>
                    ) : (
                      <span className="text-xs px-2 py-0.5 rounded-full bg-stone-50 text-stone-500 border border-stone-100">
                        学习中
                      </span>
                    )}
                    <span className="text-xs text-stone-400 font-mono tabular-nums">
                      {course.lesson_count} 篇
                    </span>
                    <svg className="w-4 h-4 text-stone-300 group-hover:text-stone-500 group-hover:translate-x-0.5 transition-all" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
                    </svg>
                  </div>
                </div>
                <p className="text-xs text-stone-400 mt-1.5 font-mono tabular-nums">
                  {new Date(course.created_at).toLocaleDateString('zh-CN')}
                </p>
              </button>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
