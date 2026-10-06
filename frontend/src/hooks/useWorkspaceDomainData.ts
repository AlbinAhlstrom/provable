/**
 * Universal Workspace Domain Data Hook.
 * Connects PM Studio frontend directly to the running Workspace FastAPI application on port 8001.
 * Provides unified CRUD, live polling, and domain exception extraction.
 */

import { useState, useEffect, useCallback } from 'react';

export function getEndpointSlug(aggregateName: string): string {
  const clean = aggregateName.trim().toLowerCase();
  if (clean.endsWith('y') && !clean.endsWith('ey') && !clean.endsWith('ay') && !clean.endsWith('oy')) {
    return clean.slice(0, -1) + 'ies';
  }
  if (clean.endsWith('s') || clean.endsWith('x') || clean.endsWith('z') || clean.endsWith('ch') || clean.endsWith('sh')) {
    return clean + 'es';
  }
  return clean + 's';
}

export const WORKSPACE_API_BASE = 'http://localhost:8001/api';

export async function fetchWorkspaceEntities(aggregateName: string): Promise<{ success: boolean; data: any[]; error?: string }> {
  const slug = getEndpointSlug(aggregateName);
  try {
    const res = await fetch(`${WORKSPACE_API_BASE}/${slug}`);
    if (res.ok) {
      const data = await res.json();
      return { success: true, data: Array.isArray(data) ? data : [] };
    }
    return { success: false, data: [], error: `HTTP ${res.status}: ${res.statusText}` };
  } catch (err: any) {
    return { success: false, data: [], error: err.message || 'Failed to connect to Workspace API (:8001)' };
  }
}

export async function createWorkspaceEntity(
  aggregateName: string,
  payload: Record<string, any>
): Promise<{ success: boolean; data?: any; error?: string; status?: number }> {
  const slug = getEndpointSlug(aggregateName);
  try {
    const res = await fetch(`${WORKSPACE_API_BASE}/${slug}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const body = await res.json().catch(() => ({}));
    if (res.ok) {
      return { success: true, data: body, status: res.status };
    }

    let errorDetail = 'Unknown validation error';
    if (typeof body.detail === 'string') {
      errorDetail = body.detail;
    } else if (Array.isArray(body.detail)) {
      errorDetail = body.detail.map((d: any) => `${d.loc?.join('.')} ${d.msg}`).join(', ');
    } else if (body.error) {
      errorDetail = body.error;
    }
    return { success: false, error: errorDetail, status: res.status };
  } catch (err: any) {
    return { success: false, error: err.message || 'Network error connecting to Workspace API (:8001)' };
  }
}

export function useWorkspaceDomainData(aggregateName: string, refreshIntervalMs = 0) {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!aggregateName) return;
    setLoading(true);
    setError(null);
    const result = await fetchWorkspaceEntities(aggregateName);
    if (result.success) {
      setData(result.data);
    } else {
      setError(result.error || 'Failed to load records');
    }
    setLoading(false);
  }, [aggregateName]);

  useEffect(() => {
    refresh();
    if (refreshIntervalMs > 0) {
      const interval = setInterval(refresh, refreshIntervalMs);
      return () => clearInterval(interval);
    }
  }, [refresh, refreshIntervalMs]);

  return { data, loading, error, refresh };
}
