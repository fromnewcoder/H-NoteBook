import { create } from 'zustand';
import {
  listNotebooks as apiListNotebooks,
  createNotebook as apiCreateNotebook,
  deleteNotebook as apiDeleteNotebook,
} from '../api/notebooks';

const useNotebookStore = create((set, get) => ({
  notebooks: [],
  currentNotebook: null,
  sources: [],
  selectedSourceIds: new Set(),
  selectedSource: null,
  messages: [],
  isLoading: false,
  error: null,

  setCurrentNotebook: (notebook) => set({ currentNotebook: notebook }),

  setSources: (sources) => {
    const selected = new Set(sources.filter(s => s.status === 'ready').map(s => s.id));
    set({ sources, selectedSourceIds: selected });
  },

  toggleSourceSelection: (sourceId) => {
    const { selectedSourceIds } = get();
    const newSelection = new Set(selectedSourceIds);
    if (newSelection.has(sourceId)) {
      newSelection.delete(sourceId);
    } else {
      newSelection.add(sourceId);
    }
    set({ selectedSourceIds: newSelection });
  },

  setMessages: (messages) => set({ messages }),

  setSelectedSource: (source) => set({ selectedSource: source }),

  clearSelectedSource: () => set({ selectedSource: null }),

  addMessage: (message) => set((state) => ({
    messages: [...state.messages, message],
  })),

  appendToLastMessage: (content) => set((state) => {
    const messages = [...state.messages];
    if (messages.length > 0 && messages[messages.length - 1].role === 'assistant' && !messages[messages.length - 1].completed) {
      messages[messages.length - 1].content += content;
    }
    return { messages };
  }),

  completeLastAssistantMessage: (messageId) => set((state) => {
    const messages = [...state.messages];
    if (messages.length > 0 && messages[messages.length - 1].role === 'assistant') {
      messages[messages.length - 1].completed = true;
      messages[messages.length - 1].id = messageId;
    }
    return { messages };
  }),

  listNotebooks: async () => {
    set({ isLoading: true, error: null });
    try {
      const notebooks = await apiListNotebooks();
      set({ notebooks, isLoading: false });
    } catch (err) {
      set({ error: err.response?.data?.detail || 'Failed to load notebooks', isLoading: false });
    }
  },

  createNotebook: async (title = 'Untitled Notebook') => {
    set({ isLoading: true, error: null });
    try {
      const notebook = await apiCreateNotebook(title);
      set((state) => ({
        notebooks: [notebook, ...state.notebooks],
        isLoading: false,
      }));
      return notebook;
    } catch (err) {
      set({ error: err.response?.data?.detail || 'Failed to create notebook', isLoading: false });
      return null;
    }
  },

  deleteNotebook: async (notebookId) => {
    try {
      await apiDeleteNotebook(notebookId);
      set((state) => ({
        notebooks: state.notebooks.filter((nb) => nb.id !== notebookId),
        currentNotebook: state.currentNotebook?.id === notebookId ? null : state.currentNotebook,
      }));
    } catch (err) {
      set({ error: err.response?.data?.detail || 'Failed to delete notebook' });
    }
  },

  clearError: () => set({ error: null }),
}));

export default useNotebookStore;
