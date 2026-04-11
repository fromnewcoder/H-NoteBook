import { useState, useEffect } from 'react';
import { Globe, FileText, FileCode, Trash2, Check } from 'lucide-react';
import StatusBadge from '../shared/StatusBadge';
import { deleteSource, getSourceStatus } from '../../api/sources';
import useNotebookStore from '../../store/notebookStore';

const sourceIcons = {
  url: Globe,
  txt: FileText,
  md: FileCode,
  docx: FileText,
};

export default function SourceItem({ source, notebookId, isSelected, onToggle, onViewSummary }) {
  const [isDeleting, setIsDeleting] = useState(false);
  const { setSources } = useNotebookStore();

  useEffect(() => {
    if (source.status === 'processing') {
      const pollStatus = async () => {
        try {
          const status = await getSourceStatus(notebookId, source.id);
          if (status.status === 'ready' || status.status === 'failed') {
            // Refresh sources list to update status
            const { listSources } = await import('../../api/sources');
            const sources = await listSources(notebookId);
            setSources(sources);
          } else {
            setTimeout(pollStatus, 2000);
          }
        } catch (err) {
          console.error('Error polling source status:', err);
        }
      };
      pollStatus();
    }
  }, [source.status, notebookId, source.id]);

  const handleDelete = async () => {
    if (isDeleting) return;
    setIsDeleting(true);
    try {
      await deleteSource(notebookId, source.id);
      const { listSources } = await import('../../api/sources');
      const sources = await listSources(notebookId);
      setSources(sources);
    } catch (err) {
      console.error('Error deleting source:', err);
    } finally {
      setIsDeleting(false);
    }
  };

  const Icon = sourceIcons[source.source_type] || FileText;
  const canSelect = source.status === 'ready';

  return (
    <div
      onClick={canSelect ? onViewSummary : undefined}
      className={`flex items-center gap-2 p-2 rounded-lg border transition cursor-pointer ${
        canSelect
          ? isSelected
            ? 'border-indigo-400 bg-indigo-50'
            : 'border-gray-200 hover:border-gray-300'
          : 'border-gray-200 opacity-60 cursor-default'
      }`}
    >
      <button
        onClick={(e) => { e.stopPropagation(); onToggle(); }}
        disabled={!canSelect}
        className={`w-5 h-5 rounded border flex items-center justify-center transition ${
          isSelected
            ? 'bg-indigo-600 border-indigo-600 text-white'
            : 'border-gray-300 hover:border-indigo-400'
        } disabled:cursor-not-allowed`}
      >
        {isSelected && <Check className="w-3 h-3" />}
      </button>

      <Icon className="w-4 h-4 text-gray-500 flex-shrink-0" />

      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-800 truncate" title={source.name}>
          {source.name}
        </p>
        <div className="flex items-center gap-2 mt-0.5">
          <StatusBadge status={source.status} />
        </div>
      </div>

      <button
        onClick={(e) => { e.stopPropagation(); handleDelete(); }}
        disabled={isDeleting}
        className="p-1 hover:bg-red-50 rounded transition disabled:opacity-50"
        title="Delete source"
      >
        <Trash2 className="w-4 h-4 text-red-500" />
      </button>
    </div>
  );
}
