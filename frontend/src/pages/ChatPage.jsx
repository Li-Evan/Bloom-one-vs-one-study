import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getMessages, sendMessage } from '../lib/api';
import { useAuth } from '../lib/AuthContext';
import ReactMarkdown from 'react-markdown';

export default function ChatPage() {
  const { courseId } = useParams();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [streaming, setStreaming] = useState(false);
  const [streamContent, setStreamContent] = useState('');
  const [error, setError] = useState('');
  const messagesEndRef = useRef(null);
  const navigate = useNavigate();
  const { refreshUser } = useAuth();

  useEffect(() => {
    getMessages(courseId).then(setMessages).catch(() => navigate('/'));
  }, [courseId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamContent]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || streaming) return;

    const userMsg = input.trim();
    setInput('');
    setError('');
    setMessages((prev) => [...prev, { role: 'user', content: userMsg, id: Date.now() }]);
    setStreaming(true);
    setStreamContent('');

    try {
      let accumulated = '';
      await sendMessage(courseId, userMsg, (chunk) => {
        accumulated += chunk;
        setStreamContent(accumulated);
      });

      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: accumulated, id: Date.now() + 1 },
      ]);
      setStreamContent('');
      refreshUser();
    } catch (err) {
      setError(err.message);
    } finally {
      setStreaming(false);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shrink-0">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
          <button onClick={() => navigate('/')} className="text-gray-600 hover:text-gray-900 text-sm">
            &larr; 返回课程列表
          </button>
          <span className="text-sm text-gray-500">课程 #{courseId}</span>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-4 py-6 space-y-4">
          {messages.length === 0 && !streaming && (
            <div className="text-center py-20">
              <p className="text-gray-400 text-lg mb-2">开始你的学习之旅</p>
              <p className="text-gray-400 text-sm">
                告诉导师你想学什么，例如：「我想学习博弈论的基础概念」
              </p>
            </div>
          )}

          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                  msg.role === 'user'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-white border border-gray-200 text-gray-800'
                }`}
              >
                {msg.role === 'user' ? (
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                ) : (
                  <div className="prose prose-sm max-w-none">
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>
                )}
              </div>
            </div>
          ))}

          {streaming && streamContent && (
            <div className="flex justify-start">
              <div className="max-w-[80%] rounded-2xl px-4 py-3 bg-white border border-gray-200 text-gray-800">
                <div className="prose prose-sm max-w-none">
                  <ReactMarkdown>{streamContent}</ReactMarkdown>
                </div>
              </div>
            </div>
          )}

          {streaming && !streamContent && (
            <div className="flex justify-start">
              <div className="rounded-2xl px-4 py-3 bg-white border border-gray-200 text-gray-400">
                思考中...
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 text-red-600 text-sm px-4 py-2 text-center">{error}</div>
      )}

      {/* Input */}
      <div className="bg-white border-t border-gray-200 shrink-0">
        <form onSubmit={handleSend} className="max-w-4xl mx-auto px-4 py-3 flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="输入你的问题或回答..."
            disabled={streaming}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={streaming || !input.trim()}
            className="bg-indigo-600 text-white px-6 py-2 rounded-xl hover:bg-indigo-700 disabled:opacity-50 transition-colors"
          >
            发送
          </button>
        </form>
      </div>
    </div>
  );
}
