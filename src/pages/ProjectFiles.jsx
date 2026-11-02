import { useState, useEffect } from 'react';
import { api } from '../utils/api';
import { useAuth } from '../context/AuthContext';
import { Folder, FolderOpen, AlertCircle, FileText, ChevronRight } from 'lucide-react';
import FolderExplorer from '../components/FolderExplorer';

const ProjectFiles = () => {
  const { user } = useAuth();
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchUserProjects();
  }, []);

  const fetchUserProjects = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await api.getProjects();
      setProjects(data);

      if (data && data.length > 0) {
        setSelectedProject(data[0]);
      }
    } catch (err) {
      setError(err.message || 'Failed to load assigned project files.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="card text-center" style={{ padding: '60px' }}>
        <div style={{ border: '3px solid var(--border-color)', borderTop: '3px solid var(--primary)', borderRadius: '50%', width: '32px', height: '32px', animation: 'spin 1s linear infinite', margin: '0 auto 12px' }}></div>
        <p className="text-muted">Loading project file repository...</p>
      </div>
    );
  }

  return (
    <div className="project-files-container flex flex-col gap-4">
      {/* Page Header Card */}
      <div className="card flex justify-between items-center" style={{ padding: '20px' }}>
        <div>
          <div className="flex items-center gap-2">
            <FolderOpen size={22} style={{ color: 'var(--primary)' }} />
            <h2 className="font-display" style={{ fontSize: '1.4rem', fontWeight: 700 }}>
              Project Files & Repository
            </h2>
          </div>
          <p className="text-muted" style={{ fontSize: '0.85rem', marginTop: '2px' }}>
            Access project folders (`folder_master`) and assets (`asset_master`) stored in MySQL database.
          </p>
        </div>

        {selectedProject && (
          <div className="flex items-center gap-2">
            <span className="badge badge-primary font-mono" style={{ fontSize: '0.85rem', padding: '6px 12px' }}>
              {selectedProject.projectCode}
            </span>
          </div>
        )}
      </div>

      {/* Main Folder Explorer Component */}
      <FolderExplorer 
        projects={projects} 
        selectedProject={selectedProject} 
        onSelectProject={(proj) => setSelectedProject(proj)} 
      />
    </div>
  );
};

export default ProjectFiles;
