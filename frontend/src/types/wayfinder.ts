export interface BddClause {
  given: string;
  when: string;
  then: string;
  unless?: string | null;
}

export interface BddPreset {
  id: string;
  label: string;
  bdd: BddClause;
  description?: string;
}

export type WayfinderTicketType = 'GRILL' | 'PROTOTYPE' | 'RESEARCH' | 'TASK';
export type WayfinderTicketStatus = 'LOCKED' | 'FRONTIER' | 'FOG';

export interface WayfinderTicket {
  id: string;
  title: string;
  ticket_type: WayfinderTicketType;
  status: WayfinderTicketStatus;
  target_aggregate: string;
  rationale: string;
  depends_on: string[];
  bdd_template?: BddClause | null;
  presets: BddPreset[];
  schema_preview?: Record<string, any> | null;
  resolved_bdd?: BddClause | null;
}

export interface WayfinderGraphState {
  pitch: string;
  brand_name: string;
  tickets: WayfinderTicket[];
  frontier: WayfinderTicket[];
  fog: WayfinderTicket[];
  locked: WayfinderTicket[];
  progress_pct: number;
  is_synthesis_ready: boolean;
}
