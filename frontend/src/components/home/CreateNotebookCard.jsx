import { Plus } from 'lucide-react';
import useNotebookStore from '../../store/notebookStore';

export default function CreateNotebookCard({ onCreated }) {
  const { createNotebook, isLoading } = useNotebookStore();

  const handleCreate = async () => {
    const notebook = await createNotebook('Untitled Notebook');
    if (notebook && onCreated) {
      onCreated(notebook);
    }
  };

  return (
    <button
      onClick={handleCreate}
      disabled={isLoading}
      className="bg-white rounded-xl border-2 border-dashed border-gray-300 p-4 cursor-pointer hover:border-indigo-400 hover:bg-indigo-50/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex flex-col items-center justify-center min-h-[140px]"
    >
      {isLoading ? (
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600"></div>
      ) : (
        <>
          <div className="bg-indigo-100 p-2 rounded-full mb-2">
            <Plus className="w-5 h-5 text-indigo-600" />
          </div>
          <span className="text-sm font-medium text-gray-600">Create Notebook</span>
        </>
      )}
    </button>
  );
}
