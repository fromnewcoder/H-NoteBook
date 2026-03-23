import api from './auth';

export const listNotebooks = async () => {
  const response = await api.get('/notebooks');
  return response.data;
};

export const createNotebook = async (title = 'Untitled Notebook') => {
  const response = await api.post('/notebooks', { title });
  return response.data;
};

export const getNotebook = async (notebookId) => {
  const response = await api.get(`/notebooks/${notebookId}`);
  return response.data;
};

export const updateNotebook = async (notebookId, title) => {
  const response = await api.patch(`/notebooks/${notebookId}`, { title });
  return response.data;
};

export const deleteNotebook = async (notebookId) => {
  await api.delete(`/notebooks/${notebookId}`);
};
