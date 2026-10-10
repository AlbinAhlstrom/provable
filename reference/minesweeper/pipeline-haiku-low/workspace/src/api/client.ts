/**
 * Auto-Generated Type-Safe API Client for Workspace Domain API (:8001).
 * Generated deterministically from domain aggregates and Pydantic schemas.
 */

export interface Game {
  id: string;
  difficulty?: string;
  status?: string;
  started_at?: string;
  ended_at?: string;
  elapsed_seconds?: number;
  mine_count?: number;
  flag_count?: number;
  cells?: Array<{ id: string; row: number; column: number; has_mine: boolean; adjacent_mine_count: number; state: string }>;
  [key: string]: any;
}

export interface DifficultySetting {
  id: string;
  name: string;
  rows: number;
  columns: number;
  mine_count: number;
  [key: string]: any;
}

export async function fetchGameList(): Promise<Game[]> {
  const res = await fetch(`/api/games`);
  if (!res.ok) throw new Error(`Failed to fetch Game list: ${res.statusText}`);
  return res.json();
}

export async function getGame(id: string): Promise<Game> {
  const res = await fetch(`/api/games/${encodeURIComponent(id)}`);
  if (!res.ok) throw new Error(`Failed to fetch Game ${id}: ${res.statusText}`);
  return res.json();
}

export async function createGame(data: Partial<Game>): Promise<Game> {
  const res = await fetch(`/api/games`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Failed to create Game`);
  }
  return res.json();
}

export async function fetchDifficultySettingList(): Promise<DifficultySetting[]> {
  const res = await fetch(`/api/difficulty_settings`);
  if (!res.ok) throw new Error(`Failed to fetch DifficultySetting list: ${res.statusText}`);
  return res.json();
}

export async function getDifficultySetting(id: string): Promise<DifficultySetting> {
  const res = await fetch(`/api/difficulty_settings/${encodeURIComponent(id)}`);
  if (!res.ok) throw new Error(`Failed to fetch DifficultySetting ${id}: ${res.statusText}`);
  return res.json();
}

export async function createDifficultySetting(data: Partial<DifficultySetting>): Promise<DifficultySetting> {
  const res = await fetch(`/api/difficulty_settings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Failed to create DifficultySetting`);
  }
  return res.json();
}
