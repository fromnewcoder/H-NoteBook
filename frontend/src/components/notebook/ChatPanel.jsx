import { useState, useRef, useEffect } from 'react';
import { Send } from 'lucide-react';
import ChatMessage from './ChatMessage';
import Spinner from '../shared/Spinner';

export default function ChatPanel({ messages, onSendMessage, streaming, hasSources }) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || streaming) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full">
      <h2 className="font-semibold text-gray-800 mb-4">Chat</h2>

      {!hasSources ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <p className="text-gray-500 mb-2">No sources available</p>
            <p className="text-sm text-gray-400">
              Add sources to start chatting with your content
            </p>
          </div>
        </div>
      ) : messages.length === 0 ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <p className="text-gray-500 mb-2">Start a conversation</p>
            <p className="text-sm text-gray-400">
              Ask questions about your sources and get AI-powered answers
            </p>
          </div>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto space-y-4 mb-4 max-h-[calc(100vh-320px)]">
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}
          {streaming && (
            <div className="flex items-start gap-2">
              <div className="bg-gray-100 rounded-lg px-3 py-2">
                <Spinner size="small" />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      )}

      <form onSubmit={handleSubmit} className="mt-auto">
        <div className="flex gap-2">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              hasSources
                ? 'Ask a question about your sources...'
                : 'Add sources to start chatting...'
            }
            disabled={!hasSources || streaming}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none disabled:bg-gray-100 disabled:cursor-not-allowed"
            rows={2}
          />
          <button
            type="submit"
            disabled={!hasSources || !input.trim() || streaming}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed self-end"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </form>
    </div>
  );
}
