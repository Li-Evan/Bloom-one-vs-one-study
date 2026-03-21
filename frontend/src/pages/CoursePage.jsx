import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { getCourse, getLessons, getSummary } from '../lib/api';

const stripFences = (text) => {
  if (!text) return '';
  let t = text.trim();
  if (/^```(?:markdown|md)?\s*\n?/i.test(t)) {
    t = t.replace(/^```(?:markdown|md)?\s*\n?/i, '').replace(/\n?```\s*$/, '');
  }
  return t.trim();
};

export default function CoursePage() {
  const { courseId } = useParams();
  const navigate = useNavigate();
  const [course, setCourse] = useState(null);
  const [lessons, setLessons] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showSyllabus, setShowSyllabus] = useState(true);

  useEffect(() => {
    Promise.all([getCourse(courseId), getLessons(courseId)])
      .then(([c, l]) => {
        setCourse(c);
        setLessons(l);
        if (c.status === 'completed') {
          getSummary(courseId).then(setSummary).catch(() => {});
        }
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [courseId]);

  if (loading) {
    return (
      <div className="min-h-[100dvh] bg-stone-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 rounded-full border-2 border-stone-200 border-t-emerald-600 animate-spin mx-auto" />
          <p className="text-stone-400 text-sm mt-3">加载中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-[100dvh] bg-stone-50 flex flex-col items-center justify-center gap-4">
        <p className="text-rose-500 text-sm">{error}</p>
        <button onClick={() => navigate('/')} className="text-emerald-600 hover:text-emerald-700 text-sm font-medium transition-colors">
          返回首页
        </button>
      </div>
    );
  }

  const normalLessons = lessons.filter((l) => l.number > 0);

  return (
    <div className="min-h-[100dvh] bg-stone-50">
      <header className="bg-white border-b border-stone-200/60 sticky top-0 z-10">
        <div className="max-w-[1100px] mx-auto px-6 py-3.5 flex items-center justify-between">
          <button
            onClick={() => navigate('/')}
            className="text-stone-400 hover:text-stone-700 text-sm transition-colors flex items-center gap-1.5"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
            </svg>
            返回
          </button>
          <span className="text-xs text-stone-400 font-mono">
            {course.status === 'completed' ? 'COMPLETED' : 'IN PROGRESS'}
          </span>
        </div>
      </header>

      <main className="max-w-[1100px] mx-auto px-6 py-10">
        <h1 className="text-2xl font-semibold tracking-tight text-stone-900 mb-8">{course.name}</h1>

        <div className="grid md:grid-cols-3 gap-8">
          {/* Left: Syllabus */}
          <div className="md:col-span-1">
            <div className="bg-white rounded-xl border border-stone-200/60 p-5 sticky top-20">
              <button
                onClick={() => setShowSyllabus(!showSyllabus)}
                className="w-full flex items-center justify-between text-sm font-medium text-stone-700"
              >
                <span>课程大纲</span>
                <svg
                  className={`w-4 h-4 text-stone-400 transition-transform duration-200 ${showSyllabus ? 'rotate-180' : ''}`}
                  fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
                </svg>
              </button>
              {showSyllabus && course.syllabus_content && (
                <div className="mt-4 pt-4 border-t border-stone-100 prose prose-sm prose-stone max-w-none">
                  <ReactMarkdown>{stripFences(course.syllabus_content)}</ReactMarkdown>
                </div>
              )}
            </div>
          </div>

          {/* Right: Lesson List */}
          <div className="md:col-span-2">
            <h2 className="text-sm font-medium text-stone-500 uppercase tracking-wide mb-4">课文列表</h2>

            {normalLessons.length === 0 ? (
              <div className="py-16 text-center">
                <p className="text-stone-400 text-sm">暂无课文</p>
              </div>
            ) : (
              <div className="space-y-2">
                {normalLessons.map((lesson, index) => (
                  <button
                    key={lesson.id}
                    onClick={() => navigate(`/course/${courseId}/lesson/${lesson.number}`)}
                    className="w-full bg-white rounded-xl p-4 text-left border border-stone-200/60 hover:border-stone-300 hover:shadow-[0_2px_12px_-4px_rgba(0,0,0,0.06)] transition-all duration-200 group cursor-pointer"
                    style={{ animationDelay: `${index * 60}ms` }}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span className="w-8 h-8 rounded-lg bg-stone-50 border border-stone-100 flex items-center justify-center text-xs font-mono text-stone-500">
                          {String(lesson.number).padStart(2, '0')}
                        </span>
                        <span className="font-medium text-stone-700 text-sm group-hover:text-stone-900 transition-colors">
                          第 {String(lesson.number).padStart(2, '0')} 篇
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        {lesson.is_evaluation && (
                          <span className="text-xs px-2 py-0.5 rounded-full bg-amber-50 text-amber-600 border border-amber-100">
                            评估篇
                          </span>
                        )}
                        <span className="text-xs text-stone-400 font-mono tabular-nums">
                          {new Date(lesson.created_at).toLocaleDateString('zh-CN')}
                        </span>
                        <svg className="w-4 h-4 text-stone-300 group-hover:text-stone-500 group-hover:translate-x-0.5 transition-all" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
                        </svg>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}

            {/* Summary section */}
            {summary && (
              <div className="mt-8 bg-white rounded-xl border border-emerald-200/60 p-6">
                <h3 className="text-sm font-medium text-emerald-700 mb-4 uppercase tracking-wide">课程总结</h3>
                <div className="prose prose-sm prose-stone max-w-none">
                  <ReactMarkdown>{stripFences(summary.content)}</ReactMarkdown>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
