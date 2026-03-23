import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { LogOut } from 'lucide-react';
import PageShell from '../components/layout/PageShell';
import NotebookCard from '../components/home/NotebookCard';
import CreateNotebookCard from '../components/home/CreateNotebookCard';
import useNotebookStore from '../store/notebookStore';
import useAuthStore from '../store/authStore';

export default function HomePage() {
  const { notebooks, isLoading, listNotebooks } = useNotebookStore();
  const { logout } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    listNotebooks();
  }, []);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <PageShell>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-800">My Notebooks</h1>
        <button
          onClick={handleLogout}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-800 transition"
        >
          <LogOut className="w-5 h-5" />
          Logout
        </button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          <CreateNotebookCard onCreated={(nb) => navigate(`/notebooks/${nb.id}`)} />
          {notebooks.map((notebook) => (
            <NotebookCard
              key={notebook.id}
              notebook={notebook}
              onClick={() => navigate(`/notebooks/${notebook.id}`)}
            />
          ))}
        </div>
      )}

      {!isLoading && notebooks.length === 0 && (
        <div className="text-center py-16">
          <p className="text-gray-500 text-lg">No notebooks yet</p>
          <p className="text-gray-400 text-sm mt-1">Create your first notebook to get started</p>
        </div>
      )}
    </PageShell>
  );
}
