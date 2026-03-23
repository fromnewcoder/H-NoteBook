import { FileText, Clock } from 'lucide-react';

export default function NotebookCard({ notebook, onClick }) {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <div
      onClick={onClick}
      className="bg-white rounded-xl border border-gray-200 p-4 cursor-pointer hover:shadow-md hover:border-indigo-300 transition-all group"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="bg-indigo-50 p-2 rounded-lg group-hover:bg-indigo-100 transition">
          <FileText className="w-5 h-5 text-indigo-600" />
        </div>
      </div>
      <h3 className="font-semibold text-gray-800 mb-1 truncate">{notebook.title}</h3>
      <div className="flex items-center justify-between text-sm text-gray-500">
        <span>{notebook.source_count} sources</span>
        <div className="flex items-center gap-1">
          <Clock className="w-3 h-3" />
          {formatDate(notebook.updated_at)}
        </div>
      </div>
    </div>
  );
}
