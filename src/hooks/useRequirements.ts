import { useState, useEffect } from 'react';

export type Priority = 'High' | 'Med' | 'Low';
export type KanbanStatus = 'Backlog' | 'InProgress' | 'Review' | 'Conflict' | 'Done';

export interface Requirement {
  id: string;
  title: string;
  description: string;
  priority: Priority;
  status: KanbanStatus;
  type: 'Folder' | 'Epic' | 'Requirement' | 'Task' | 'Bug';
  parentId: string | null;
  dependencies?: string[];
  assignedAgents?: string[];
  jira_key?: string;
  jiraKey?: string;
  tests?: any[];
  feedback?: string;
}

export function useRequirements() {
  const [requirements, setRequirements] = useState<Requirement[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchReqs = async () => {
    try {
      const res = await fetch('/api/requirements');
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data)) {
          setRequirements(data);
          setLoading(false);
        }
      } else {
        setTimeout(fetchReqs, 1500);
      }
    } catch (e) {
      console.warn("Retrying requirements fetch (backend initializing)...", e);
      setTimeout(fetchReqs, 1500);
    }
  };

  useEffect(() => {
    fetchReqs();
    const interval = setInterval(fetchReqs, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleCreateReq = async (req: Requirement) => {
    const updated = [...requirements, req];
    setRequirements(updated);
    await fetch('/api/requirements', { 
      method: 'POST', 
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updated) 
    });
  };

  const handleUpdateReq = async (id: string, fields: Partial<Requirement>) => {
    const updated = requirements.map(r => r.id === id ? { ...r, ...fields } : r);
    setRequirements(updated);
    
    await fetch('/api/edit-requirement', { 
      method: 'POST', 
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id, ...fields }) 
    });
  };

  const handleDeleteReq = async (id: string) => {
    const getDescendantIds = (targetId: string, reqs: Requirement[]): Set<string> => {
      const ids = new Set<string>([targetId]);
      let sizeBefore: number;
      do {
        sizeBefore = ids.size;
        reqs.forEach(r => {
          if (r.parentId && ids.has(r.parentId)) {
            ids.add(r.id);
          }
        });
      } while (ids.size > sizeBefore);
      return ids;
    };
    
    const descendants = getDescendantIds(id, requirements);
    const updated = requirements.filter(r => !descendants.has(r.id));
    
    setRequirements(updated);
    
    await fetch('/api/requirements', { 
      method: 'POST', 
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updated) 
    });
  };

  return {
    requirements,
    loading,
    fetchReqs,
    handleCreateReq,
    handleUpdateReq,
    handleDeleteReq
  };
}
