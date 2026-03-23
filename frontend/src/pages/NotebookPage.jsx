import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import PageShell from '../components/layout/PageShell';
import SourcePanel from '../components/notebook/SourcePanel';
import ChatPanel from '../components/notebook/ChatPanel';
import ExportPanel from '../components/notebook/ExportPanel';
import useNotebookStore from '../store/notebookStore';
import { getNotebook, updateNotebook } from '../api/notebooks';
import { getMessages } from '../api/chat';
import { listSources } from '../api/sources';

export default function NotebookPage() {
  const { notebookId } = useParams();
  const navigate = useNavigate();
  const {
    currentNotebook,
    setCurrentNotebook,
    sources,
    setSources,
    selectedSourceIds,
    messages,
    setMessages,
    addMessage,
    appendToLastMessage,
    completeLastAssistantMessage,
  } = useNotebookStore();

  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [titleValue, setTitleValue] = useState('');
  const [streaming, setStreaming] = useState(false);
  const titleInputRef = useRef(null);

  useEffect(() => {
    const loadNotebook = async () => {
      try {
        const [nb, msgs, srcs] = await Promise.all([
          getNotebook(notebookId),
          getMessages(notebookId),
          listSources(notebookId),
        ]);
        setCurrentNotebook(nb);
        setTitleValue(nb.title);
        setMessages(msgs);
        setSources(srcs);
      } catch (err) {
        console.error('Failed to load notebook:', err);
        navigate('/');
      }
    };
    loadNotebook();
  }, [notebookId]);

  useEffect(() => {
    if (isEditingTitle && titleInputRef.current) {
      titleInputRef.current.focus();
    }
  }, [isEditingTitle]);

  const handleTitleSave = async () => {
    if (titleValue.trim() && titleValue !== currentNotebook?.title) {
      try {
        await updateNotebook(notebookId, titleValue.trim());
        setCurrentNotebook({ ...currentNotebook, title: titleValue.trim() });
      } catch (err) {
        console.error('Failed to update title:', err);
      }
    }
    setIsEditingTitle(false);
  };

  const handleSendMessage = async (content) => {
    // Add user message
    const userMsg = {
      id: Date.now().toString(),
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    };
    addMessage(userMsg);

    // Add placeholder assistant message
    const assistantMsg = {
      id: 'streaming',
      role: 'assistant',
      content: '',
      completed: false,
      created_at: new Date().toISOString(),
    };
    addMessage(assistantMsg);

    setStreaming(true);

    try {
      const response = await fetch(`/api/v1/notebooks/${notebookId}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          content,
          selected_source_ids: Array.from(selectedSourceIds),
        }),
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));
            if (data.type === 'token') {
              appendToLastMessage(data.content);
            } else if (data.type === 'done') {
              completeLastAssistantMessage(data.message_id);
            } else if (data.type === 'error') {
              appendToLastMessage(`\nError: ${data.content}`);
              completeLastAssistantMessage('error');
            }
          }
        }
      }
    } catch (err) {
      console.error('Chat error:', err);
      appendToLastMessage('\nError: Failed to get response');
      completeLastAssistantMessage('error');
    } finally {
      setStreaming(false);
    }
  };

  if (!currentNotebook) {
    return (
      <PageShell>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>
      </PageShell>
    );
  }

  return (
    <PageShell>
      <div className="flex items-center gap-4 mb-6">
        <button
          onClick={() => navigate('/')}
          className="p-2 hover:bg-gray-100 rounded-lg transition"
        >
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </button>

        {isEditingTitle ? (
          <input
            ref={titleInputRef}
            type="text"
            value={titleValue}
            onChange={(e) => setTitleValue(e.target.value)}
            onBlur={handleTitleSave}
            onKeyDown={(e) => e.key === 'Enter' && handleTitleSave()}
            className="text-2xl font-bold text-gray-800 border-b-2 border-indigo-500 outline-none px-1"
          />
        ) : (
          <h1
            className="text-2xl font-bold text-gray-800 cursor-pointer hover:text-indigo-600 transition"
            onClick={() => setIsEditingTitle(true)}
          >
            {currentNotebook.title}
          </h1>
        )}
      </div>

      <div className="grid grid-cols-12 gap-6 h-[calc(100vh-180px)]">
        <div className="col-span-3 bg-white rounded-xl shadow-sm p-4 overflow-y-auto">
          <SourcePanel notebookId={notebookId} sources={sources} />
        </div>

        <div className="col-span-6 bg-white rounded-xl shadow-sm p-4 flex flex-col">
          <ChatPanel
            messages={messages}
            onSendMessage={handleSendMessage}
            streaming={streaming}
            hasSources={sources.some((s) => s.status === 'ready')}
          />
        </div>

        <div className="col-span-3 bg-white rounded-xl shadow-sm p-4">
          <ExportPanel notebookId={notebookId} />
        </div>
      </div>
    </PageShell>
  );
}
