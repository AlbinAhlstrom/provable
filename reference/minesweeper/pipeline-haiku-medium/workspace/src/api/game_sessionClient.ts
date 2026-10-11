/** Generated from the GameSession aggregate; calls the domain API (:8001) through the Vite proxy. */

export interface GameSessionState {
  id: string;
  difficulty_id: string;
  status?: string;
  rows: number;
  columns: number;
  mine_count: number;
  flag_count?: number;
  elapsed_seconds?: number;
  started_at?: string;
  ended_at?: string;
  cells?: Array<{ id: string; row: number; column: number; has_mine: boolean; adjacent_mine_count: number; state: string }>;
  [key: string]: any;
}

export interface ActionResponse {
  success: boolean;
  state: GameSessionState;
  message?: string;
}

const BASE_URL = '/api/game_sessions';

async function failure(res: Response, what: string): Promise<Error> {
  const body = await res.json().catch(() => ({}));
  return new Error(typeof body.detail === 'string' ? body.detail : `${what} failed (${res.status})`);
}

export async function listGameSession(): Promise<GameSessionState[]> {
  const res = await fetch(BASE_URL);
  if (!res.ok) throw await failure(res, 'Loading');
  return res.json();
}

export async function getGameSession(id: string): Promise<GameSessionState> {
  const res = await fetch(`${BASE_URL}/${encodeURIComponent(id)}`);
  if (!res.ok) throw await failure(res, 'Loading');
  return res.json();
}

export async function createGameSession(data: Partial<GameSessionState>): Promise<GameSessionState> {
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
