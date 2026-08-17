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

export interface CheckoutPreviewPayloadDTO {
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

export interface DomainEntityDTO {
  name: string;
  description: string;
  attributes: Record<string, string>;
  seed_items: Record<string, any>[];
}

