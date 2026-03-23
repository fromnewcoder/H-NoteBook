import { create } from 'zustand';
import { login as apiLogin, logout as apiLogout } from '../api/auth';

const useAuthStore = create((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  login: async (username, password) => {
    set({ isLoading: true, error: null });
    try {
      const data = await apiLogin(username, password);
      localStorage.setItem('access_token', data.access_token);
      set({ user: { username }, isAuthenticated: true, isLoading: false });
      return true;
    } catch (err) {
      set({ error: err.response?.data?.detail || 'Login failed', isLoading: false });
      return false;
    }
  },

  logout: async () => {
    try {
      await apiLogout();
    } catch (err) {
      // Ignore logout errors
    }
    localStorage.removeItem('access_token');
    set({ user: null, isAuthenticated: false });
  },

  checkAuth: () => {
    const token = localStorage.getItem('access_token');
    if (token) {
      set({ isAuthenticated: true, user: { username: 'admin' } });
    }
  },

  clearError: () => set({ error: null }),
}));

export default useAuthStore;
