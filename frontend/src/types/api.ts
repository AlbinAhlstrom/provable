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
  page_test?: PageTestDTO | null;
}

/** The last run of a rule's page test: the test itself, what it showed when it did not pass, and when it ran. */
export interface PageTestDTO {
  source?: string | null;
  evidence?: string | null;
  ran_at?: string | null;
}

/** The outcome of a rule's page test: never run, every assertion held, the test could not judge, or one did not hold. */
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




