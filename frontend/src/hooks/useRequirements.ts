import { useState, useEffect, useCallback } from 'react';
import { RequirementDTO, TestCaseDTO } from '../types/api';

export type { RequirementDTO, TestCaseDTO };
export type Requirement = RequirementDTO;
export type TestCase = TestCaseDTO;

export type Priority = 'High' | 'Med' | 'Low' | string;
export type RequirementType = 'Folder' | 'Requirement' | 'Task' | 'Bug' | 'Epic' | string;
export type KanbanStatus = 'Backlog' | 'In Progress' | 'Review' | 'Conflict' | 'Done' | string;
export type RequirementStatus = KanbanStatus;

export function normalizeRequirement(req: any): RequirementDTO {
  const parentId = req.parentId !== undefined ? req.parentId : (req.parent_id !== undefined ? req.parent_id : null);
  const assignedAgents = req.assignedAgents || req.assigned_agents || [];
  const proposedCode = req.proposedCode !== undefined ? req.proposedCode : (req.proposed_code !== undefined ? req.proposed_code : null);
  const tests = req.tests || req.test_cases || [];

  return {
    ...req,
    parentId,
    parent_id: parentId,
    assignedAgents,
    assigned_agents: assignedAgents,
    proposedCode,
    proposed_code: proposedCode,
    tests,
    test_cases: tests,
    dependencies: req.dependencies || []
  };
}

export function useRequirements() {
  const [requirements, setRequirements] = useState<RequirementDTO[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRequirements = useCallback(async () => {
    try {
      setLoading(true);
      const res = await fetch('http://localhost:8000/api/requirements');
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const data = await res.json();
      const normalizedData = Array.isArray(data) ? data.map(normalizeRequirement) : [];
      setRequirements(normalizedData);
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

  const createRequirement = async (reqData: Partial<RequirementDTO>) => {
    const res = await fetch('http://localhost:8000/api/requirements', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(reqData)
    });
    if (!res.ok) throw new Error('Failed to create requirement');
    await fetchRequirements();
  };

  const updateRequirement = async (id: string, updates: Partial<RequirementDTO>) => {
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
