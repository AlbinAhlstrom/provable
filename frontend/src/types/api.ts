/**
 * TypeScript DTO Interfaces matching backend/entrypoints/schemas.py
 */

export interface TestCaseDTO {
  id?: string;
  requirement_id?: string;
  title?: string;
  name?: string;
  given_text?: string;
  when_text?: string;
  then_text?: string;
  given?: string;
  when?: string;
  then?: string;
  file_path?: string;
  last_result?: 'pass' | 'fail' | 'skip' | 'pending' | 'never_run' | string;
  status?: string;
  allure_id?: string;
  failure_message?: string;
  [key: string]: any;
}

export interface RequirementDTO {
  id: string;
  title: string;
  description: string;
  priority: string;
  status: string;
  layer?: 'PRESENTATION' | 'LOGIC' | 'INFRASTRUCTURE' | string;
  tests: TestCaseDTO[] | Record<string, any>[];
  assignedAgents: string[];
  proposedCode?: string | null;
  feedback?: string | null;
  type?: string | null;
  parentId?: string | null;
  dependencies?: string[];
  // Legacy / normalized alias compatibility properties
  parent_id?: string | null;
  assigned_agents?: string[];
  proposed_code?: string | null;
  created_at?: string;
  updated_at?: string;
  test_cases?: TestCaseDTO[];
}

export interface CreateRequirementPayloadDTO {
  title: string;
  description: string;
  parentId?: string | null;
}

export interface CreateFolderPayloadDTO {
  title: string;
  description?: string;
  parentId?: string | null;
}

export interface EditRequirementPayloadDTO {
  id: string;
  title: string;
  description: string;
  priority: string;
}

export interface ProjectSwitchPayloadDTO {
  path: string;
}

export interface ProjectAddPayloadDTO {
  path: string;
  run_synthesis?: boolean;
}

export interface ParamUpdateRequestDTO {
  param_key: string;
  value: string;
}

export interface FeatureToggleRequestDTO {
  feature_id: string;
  enabled: boolean;
}

export interface ApprovePayloadDTO {
  id: string;
  code?: string | null;
}

export interface RejectPayloadDTO {
  id: string;
  feedback: string;
}

export interface FeedbackPayloadDTO {
  id: string;
  feedback: string;
}

export interface ReportBugPayloadDTO {
  title: string;
  parentId: string;
  steps: string;
  expected: string;
  actual: string;
}

export interface SwitchBranchPayloadDTO {
  branch: string;
}

export interface DomainDiscoveryRequestDTO {
  business_pitch: string;
}

export interface DomainRefinementRequestDTO {
  current_schema: Record<string, any>;
  feedback: string;
}

export interface DomainSynthesisRequestDTO {
  domain_schema: Record<string, any>;
}

export interface KickstartAnalyzeRequestDTO {
  business_pitch: string;
}

export interface KickstartSynthesisRequestDTO {
  business_pitch?: string | null;
  pitch?: string | null;
  selected_blocks?: string[] | null;
  selected_block_ids?: string[] | null;
  requirements?: Record<string, any>[] | null;
  extracted_requirements?: Record<string, any>[] | null;
}

export interface ComponentAddRequestDTO {
  prompt: string;
  component_type?: string;
}

export interface ComponentDeleteRequestDTO {
  canonical_key: string;
}

export interface SubRequirementAddRequestDTO {
  parent_canonical_key: string;
  prompt: string;
}

export interface SubRequirementDeleteRequestDTO {
  parent_canonical_key: string;
  sub_id: string;
}

export interface PageDTO {
  id: string;
  name: string;
  route: string;
  icon?: string;
  is_home?: boolean;
}

export interface PageAddRequestDTO {
  name: string;
  route: string;
  icon?: string;
}

export interface TestSpecAddDTO {
  component_id: string;
  test_name: string;
  given_text?: string;
  when_text?: string;
  then_text?: string;
}

export interface EntityAttributeDTO {
  name: string;
  type: 'string' | 'number' | 'tags' | 'boolean' | string;
  required?: boolean;
  default_value?: any;
  display_mode?: 'visible' | 'tag_chips' | 'badge' | 'subtitle' | 'hidden';
}

export interface DomainEntitySchemaDTO {
  entity_name: string;
  canonical_key: string;
  attributes: EntityAttributeDTO[];
}

export interface DomainEntityDTO {
  name: string;
  description: string;
  attributes: Record<string, string>;
  seed_items: Record<string, any>[];
}

export interface DomainAggregateDTO {
  name: string;
  description: string;
  entity_name: string;
  canonical_key: string;
  icon?: string;
  attributes: Array<{
    name: string;
    type: string;
    required?: boolean;
    description?: string;
  }>;
  invariants?: string[];
  specs?: BusinessSpecItemDTO[];
}

export interface BusinessSpecItemDTO {
  spec_id: string;
  title: string;
  description: string;
  given_when_then: string;
  target_aggregate: string;
  spec_type?: 'ATTRIBUTE_EXPANSION' | 'DOMAIN_INVARIANT' | 'STATE_TRANSITION' | 'API_CONTRACT' | string;
  kind?: 'behavior' | 'presentation';
  is_mathematical_boundary?: boolean;
  priority: string;
  status: 'PENDING' | 'IN_PROGRESS' | 'FULFILLED' | 'REQUIRES_HUMAN_INTERVENTION' | string;
  tdd?: SpecTddSummaryDTO;
}

/** What kind of product the pitch asks for, decided before the domain model is designed. */
export interface ProductIntentDTO {
  product_type: string;
  audience: string;
  primary_goal: string;
  scope_summary: string;
  model_focus: string[];
  out_of_scope: string[];
  assumptions: string[];
}

export interface TddAttemptDTO {
  attempt: number;
  approved: boolean;
  reason?: string | null;
}

/** What the TDD loop did for a spec: the generated test (for human review) and every attempt's verdict. */
export interface SpecTddSummaryDTO {
  phase?: string | null;
  error?: string | null;
  test_source?: string | null;
  test_location?: string | null;
  red_attempts: TddAttemptDTO[];
  attempts: TddAttemptDTO[];
  rolled_back: boolean;
}

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




