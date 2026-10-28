export type SeverityLevel = 'critical' | 'high' | 'medium' | 'low' | 'info';

export type FindingCategory =
  | 'security'
  | 'bug_risk'
  | 'error_handling'
  | 'maintainability'
  | 'test_insufficiency'
  | 'secret_leak';

export type DetectionSource =
  | 'deterministic'
  | 'bandit'
  | 'ast_check'
  | 'regex_secret'
  | 'llm_suggestion'
  | 'quality_linter';

export type ConfidenceLevel = 'deterministic' | 'high' | 'medium' | 'low';

export type ReviewStatus = 'QUEUED' | 'PROCESSING' | 'COMPLETED' | 'FAILED';

export interface Finding {
  id: number;
  review_job_id: number;
  file_path: string;
  line_start?: number | null;
  line_end?: number | null;
  severity: SeverityLevel;
  category: FindingCategory;
  title: string;
  message: string;
  evidence?: string | null;
  suggested_remediation?: string | null;
  detection_source: DetectionSource;
  confidence: ConfidenceLevel;
  rule_id: string;
  created_at: string;
  feedback_type?: 'helpful' | 'false_positive' | 'ignored' | null;
}

export interface SeverityCounts {
  critical: number;
  high: number;
  medium: number;
  low: number;
  info: number;
}

export interface ReviewJob {
  id: number;
  pull_request_id: number;
  commit_sha: string;
  idempotency_key: string;
  status: ReviewStatus;
  mode: string;
  total_files_analyzed: number;
  total_findings: number;
  summary: string;
  error_message?: string | null;
  execution_time_ms?: number | null;
  started_at?: string | null;
  completed_at?: string | null;
  created_at: string;
  updated_at: string;
  severity_counts?: SeverityCounts | null;
  findings?: Finding[] | null;
  repo_full_name?: string | null;
  pr_number?: number | null;
  pr_title?: string | null;
}

export interface Repository {
  id: number;
  owner: string;
  name: string;
  full_name: string;
  default_branch: string;
  is_private: boolean;
  html_url: string;
  created_at: string;
  updated_at: string;
  open_prs_count?: number;
  total_reviews_count?: number;
}

export interface ChangedHunk {
  old_start: number;
  old_length: number;
  new_start: number;
  new_length: number;
  header: string;
  lines: string[];
}

export interface ChangedFile {
  path: string;
  old_path?: string | null;
  change_type: string;
  additions: number;
  deletions: number;
  patch?: string | null;
  hunks: ChangedHunk[];
  is_binary: boolean;
}

export interface DiffSummary {
  total_files: number;
  total_additions: number;
  total_deletions: number;
  files: ChangedFile[];
}

export interface SystemSettings {
  project_name: string;
  version: string;
  environment: string;
  database_connected: boolean;
  database_dialect: string;
  github_token_configured: boolean;
  github_rate_limit_remaining?: number | null;
  github_webhook_configured: boolean;
  llm_provider: string;
  llm_configured: boolean;
  available_providers: string[];
  max_diff_files: number;
  max_diff_bytes: number;
}

export interface FeedbackSubmission {
  finding_id: number;
  feedback_type: 'helpful' | 'false_positive' | 'ignored';
  comment?: string;
}
