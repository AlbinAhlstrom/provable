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
  cause?: RuleCauseDTO | null;  // what a fix found when it left the rule red
}

/** Where a fix found the fault of a red rule: on the page, in what the app does, in rules that cannot hold
 *  together (named by title), or in the test. */
export interface RuleCauseDTO {
  fault: 'page' | 'logic' | 'rules' | 'test';
  why: string;      // one sentence in everyday words
  rules: string[];
}

/** What a fix answered (backend/service_layer/rule_tests.py). */
export interface RuleFixDTO extends Partial<RuleCauseDTO> {
  success: boolean;
  status: string;
  reason?: string | null;
  files?: string[];
}

/** The outcome of a rule's page test: never run, every assertion held, the test could not judge, or one did not hold. */
export type SpecTestStatus = 'not_run' | 'pass' | 'broken' | 'fail';

/** A planned change to the built app, before it is built (backend/service_layer/change_tickets.py). */
export interface ChangeCardDTO {
  request: string;
  title: string;
  understood: string;                          // the request as it was read: one sentence in everyday words
  // the rules the change would add: the feature of the app each is filed under, the sentence, and its Given, When
  // and Then apart (empty where it has none)
  rules: { title: string; feature: string; plain: string; given: string; when: string; then: string }[];
  adds: { kind: string; name: string }[];      // what else it adds to the app, by name
  stays_green: number;                         // the rules the app already has, checked after the build
  problem: string | null;                      // why the app cannot take the change as planned
}

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




