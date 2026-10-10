/** Generated from the DifficultySetting aggregate; calls the domain API (:8001) through the Vite proxy. */

export interface DifficultySettingState {
  id: string;
  name: string;
  rows: number;
  columns: number;
  mine_count: number;
  [key: string]: any;
}

export interface ActionResponse {
  success: boolean;
  state: DifficultySettingState;
  message?: string;
}

const BASE_URL = '/api/difficulty_settings';

async function failure(res: Response, what: string): Promise<Error> {
  const body = await res.json().catch(() => ({}));
  return new Error(typeof body.detail === 'string' ? body.detail : `${what} failed (${res.status})`);
}

export async function listDifficultySetting(): Promise<DifficultySettingState[]> {
  const res = await fetch(BASE_URL);
  if (!res.ok) throw await failure(res, 'Loading');
  return res.json();
}

export async function getDifficultySetting(id: string): Promise<DifficultySettingState> {
  const res = await fetch(`${BASE_URL}/${encodeURIComponent(id)}`);
  if (!res.ok) throw await failure(res, 'Loading');
  return res.json();
}

export async function createDifficultySetting(data: Partial<DifficultySettingState>): Promise<DifficultySettingState> {
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
