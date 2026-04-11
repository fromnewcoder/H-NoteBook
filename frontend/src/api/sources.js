import api from './auth';

export const listSources = async (notebookId) => {
  const response = await api.get(`/notebooks/${notebookId}/sources`);
  return response.data;
};

export const createSourceURL = async (notebookId, url) => {
  const formData = new FormData();
  formData.append('source_type', 'url');
  formData.append('url', url);

  const response = await api.post(`/notebooks/${notebookId}/sources`, formData);
  return response.data;
};

export const createSourceFile = async (notebookId, sourceType, file) => {
  const formData = new FormData();
  formData.append('source_type', sourceType);
  formData.append('file', file);

  const response = await api.post(`/notebooks/${notebookId}/sources`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const deleteSource = async (notebookId, sourceId) => {
  await api.delete(`/notebooks/${notebookId}/sources/${sourceId}`);
};

export const getSourceStatus = async (notebookId, sourceId) => {
  const response = await api.get(`/notebooks/${notebookId}/sources/${sourceId}/status`);
  return response.data;
};
