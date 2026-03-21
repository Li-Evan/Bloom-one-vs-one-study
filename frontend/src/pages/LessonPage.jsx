import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import {
  getLesson, getLessons, getAnnotations, createAnnotation,
  submitFeedback, generateNextLesson,
} from '../lib/api';

const stripFences = (text) => {
  if (!text) return '';
  let t = text.trim();
  if (/^```(?:markdown|md)?\s*\n?/i.test(t)) {
    t = t.replace(/^```(?:markdown|md)?\s*\n?/i, '').replace(/\n?```\s*$/, '');
  }
  return t.trim();
};

export default function LessonPage() {
  const { courseId, lessonNum } = useParams();
  const navigate = useNavigate();

  const [lesson, setLesson] = useState(null);
  const [allLessons, setAllLessons] = useState([]);
  const [annotations, setAnnotations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [feedbackContent, setFeedbackContent] = useState('');
  const [thoughtAnswers, setThoughtAnswers] = useState('');
  const [submittingFeedback, setSubmittingFeedback] = useState(false);
  const [feedbackSaved, setFeedbackSaved] = useState(false);

  const [showAnnotation, setShowAnnotation] = useState(false);
  const [selectedText, setSelectedText] = useState('');
  const [annotationComment, setAnnotationComment] = useState('');
  const [selectionRange, setSelectionRange] = useState({ start: 0, end: 0 });

  const [generating, setGenerating] = useState(false);
  const [streamContent, setStreamContent] = useState('');

  const contentRef = useRef(null);

  useEffect(() => {
    setLoading(true);
    setError('');
    setFeedbackSaved(false);
    setStreamContent('');
    setGenerating(false);
    setFeedbackContent('');
    setThoughtAnswers('');

    Promise.all([
      getLesson(courseId, lessonNum),
      getAnnotations(courseId, lessonNum),
      getLessons(courseId),
    ])
      .then(([l, a, all]) => {
        setLesson(l);
        setAnnotations(a);
        setAllLessons(all.filter((x) => x.number > 0));
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [courseId, lessonNum]);

  const handleTextSelect = () => {
    const selection = window.getSelection();
    const text = selection?.toString().trim();
    if (text && text.length > 0 && contentRef.current?.contains(selection.anchorNode)) {
      setSelectedText(text);
      setSelectionRange({ start: 0, end: text.length });
      setShowAnnotation(true);
      setAnnotationComment('');
    }
  };

  const handleSaveAnnotation = async () => {
    if (!annotationComment.trim()) return;
    try {
      const ann = await createAnnotation(courseId, lessonNum, {
        position_start: selectionRange.start,
        position_end: selectionRange.end,
        original_text: selectedText,
        comment: annotationComment.trim(),
      });
      setAnnotations((prev) => [...prev, ann]);
      setShowAnnotation(false);
      setAnnotationComment('');
      setSelectedText('');
    } catch (err) {
      setError(err.message);
    }
  };

  const handleSubmitFeedback = async () => {
    setSubmittingFeedback(true);
    setError('');
    try {
      await submitFeedback(courseId, lessonNum, feedbackContent, thoughtAnswers.trim() || null);
      setFeedbackSaved(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmittingFeedback(false);
    }
  };

  const handleReadDone = async () => {
    if (feedbackContent.trim() && !feedbackSaved) {
      await handleSubmitFeedback();
    }
    setGenerating(true);
    setStreamContent('');
    setError('');
    try {
      let finalData = null;
      await generateNextLesson(
        courseId,
        (chunk) => setStreamContent((prev) => prev + chunk),
        (data) => { finalData = data; },
      );
      if (finalData?.completed) {
        navigate(`/course/${courseId}`);
      } else if (finalData?.lesson_number) {
        navigate(`/course/${courseId}/lesson/${finalData.lesson_number}`);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setGenerating(false);
    }
  };

  const currentNum = parseInt(lessonNum, 10);

  if (loading) {
    return (
      <div className="min-h-[100dvh] bg-stone-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 rounded-full border-2 border-stone-200 border-t-emerald-600 animate-spin mx-auto" />
          <p className="text-stone-400 text-sm mt-3">加载课文...</p>
        </div>
      </div>
    );
  }

  if (error && !lesson) {
    return (
      <div className="min-h-[100dvh] bg-stone-50 flex flex-col items-center justify-center gap-4">
        <p className="text-rose-500 text-sm">{error}</p>
        <button
          onClick={() => navigate(`/course/${courseId}`)}
          className="text-emerald-600 hover:text-emerald-700 text-sm font-medium transition-colors"
        >
          返回课程
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-[100dvh] bg-stone-50">
      {/* Header */}
      <header className="bg-stone-900 sticky top-0 z-10">
        <div className="max-w-[1200px] mx-auto px-6 py-3.5 flex items-center justify-between">
          <button
            onClick={() => navigate(`/course/${courseId}`)}
            className="text-stone-400 hover:text-white text-sm transition-colors flex items-center gap-1.5"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
            </svg>
            返回课程
          </button>
          <span className="text-xs text-stone-500 font-mono tabular-nums">
            {String(lessonNum).padStart(2, '0')}{lesson?.is_evaluation ? ' / EVAL' : ''}
          </span>
        </div>
      </header>

      <div className="max-w-[1200px] mx-auto px-6 py-10 flex gap-8">
        {/* Main content */}
        <main className="flex-1 min-w-0">
          {/* Lesson Content */}
          <article
            ref={contentRef}
            onMouseUp={handleTextSelect}
            className="bg-white rounded-2xl border border-stone-200/60 shadow-[0_1px_3px_rgba(0,0,0,0.04)] p-8 md:p-10 mb-8"
          >
            <div className="prose prose-stone prose-lg max-w-none">
              <ReactMarkdown>{stripFences(lesson?.content)}</ReactMarkdown>
            </div>
          </article>

          {/* Annotations */}
          {annotations.length > 0 && (
            <div className="bg-amber-50/50 rounded-xl border border-amber-200/40 p-5 mb-8">
              <h3 className="text-xs font-medium text-amber-700 uppercase tracking-wide mb-3">我的批注</h3>
              <div className="space-y-2">
                {annotations.map((ann) => (
                  <div key={ann.id} className="bg-white rounded-lg p-3 border border-amber-100/60">
                    <p className="text-xs text-stone-400 mb-1 leading-relaxed">
                      原文：{ann.original_text.length > 80 ? ann.original_text.slice(0, 80) + '...' : ann.original_text}
                    </p>
                    <p className="text-sm text-stone-700">{ann.comment}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Feedback section */}
          <div className="bg-white rounded-2xl border border-stone-200/60 p-6 md:p-8 mb-8">
            <h3 className="text-sm font-medium text-stone-800 mb-1">你的反馈</h3>
            <p className="text-xs text-stone-400 mb-5">
              写下你的问题、感悟、不理解的地方，或者你希望下一篇深入探讨的方向。
            </p>
            <textarea
              value={feedbackContent}
              onChange={(e) => { setFeedbackContent(e.target.value); setFeedbackSaved(false); }}
              placeholder="在这里写下你的反馈..."
              className="w-full border border-stone-200 rounded-lg p-3.5 text-sm resize-none h-32 transition-colors hover:border-stone-300 focus:border-emerald-600 outline-none mb-4"
            />
            <details className="mb-4">
              <summary className="text-xs text-stone-400 cursor-pointer hover:text-stone-600 transition-colors select-none">
                思考题回答（可选）
              </summary>
              <textarea
                value={thoughtAnswers}
                onChange={(e) => { setThoughtAnswers(e.target.value); setFeedbackSaved(false); }}
                placeholder="在这里写下你对思考题的回答..."
                className="w-full border border-stone-200 rounded-lg p-3.5 text-sm resize-none h-24 transition-colors hover:border-stone-300 focus:border-emerald-600 outline-none mt-3"
              />
            </details>
            <div className="flex items-center gap-3">
              <button
                onClick={handleSubmitFeedback}
                disabled={submittingFeedback}
                className="px-4 py-2 text-sm bg-stone-100 text-stone-600 rounded-lg hover:bg-stone-200 disabled:opacity-50 transition-all duration-200 cursor-pointer"
              >
                {submittingFeedback ? '保存中...' : '保存反馈'}
              </button>
              {feedbackSaved && (
                <span className="text-xs text-emerald-600 font-medium">已保存</span>
              )}
            </div>
          </div>

          {/* Error */}
          {error && (
            <div className="mb-6 bg-rose-50 text-rose-600 text-sm px-4 py-2.5 rounded-lg border border-rose-100">
              {error}
            </div>
          )}

          {/* Generate next / streaming */}
          {generating ? (
            <div className="bg-white rounded-2xl border border-emerald-200/40 p-6 md:p-8">
              <div className="flex items-center gap-2 mb-4">
                <div className="w-4 h-4 rounded-full border-2 border-stone-200 border-t-emerald-600 animate-spin" />
                <h3 className="text-xs font-medium text-emerald-700 uppercase tracking-wide">生成下一篇课文</h3>
              </div>
              {streamContent ? (
                <div className="prose prose-sm prose-stone max-w-none">
                  <ReactMarkdown>{stripFences(streamContent)}</ReactMarkdown>
                </div>
              ) : (
                <p className="text-stone-400 text-sm">AI 正在思考中...</p>
              )}
            </div>
          ) : (
            <button
              onClick={handleReadDone}
              className="w-full py-3.5 bg-stone-900 text-white rounded-xl text-sm font-medium hover:bg-stone-800 transition-all duration-200 cursor-pointer"
            >
              我读完了 — 生成下一篇
            </button>
          )}

          <p className="text-xs text-stone-300 text-center mt-4">
            提示：选中课文中的文字可以添加行内批注
          </p>
        </main>

        {/* Right sidebar — chapter nav */}
        <aside className="hidden lg:block w-48 shrink-0">
          <div className="sticky top-20">
            <h3 className="text-xs font-medium text-stone-400 uppercase tracking-wide mb-3">章节</h3>
            <nav className="space-y-0.5">
              {allLessons.map((l) => {
                const isActive = l.number === currentNum;
                return (
                  <button
                    key={l.id}
                    onClick={() => navigate(`/course/${courseId}/lesson/${l.number}`)}
                    className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-all duration-150 flex items-center gap-2.5 cursor-pointer ${
                      isActive
                        ? 'bg-stone-900 text-white'
                        : 'text-stone-500 hover:bg-stone-100 hover:text-stone-700'
                    }`}
                  >
                    <span className={`font-mono tabular-nums text-xs ${isActive ? 'text-stone-400' : 'text-stone-300'}`}>
                      {String(l.number).padStart(2, '0')}
                    </span>
                    <span>
                      第 {String(l.number).padStart(2, '0')} 篇
                    </span>
                    {l.is_evaluation && (
                      <span className={`text-[10px] ml-auto ${isActive ? 'text-amber-300' : 'text-amber-500'}`}>
                        评估
                      </span>
                    )}
                  </button>
                );
              })}
            </nav>

            {/* Quick actions */}
            <div className="mt-6 pt-6 border-t border-stone-100 space-y-2">
              <button
                onClick={() => navigate(`/course/${courseId}`)}
                className="w-full text-left px-3 py-2 rounded-lg text-xs text-stone-400 hover:bg-stone-100 hover:text-stone-600 transition-all cursor-pointer"
              >
                查看大纲
              </button>
              {annotations.length > 0 && (
                <div className="px-3 py-1">
                  <span className="text-[10px] text-stone-300">
                    {annotations.length} 条批注
                  </span>
                </div>
              )}
            </div>
          </div>
        </aside>
      </div>

      {/* Annotation popup */}
      {showAnnotation && (
        <div className="fixed inset-0 bg-stone-950/40 flex items-center justify-center z-50 p-6">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full shadow-[0_20px_40px_-15px_rgba(0,0,0,0.15)]">
            <h3 className="font-medium text-stone-800 text-sm mb-3">添加批注</h3>
            <p className="text-xs text-stone-400 mb-4 leading-relaxed">
              选中文本：{selectedText.length > 100 ? selectedText.slice(0, 100) + '...' : selectedText}
            </p>
            <textarea
              value={annotationComment}
              onChange={(e) => setAnnotationComment(e.target.value)}
              placeholder="写下你的困惑或想法..."
              className="w-full border border-stone-200 rounded-lg p-3 text-sm resize-none h-24 transition-colors hover:border-stone-300 focus:border-emerald-600 outline-none"
              autoFocus
            />
            <div className="flex justify-end gap-2 mt-4">
              <button
                onClick={() => { setShowAnnotation(false); setSelectedText(''); }}
                className="px-3 py-1.5 text-sm text-stone-500 hover:text-stone-700 transition-colors"
              >
                取消
              </button>
              <button
                onClick={handleSaveAnnotation}
                disabled={!annotationComment.trim()}
                className="px-4 py-1.5 text-sm bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-40 transition-all duration-200 cursor-pointer"
              >
                保存
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
