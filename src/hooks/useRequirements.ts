import { useState, useEffect, useCallback } from 'react';

export type Priority = 'High' | 'Med' | 'Low';
export type RequirementType = 'Folder' | 'Requirement' | 'Task' | 'Bug' | 'Epic';
export type KanbanStatus = 'Backlog' | 'In Progress' | 'Review' | 'Conflict' | 'Done';
export type RequirementStatus = KanbanStatus;

export interface TestCase {
  id: string;
  requirement_id: string;
  title: string;
  given_text?: string;
  when_text?: string;
  then_text?: string;
  file_path: string;
  last_result: 'pass' | 'fail' | 'skip' | 'pending' | 'never_run';
  allure_id?: string;
  failure_message?: string;
}

export interface Requirement {
  id: string;
  title: string;
  description: string;
  type: RequirementType;
  priority: Priority;
  status: RequirementStatus;
  parent_id: string | null;
  parentId?: string | null;
  jira_key?: string;
  sdoc_uid?: string;
  dependencies: string[];
  assigned_agents: string[];
  assignedAgents?: string[];
  proposed_code?: string;
  feedback?: string;
  created_at: string;
  updated_at: string;
  test_cases?: TestCase[];
  tests?: TestCase[];
}

export function useRequirements() {
  const [requirements, setRequirements] = useState<Requirement[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRequirements = useCallback(async () => {
    try {
      setLoading(true);
      const res = await fetch('http://localhost:8000/api/requirements');
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const data = await res.json();
      setRequirements(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch requirements');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRequirements();
  }, [fetchRequirements]);

  const createRequirement = async (reqData: Partial<Requirement>) => {
    const res = await fetch('http://localhost:8000/api/requirements', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(reqData)
    });
    if (!res.ok) throw new Error('Failed to create requirement');
    await fetchRequirements();
  };

  const updateRequirement = async (id: string, updates: Partial<Requirement>) => {
    const res = await fetch(`http://localhost:8000/api/requirements/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates)
    });
    if (!res.ok) throw new Error('Failed to update requirement');
    await fetchRequirements();
  };

  const deleteRequirement = async (id: string) => {
    const res = await fetch(`http://localhost:8000/api/requirements/${id}`, {
      method: 'DELETE'
    });
    if (!res.ok) throw new Error('Failed to delete requirement');
    await fetchRequirements();
  };

  const generateTestCase = async (id: string) => {
    const res = await fetch(`http://localhost:8000/api/requirements/${id}/generate-test`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to generate test case');
    await fetchRequirements();
  };

  const triggerAgent = async (id: string) => {
    const res = await fetch(`http://localhost:8000/api/requirements/${id}/run-agent`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to trigger agent');
    await fetchRequirements();
  };

  const approveMerge = async (id: string) => {
    const res = await fetch(`http://localhost:8000/api/requirements/${id}/merge`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to approve merge');
    await fetchRequirements();
  };

  const rejectSubmission = async (id: string, feedback: string) => {
    const res = await fetch(`http://localhost:8000/api/requirements/${id}/reject`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ feedback })
    });
    if (!res.ok) throw new Error('Failed to reject submission');
    await fetchRequirements();
  };

  return {
    requirements,
    loading,
    error,
    fetchRequirements,
    createRequirement,
    updateRequirement,
    deleteRequirement,
    generateTestCase,
    triggerAgent,
    approveMerge,
    rejectSubmission
  };
}
