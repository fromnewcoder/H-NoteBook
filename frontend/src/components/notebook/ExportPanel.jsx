import { useState } from 'react';
import { FileText, Network, Presentation, Table, Download } from 'lucide-react';
import { createExport, getExportStatus, downloadExport } from '../../api/exports';
import StatusBadge from '../shared/StatusBadge';

const exportFormats = [
  { value: 'pdf', label: 'Summary PDF', icon: FileText },
  { value: 'mind_map', label: 'Mind Map', icon: Network },
  { value: 'docx', label: 'Word', icon: FileText },
  { value: 'pptx', label: 'PowerPoint', icon: Presentation },
  { value: 'xlsx', label: 'Excel', icon: Table },
];

export default function ExportPanel({ notebookId }) {
  const [exportingFormat, setExportingFormat] = useState(null);
  const [exportJob, setExportJob] = useState(null);
  const [error, setError] = useState(null);

  const handleExport = async (format) => {
    setError(null);
    setExportingFormat(format);
    setExportJob(null);

    try {
      const job = await createExport(notebookId, format);
      setExportJob(job);

      // Poll for completion
      const pollInterval = setInterval(async () => {
        try {
          const status = await getExportStatus(notebookId, job.job_id);
          setExportJob(status);

          if (status.status === 'done') {
            clearInterval(pollInterval);
            // Trigger download
            const blob = await downloadExport(notebookId, job.job_id);
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `export_${job.job_id}.${format}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            setExportingFormat(null);
          } else if (status.status === 'failed') {
            clearInterval(pollInterval);
            setError(status.error_message || 'Export failed');
            setExportingFormat(null);
          }
        } catch (err) {
          clearInterval(pollInterval);
          setError('Failed to get export status');
          setExportingFormat(null);
        }
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create export');
      setExportingFormat(null);
    }
  };

  return (
    <div className="h-full flex flex-col">
      <h2 className="font-semibold text-gray-800 mb-4">Export</h2>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-600 px-3 py-2 rounded-lg text-sm mb-4">
          {error}
        </div>
      )}

      {exportJob && (
        <div className="bg-gray-50 rounded-lg p-3 mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Export Status</span>
            <StatusBadge status={exportJob.status} />
          </div>
          <p className="text-xs text-gray-500">
            Format: {exportJob.format.toUpperCase()}
          </p>
        </div>
      )}

      <div className="space-y-2">
        {exportFormats.map((format) => (
          <button
            key={format.value}
            onClick={() => handleExport(format.value)}
            disabled={exportingFormat !== null}
            className="w-full flex items-center gap-3 px-3 py-2 border border-gray-200 rounded-lg hover:bg-indigo-50 hover:border-indigo-300 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <format.icon className="w-5 h-5 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">{format.label}</span>
            {exportingFormat === format.value && (
              <div className="ml-auto">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-indigo-600"></div>
              </div>
            )}
          </button>
        ))}
      </div>

      <div className="mt-auto pt-4">
        <p className="text-xs text-gray-400 text-center">
          Exports are processed in the background
        </p>
      </div>
    </div>
  );
}
