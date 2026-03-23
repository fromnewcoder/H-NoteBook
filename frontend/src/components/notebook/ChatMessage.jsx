import { User, Bot } from 'lucide-react';

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex items-start gap-2 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div
        className={`p-2 rounded-lg ${
          isUser ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-800'
        }`}
      >
        {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
      </div>
      <div
        className={`max-w-[80%] rounded-lg px-3 py-2 ${
          isUser ? 'bg-indigo-100 text-gray-800' : 'bg-gray-100 text-gray-800'
        }`}
      >
        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        {message.completed === false && (
          <span className="inline-block w-2 h-2 bg-gray-400 rounded-full ml-1 animate-pulse" />
        )}
      </div>
    </div>
  );
}
