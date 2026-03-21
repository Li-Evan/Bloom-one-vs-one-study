import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { getCourse, getLessons, getSummary } from '../lib/api';

// Strip wrapping ```markdown fences from AI output
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
    Promise.all([
      getCourse(courseId),
      getLessons(courseId),
    ])
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
      <div className="min-h-screen flex items-center justify-center text-gray-400">加载中...</div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4">
        <p className="text-red-500">{error}</p>
        <button onClick={() => navigate('/')} className="text-indigo-600 hover:underline">返回首页</button>
      </div>
    );
  }

  const normalLessons = lessons.filter((l) => l.number > 0);

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
          <button onClick={() => navigate('/')} className="text-gray-600 hover:text-gray-900 text-sm">
            &larr; 返回课程列表
          </button>
          <span className="text-sm text-gray-500">
            {course.status === 'completed' ? '已完成' : '学习中'}
          </span>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">{course.name}</h1>

        <div className="grid md:grid-cols-3 gap-6">
          {/* Left: Syllabus */}
          <div className="md:col-span-1">
            <div className="bg-white rounded-xl border border-gray-200 p-4 sticky top-6">
              <button
                onClick={() => setShowSyllabus(!showSyllabus)}
                className="w-full flex items-center justify-between text-sm font-semibold text-gray-700 mb-2"
              >
                课程大纲
                <span className="text-gray-400">{showSyllabus ? '▾' : '▸'}</span>
              </button>
              {showSyllabus && course.syllabus_content && (
                <div className="prose prose-sm max-w-none text-gray-600">
                  <ReactMarkdown>{stripFences(course.syllabus_content)}</ReactMarkdown>
                </div>
              )}
            </div>
          </div>

          {/* Right: Lesson List */}
          <div className="md:col-span-2 space-y-3">
            <h2 className="text-lg font-semibold text-gray-800 mb-2">课文列表</h2>

            {normalLessons.length === 0 ? (
              <p className="text-gray-400 text-center py-8">暂无课文</p>
            ) : (
              normalLessons.map((lesson) => (
                <button
                  key={lesson.id}
                  onClick={() => navigate(`/course/${courseId}/lesson/${lesson.number}`)}
                  className="w-full bg-white rounded-xl p-4 text-left border border-gray-200 hover:border-indigo-300 hover:shadow-sm transition-all"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-gray-800">
                      第 {String(lesson.number).padStart(2, '0')} 篇
                    </span>
                    <div className="flex items-center gap-2">
                      {lesson.is_evaluation && (
                        <span className="text-xs px-2 py-0.5 rounded-full bg-amber-100 text-amber-700">评估篇</span>
                      )}
                      <span className="text-xs text-gray-400">
                        {new Date(lesson.created_at).toLocaleDateString('zh-CN')}
                      </span>
                    </div>
                  </div>
                </button>
              ))
            )}

            {/* Summary section */}
            {summary && (
              <div className="bg-white rounded-xl border border-green-200 p-6 mt-4">
                <h3 className="text-lg font-semibold text-green-700 mb-3">课程总结</h3>
                <div className="prose prose-sm max-w-none">
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
