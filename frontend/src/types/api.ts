/**
 * The engine responses PM Studio reads (backend/entrypoints/schemas.py).
 */

export interface RuleCardDTO {
  id: string;
  title: string;
  chapter?: string;
  card_type: 'LOGIC' | 'VIEW' | string;
  category?: string;
  target: string;
  description?: string;
  given_clause?: string;
  when_clause?: string;
  then_clause?: string;
  unless_clause?: string;
  is_active: boolean;
  status: 'PENDING' | 'IN_PROGRESS' | 'FULFILLED' | 'CONFLICT' | 'PAUSED' | 'REQUIRES_HUMAN_INTERVENTION' | string;
  derived_from_id?: string | null;
  test_status: SpecTestStatus;
  test_reason?: string | null;  // one line saying why the last run did not pass
}

/** The outcome of a spec's last test run: never run, proved, stopped before it could be judged, or judged and rejected. */
export type SpecTestStatus = 'not_run' | 'pass' | 'broken' | 'fail';

export interface LivingDeckDTO {
  chapters?: Record<string, RuleCardDTO[]>;
  logic_cards: {
    global: RuleCardDTO[];
    entities: Record<string, RuleCardDTO[]>;
  };
  view_cards: {
    global_theme: RuleCardDTO[];
    components: Record<string, RuleCardDTO[]>;
  };
  all_cards?: RuleCardDTO[];
}




