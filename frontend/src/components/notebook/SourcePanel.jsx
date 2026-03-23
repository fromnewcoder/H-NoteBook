import { useState } from 'react';
import { Plus } from 'lucide-react';
import SourceItem from './SourceItem';
import AddSourceModal from './AddSourceModal';
import useNotebookStore from '../../store/notebookStore';

export default function SourcePanel({ notebookId, sources }) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { selectedSourceIds, toggleSourceSelection } = useNotebookStore();

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-semibold text-gray-800">Sources</h2>
        <button
          onClick={() => setIsModalOpen(true)}
          className="p-1.5 hover:bg-gray-100 rounded-lg transition"
          title="Add Source"
        >
          <Plus className="w-5 h-5 text-gray-600" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto space-y-2">
        {sources.length === 0 ? (
          <p className="text-sm text-gray-500 text-center py-8">
            No sources yet. Add a source to start chatting.
          </p>
        ) : (
          sources.map((source) => (
            <SourceItem
              key={source.id}
              source={source}
              notebookId={notebookId}
              isSelected={selectedSourceIds.has(source.id)}
              onToggle={() => toggleSourceSelection(source.id)}
            />
          ))
        )}
      </div>

      {isModalOpen && (
        <AddSourceModal notebookId={notebookId} onClose={() => setIsModalOpen(false)} />
      )}
    </div>
  );
}
