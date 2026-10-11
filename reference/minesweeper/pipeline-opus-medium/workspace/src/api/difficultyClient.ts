/** Generated from the Difficulty aggregate; calls the domain API (:8001) through the Vite proxy. */

export interface DifficultyState {
  id: string;
  name: string;
  width?: number;
  height?: number;
  mine_count?: number;
  is_standard?: boolean;
  display_order: number;
  [key: string]: any;
}

export interface ActionResponse {
  success: boolean;
  state: DifficultyState;
  message?: string;
}

const BASE_URL = '/api/difficulties';

async function failure(res: Response, what: string): Promise<Error> {
  const body = await res.json().catch(() => ({}));
  return new Error(typeof body.detail === 'string' ? body.detail : `${what} failed (${res.status})`);
}

export async function listDifficulty(): Promise<DifficultyState[]> {
  const res = await fetch(BASE_URL);
  if (!res.ok) throw await failure(res, 'Loading');
  return res.json();
}

export async function getDifficulty(id: string): Promise<DifficultyState> {
  const res = await fetch(`${BASE_URL}/${encodeURIComponent(id)}`);
  if (!res.ok) throw await failure(res, 'Loading');
  return res.json();
}

export async function createDifficulty(data: Partial<DifficultyState>): Promise<DifficultyState> {
  const res = await fetch(BASE_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw await failure(res, 'Saving');
  return res.json();
}

export async function sendAction(
  id: string,
  actionType: string,
  params: Record<string, unknown> = {}
): Promise<ActionResponse> {
  const res = await fetch(`${BASE_URL}/${encodeURIComponent(id)}/action`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action_type: actionType, params }),
  });
  if (!res.ok) throw await failure(res, 'The action');
  return res.json();
}
