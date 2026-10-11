import React, { useState, useEffect, useRef } from 'react';
import AddIcon from '@mui/icons-material/Add';
import CheckIcon from '@mui/icons-material/Check';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import FolderOutlinedIcon from '@mui/icons-material/FolderOutlined';

interface Project {
  name: string;
  path: string;
  active: boolean;
}

interface ProjectSelectorProps {
  onProjectSwitch: () => void;
}

const ProjectSelector: React.FC<ProjectSelectorProps> = ({ onProjectSwitch }) => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isSwitching, setIsSwitching] = useState(false);
  const [isAdding, setIsAdding] = useState(false);
  const [newPath, setNewPath] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const activeProject = projects.find(p => p.active);

  const fetchProjects = async () => {
    try {
      const res = await fetch('/api/projects');
      if (res.ok) {
        const data = await res.json();
        setProjects(data);
      }
    } catch (e) {
      console.error('Failed to fetch projects', e);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSwitch = async (project: Project) => {
    if (project.active) {
      setIsOpen(false);
      return;
    }
    setIsSwitching(true);
    setIsOpen(false);
    try {
      const res = await fetch('/api/projects/switch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: project.path })
      });
      const data = await res.json();
      if (data.success) {
        await fetchProjects();
        onProjectSwitch();
      } else {
        alert(`Failed to switch project: ${data.error}`);
      }
    } catch (e) {
      console.error(e);
      alert('Network error while switching project.');
    } finally {
      setIsSwitching(false);
    }
  };

  const handleAddProject = async () => {
    if (!newPath.trim()) return;
    setIsAdding(true);
    try {
      const res = await fetch('/api/projects/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: newPath.trim(), run_synthesis: true })
      });
      const data = await res.json();
      if (data.success) {
        setShowAddModal(false);
        setNewPath('');
        alert(`Onboarding started! ${data.message}`);
        // Poll briefly to update the projects list
        setTimeout(fetchProjects, 3000);
      } else {
        alert(`Failed to add project: ${data.error}`);
      }
    } catch (e) {
      console.error(e);
      alert('Network error while adding project.');
    } finally {
      setIsAdding(false);
    }
  };

  return (
    <>
      <div className="project-selector" ref={dropdownRef}>
        <button
          id="project-selector-btn"
          className="project-selector-btn"
          onClick={() => setIsOpen(o => !o)}
          title="Switch project"
          disabled={isSwitching}
        >
          {isSwitching ? (
            <span className="spinner" />
          ) : (
            <FolderOutlinedIcon fontSize="inherit" />
          )}
          <span className="project-selector-name">
            {isSwitching ? 'Switching…' : (activeProject?.name ?? 'Select project')}
          </span>
          <ExpandMoreIcon fontSize="inherit" />
        </button>

        {isOpen && (
          <div className="project-dropdown">
            <div className="project-dropdown-header">Projects</div>
            {projects.length === 0 && (
              <div className="project-dropdown-empty">No projects registered</div>
            )}
            {projects.map(p => (
              <button
                key={p.path}
                className={`project-dropdown-item ${p.active ? 'active' : ''}`}
                onClick={() => handleSwitch(p)}
                title={p.path}
              >
                <span className="project-item-mark">{p.active && <CheckIcon fontSize="inherit" />}</span>
                <span className="project-item-name">{p.name}</span>
                <span className="project-item-path">{p.path.split('/').slice(-2).join('/')}</span>
              </button>
            ))}
            <div className="project-dropdown-divider" />
            <button
              className="project-dropdown-add"
              onClick={() => { setIsOpen(false); setShowAddModal(true); }}
            >
              <AddIcon fontSize="inherit" /> Add project
            </button>
          </div>
        )}
      </div>

      {/* Add Project Modal */}
      {showAddModal && (
        <div className="modal-overlay" onClick={() => setShowAddModal(false)}>
          <div className="modal-box" onClick={e => e.stopPropagation()}>
            <h3>Add Project</h3>
            <p style={{ fontSize: '0.85rem', opacity: 0.7, marginBottom: '1rem' }}>
              Enter the absolute path to a local project folder. The onboarding
              pipeline will auto-generate requirements and decorate existing tests.
            </p>
            <input
              id="add-project-path-input"
              type="text"
              className="modal-input"
              placeholder="/home/user/projects/my-app"
              value={newPath}
              onChange={e => setNewPath(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleAddProject()}
              autoFocus
            />
            <div className="modal-actions">
              <button className="btn btn-outline" onClick={() => setShowAddModal(false)}>
                Cancel
              </button>
              <button
                id="add-project-confirm-btn"
                className="btn btn-primary"
                onClick={handleAddProject}
                disabled={isAdding || !newPath.trim()}
              >
                {isAdding ? 'Onboarding…' : 'Onboard Project'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ProjectSelector;
