import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import {
  getLesson, getAnnotations, createAnnotation,
  submitFeedback, generateNextLesson,
} from '../lib/api';
import { useAuth } from '../lib/AuthContext';

export default function LessonPage() {
  const { courseId, lessonNum } = useParams();
  const navigate = useNavigate();
  const { refreshUser } = useAuth();

  const [lesson, setLesson] = useState(null);
  const [annotations, setAnnotations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Feedback form
  const [feedbackContent, setFeedbackContent] = useState('');
  const [thoughtAnswers, setThoughtAnswers] = useState('');
  const [submittingFeedback, setSubmittingFeedback] = useState(false);
  const [feedbackSaved, setFeedbackSaved] = useState(false);

  // Annotation form
  const [showAnnotation, setShowAnnotation] = useState(false);
  const [selectedText, setSelectedText] = useState('');
  const [annotationComment, setAnnotationComment] = useState('');
  const [selectionRange, setSelectionRange] = useState({ start: 0, end: 0 });

  // Generating next lesson
  const [generating, setGenerating] = useState(false);
  const [streamContent, setStreamContent] = useState('');

  const contentRef = useRef(null);

  // Strip wrapping ```markdown fences from AI output
  const stripFences = (text) => {
    if (!text) return '';
    let t = text.trim();
    if (/^```(?:markdown|md)?\s*\n?/i.test(t)) {
      t = t.replace(/^```(?:markdown|md)?\s*\n?/i, '').replace(/\n?```\s*$/, '');
    }
    return t.trim();
  };

  useEffect(() => {
    setLoading(true);
    setError('');
    setFeedbackSaved(false);
    setStreamContent('');
    setGenerating(false);

    Promise.all([
      getLesson(courseId, lessonNum),
      getAnnotations(courseId, lessonNum),
    ])
      .then(([l, a]) => {
        setLesson(l);
        setAnnotations(a);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [courseId, lessonNum]);

  // Text selection for annotations
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
    // Submit feedback first if there's content
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

      refreshUser();

      if (finalData?.completed) {
        // Course completed — go back to course page to see summary
        navigate(`/course/${courseId}`);
      } else if (finalData?.lesson_number) {
        // Navigate to the new lesson
        navigate(`/course/${courseId}/lesson/${finalData.lesson_number}`);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setGenerating(false);
    }
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center text-gray-400">加载中...</div>;
  }

  if (error && !lesson) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4">
        <p className="text-red-500">{error}</p>
        <button onClick={() => navigate(`/course/${courseId}`)} className="text-indigo-600 hover:underline">
          返回课程
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
          <button
            onClick={() => navigate(`/course/${courseId}`)}
            className="text-gray-600 hover:text-gray-900 text-sm"
          >
            &larr; 返回课程
          </button>
          <span className="text-sm text-gray-500">
            第 {String(lessonNum).padStart(2, '0')} 篇
            {lesson?.is_evaluation && ' (评估篇)'}
          </span>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-6">
        {/* Lesson Content */}
        <div
          ref={contentRef}
          onMouseUp={handleTextSelect}
          className="bg-white rounded-xl border border-gray-200 p-6 md:p-8 mb-6"
        >
          <div className="prose prose-lg max-w-none">
            <ReactMarkdown>{stripFences(lesson?.content)}</ReactMarkdown>
          </div>
        </div>

        {/* Annotations */}
        {annotations.length > 0 && (
          <div className="bg-amber-50 rounded-xl border border-amber-200 p-4 mb-6">
            <h3 className="text-sm font-semibold text-amber-700 mb-3">我的批注</h3>
            <div className="space-y-2">
              {annotations.map((ann) => (
                <div key={ann.id} className="bg-white rounded-lg p-3 border border-amber-100">
                  <p className="text-xs text-gray-400 mb-1">原文：「{ann.original_text}」</p>
                  <p className="text-sm text-gray-700">{ann.comment}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Annotation popup */}
        {showAnnotation && (
          <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl p-6 max-w-md w-full shadow-xl">
              <h3 className="font-semibold text-gray-800 mb-2">添加批注</h3>
              <p className="text-sm text-gray-500 mb-3">选中文本：「{selectedText.slice(0, 100)}{selectedText.length > 100 ? '...' : ''}」</p>
              <textarea
                value={annotationComment}
                onChange={(e) => setAnnotationComment(e.target.value)}
                placeholder="写下你的困惑或想法... (例如: ???这里为什么用这个方法)"
                className="w-full border border-gray-300 rounded-lg p-3 text-sm resize-none h-24 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
                autoFocus
              />
              <div className="flex justify-end gap-2 mt-3">
                <button
                  onClick={() => { setShowAnnotation(false); setSelectedText(''); }}
                  className="px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900"
                >
                  取消
                </button>
                <button
                  onClick={handleSaveAnnotation}
                  disabled={!annotationComment.trim()}
                  className="px-4 py-1.5 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
                >
                  保存批注
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Feedback section */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">你的反馈</h3>
          <p className="text-sm text-gray-500 mb-3">
            写下你的问题、感悟、不理解的地方，或者你希望下一篇深入探讨的方向。
          </p>
          <textarea
            value={feedbackContent}
            onChange={(e) => { setFeedbackContent(e.target.value); setFeedbackSaved(false); }}
            placeholder="在这里写下你的反馈..."
            className="w-full border border-gray-300 rounded-lg p-3 text-sm resize-none h-32 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none mb-3"
          />

          <details className="mb-3">
            <summary className="text-sm text-gray-500 cursor-pointer hover:text-gray-700">思考题回答 (可选)</summary>
            <textarea
              value={thoughtAnswers}
              onChange={(e) => { setThoughtAnswers(e.target.value); setFeedbackSaved(false); }}
              placeholder="在这里写下你对思考题的回答..."
              className="w-full border border-gray-300 rounded-lg p-3 text-sm resize-none h-24 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none mt-2"
            />
          </details>

          <div className="flex items-center gap-3">
            <button
              onClick={handleSubmitFeedback}
              disabled={submittingFeedback}
              className="px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50"
            >
              {submittingFeedback ? '保存中...' : '保存反馈'}
            </button>
            {feedbackSaved && <span className="text-sm text-green-600">已保存</span>}
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="mb-4 bg-red-50 text-red-600 text-sm px-4 py-2 rounded-lg">{error}</div>
        )}

        {/* Generate next / streaming */}
        {generating ? (
          <div className="bg-white rounded-xl border border-indigo-200 p-6">
            <h3 className="text-sm font-semibold text-indigo-600 mb-3">正在生成下一篇课文...</h3>
            {streamContent ? (
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown>{stripFences(streamContent)}</ReactMarkdown>
              </div>
            ) : (
              <p className="text-gray-400">AI 正在思考中...</p>
            )}
          </div>
        ) : (
          <button
            onClick={handleReadDone}
            className="w-full py-3 bg-indigo-600 text-white rounded-xl text-lg font-medium hover:bg-indigo-700 transition-colors"
          >
            我读完了 &rarr; 生成下一篇
          </button>
        )}

        {/* Hint */}
        <p className="text-xs text-gray-400 text-center mt-3">
          提示：选中课文中的文字可以添加行内批注
        </p>
      </main>
    </div>
  );
}
