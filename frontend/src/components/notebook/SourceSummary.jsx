import { ArrowLeft, Globe, FileText, FileCode } from 'lucide-react';
import useNotebookStore from '../../store/notebookStore';

const sourceIcons = {
  url: Globe,
  txt: FileText,
  md: FileCode,
  docx: FileText,
};

export default function SourceSummary() {
  const { selectedSource, clearSelectedSource } = useNotebookStore();

  if (!selectedSource) return null;

  const Icon = sourceIcons[selectedSource.source_type] || FileText;

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center gap-2 mb-4">
        <button
          onClick={clearSelectedSource}
          className="p-1.5 hover:bg-gray-100 rounded-lg transition"
          title="Back to sources"
        >
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </button>
        <h2 className="font-semibold text-gray-800">Source Summary</h2>
      </div>

      <div className="flex-1 overflow-y-auto">
        <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg border border-gray-200 mb-4">
          <Icon className="w-5 h-5 text-gray-500 flex-shrink-0 mt-0.5" />
          <div className="min-w-0 flex-1">
            <p className="text-sm font-medium text-gray-800 break-words">
              {selectedSource.name}
            </p>
            <p className="text-xs text-gray-500 mt-0.5">
              {selectedSource.source_type.toUpperCase()} • {selectedSource.chunk_count} chunks
            </p>
          </div>
        </div>

        <div className="space-y-2">
          <h3 className="text-sm font-medium text-gray-700">Summary</h3>
          <div className="p-3 bg-white rounded-lg border border-gray-200">
            {selectedSource.summary ? (
              <p className="text-sm text-gray-700 whitespace-pre-wrap">
                {selectedSource.summary}
              </p>
            ) : (
              <p className="text-sm text-gray-400 italic">
                No summary available.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
