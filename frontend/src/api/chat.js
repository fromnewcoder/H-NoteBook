import api from './auth';

export const getMessages = async (notebookId) => {
  const response = await api.get(`/notebooks/${notebookId}/messages`);
  return response.data;
};

export const sendMessage = async (notebookId, content, selectedSourceIds) => {
  const response = await api.post(
    `/notebooks/${notebookId}/messages`,
    { content, selected_source_ids: selectedSourceIds },
    { responseType: 'stream' }
  );
  return response.data;
};
