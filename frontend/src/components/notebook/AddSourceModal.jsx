import { useState, useRef } from 'react';
import { X, Globe, Upload } from 'lucide-react';
import { createSourceURL, createSourceFile } from '../../api/sources';
import useNotebookStore from '../../store/notebookStore';

const sourceTypes = [
  { value: 'url', label: 'URL', icon: Globe },
  { value: 'txt', label: 'Text File', icon: Upload },
  { value: 'md', label: 'Markdown', icon: Upload },
  { value: 'docx', label: 'Word Document', icon: Upload },
];

export default function AddSourceModal({ notebookId, onClose }) {
  const [activeTab, setActiveTab] = useState('url');
  const [url, setUrl] = useState('');
  const [file, setFile] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);
  const { setSources } = useNotebookStore();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      if (activeTab === 'url') {
        if (!url.trim()) {
          setError('URL is required');
          setIsSubmitting(false);
          return;
        }
        await createSourceURL(notebookId, url.trim());
      } else {
        if (!file) {
          setError('File is required');
          setIsSubmitting(false);
          return;
        }
        await createSourceFile(notebookId, activeTab, file);
      }

      // Refresh sources list
      const { listSources } = await import('../../api/sources');
      const sources = await listSources(notebookId);
      setSources(sources);

      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to add source');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md mx-4">
        <div className="flex items-center justify-between p-4 border-b">
          <h3 className="font-semibold text-gray-800">Add Source</h3>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded">
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        <div className="flex border-b">
          {sourceTypes.map((type) => (
            <button
              key={type.value}
              onClick={() => setActiveTab(type.value)}
              className={`flex-1 py-2 text-sm font-medium transition ${
                activeTab === type.value
                  ? 'text-indigo-600 border-b-2 border-indigo-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              {type.label}
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-3 py-2 rounded-lg text-sm">
              {error}
            </div>
          )}

          {activeTab === 'url' ? (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                URL
              </label>
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com/article"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
              />
            </div>
          ) : (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                File
              </label>
              <input
                ref={fileInputRef}
                type="file"
                onChange={(e) => setFile(e.target.files[0])}
                accept={
                  activeTab === 'txt'
                    ? '.txt'
                    : activeTab === 'md'
                    ? '.md'
                    : '.docx'
                }
                className="hidden"
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="w-full border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-indigo-400 hover:bg-indigo-50/50 transition"
              >
                {file ? (
                  <span className="text-sm text-gray-700">{file.name}</span>
                ) : (
                  <>
                    <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                    <span className="text-sm text-gray-500">
                      Click to select a {activeTab.toUpperCase()} file
                    </span>
                  </>
                )}
              </button>
            </div>
          )}

          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2 px-4 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 py-2 px-4 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition disabled:opacity-50"
            >
              {isSubmitting ? 'Adding...' : 'Add Source'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
