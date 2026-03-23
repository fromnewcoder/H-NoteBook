import api from './auth';

export const createExport = async (notebookId, format) => {
  const response = await api.post(`/notebooks/${notebookId}/exports`, { format });
  return response.data;
};

export const getExportStatus = async (notebookId, jobId) => {
  const response = await api.get(`/notebooks/${notebookId}/exports/${jobId}`);
  return response.data;
};

export const downloadExport = async (notebookId, jobId) => {
  const response = await api.get(`/notebooks/${notebookId}/exports/${jobId}/download`, {
    responseType: 'blob',
  });
  return response.data;
};
