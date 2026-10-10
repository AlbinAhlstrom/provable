/** Generated from the BestTime aggregate; calls the domain API (:8001) through the Vite proxy. */

export interface BestTimeState {
  id: string;
  difficulty_id: string;
  game_id: string;
  best_seconds: number;
  achieved_at: string;
  [key: string]: any;
}

export interface ActionResponse {
  success: boolean;
  state: BestTimeState;
  message?: string;
}

const BASE_URL = '/api/best_times';

async function failure(res: Response, what: string): Promise<Error> {
  const body = await res.json().catch(() => ({}));
  return new Error(typeof body.detail === 'string' ? body.detail : `${what} failed (${res.status})`);
}

export async function listBestTime(): Promise<BestTimeState[]> {
  const res = await fetch(BASE_URL);
  if (!res.ok) throw await failure(res, 'Loading');
  return res.json();
}

export async function getBestTime(id: string): Promise<BestTimeState> {
  const res = await fetch(`${BASE_URL}/${encodeURIComponent(id)}`);
  if (!res.ok) throw await failure(res, 'Loading');
  return res.json();
}

export async function createBestTime(data: Partial<BestTimeState>): Promise<BestTimeState> {
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
