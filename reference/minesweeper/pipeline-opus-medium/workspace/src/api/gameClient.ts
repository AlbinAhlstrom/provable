/** Generated from the Game aggregate; calls the domain API (:8001) through the Vite proxy. */

export interface GameState {
  id: string;
  difficulty_id: string;
  width: number;
  height: number;
  mine_count: number;
  status?: string;
  mines_laid?: boolean;
  flags_placed?: number;
  remaining_mines: number;
  elapsed_seconds?: number;
  started_at?: string;
  ended_at?: string;
  struck_cell_id?: string;
  created_at: string;
  cells?: Array<{ id: string; row: number; column: number; has_mine: boolean; adjacent_mine_count: number; state: string }>;
  [key: string]: any;
}

export interface ActionResponse {
  success: boolean;
  state: GameState;
  message?: string;
}

const BASE_URL = '/api/games';

async function failure(res: Response, what: string): Promise<Error> {
  const body = await res.json().catch(() => ({}));
  return new Error(typeof body.detail === 'string' ? body.detail : `${what} failed (${res.status})`);
}

export async function listGame(): Promise<GameState[]> {
  const res = await fetch(BASE_URL);
  if (!res.ok) throw await failure(res, 'Loading');
  return res.json();
}

export async function getGame(id: string): Promise<GameState> {
  const res = await fetch(`${BASE_URL}/${encodeURIComponent(id)}`);
  if (!res.ok) throw await failure(res, 'Loading');
  return res.json();
}

export async function createGame(data: Partial<GameState>): Promise<GameState> {
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
