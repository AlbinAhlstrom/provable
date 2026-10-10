// Typed client for the Minesweeper API. The server owns every rule; this file only
// names the endpoints and the shapes they return.

export type Status = 'ready' | 'playing' | 'won' | 'lost';
export type Difficulty = 'beginner' | 'intermediate' | 'expert' | 'custom';
export type Action = 'reveal' | 'flag' | 'chord';

/** Per cell: H hidden, F flag, 0-8 revealed; after a loss M mine, X exploded mine, W wrong flag. */
export type CellSymbol = 'H' | 'F' | 'M' | 'X' | 'W' | '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8';

export interface GameSummary {
  id: string;
  difficulty: Difficulty;
  rows: number;
  cols: number;
  mine_count: number;
  status: Status;
  mines_remaining: number;
  elapsed_seconds: number;
  created_at: number;
}

export interface Game extends GameSummary {
  /** One string per row, one CellSymbol per column. */
  board: string[];
}

export interface Preset {
  key: Exclude<Difficulty, 'custom'>;
  rows: number;
  cols: number;
  mines: number;
}

export interface Difficulties {
  presets: Preset[];
  custom: { min_side: number; max_rows: number; max_cols: number; first_area: number };
}

export interface DifficultyStats {
  played: number;
  won: number;
  best_seconds: number | null;
  win_rate: number;
}

export type Stats = Record<Difficulty, DifficultyStats>;

export interface NewGame {
  difficulty: Difficulty;
  rows?: number;
  cols?: number;
  mines?: number;
}

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
  }
}

async function request<T>(path: string, body?: unknown): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`/api${path}`, {
      method: body === undefined ? 'GET' : 'POST',
      headers: body === undefined ? undefined : { 'Content-Type': 'application/json' },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new ApiError(0, 'Cannot reach the game server. Is it running on port 8101?');
  }
  if (!response.ok) {
    let detail = `The server answered ${response.status}.`;
    try {
      const data: unknown = await response.json();
      if (data && typeof data === 'object' && 'detail' in data && typeof data.detail === 'string') {
        detail = data.detail;
      }
    } catch {
      // not JSON (for example the dev proxy with no backend behind it)
      if (response.status >= 500) detail = 'Cannot reach the game server. Is it running on port 8101?';
    }
    throw new ApiError(response.status, detail);
  }
  return (await response.json()) as T;
}

export const api = {
  difficulties: () => request<Difficulties>('/difficulties'),
  createGame: (config: NewGame) => request<Game>('/games', config),
  listGames: (limit = 50) => request<GameSummary[]>(`/games?limit=${limit}`),
  getGame: (id: string) => request<Game>(`/games/${encodeURIComponent(id)}`),
  act: (id: string, action: Action, row: number, col: number) =>
    request<Game>(`/games/${encodeURIComponent(id)}/${action}`, { row, col }),
  stats: () => request<Stats>('/stats'),
};
