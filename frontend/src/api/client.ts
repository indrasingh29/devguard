import type {
  Repository,
  ReviewJob,
  Finding,
  DiffSummary,
  SystemSettings,
  FeedbackSubmission,
} from '../types';

const RAW_API_URL = import.meta.env.VITE_API_URL || '';
const API_BASE = RAW_API_URL ? `${RAW_API_URL.replace(/\/$/, '')}/api/v1` : '/api/v1';

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorDetail = 'An unexpected server error occurred';
    try {
      const data = await res.json();
      errorDetail = data.detail || data.error || errorDetail;
    } catch {
      errorDetail = res.statusText || errorDetail;
    }
    throw new Error(errorDetail);
  }
  return res.json();
}

export const api = {
  // Repositories
  async getRepositories(): Promise<Repository[]> {
    const res = await fetch(`${API_BASE}/repositories`);
    return handleResponse<Repository[]>(res);
  },

  async getRepository(id: number): Promise<Repository> {
    const res = await fetch(`${API_BASE}/repositories/${id}`);
    return handleResponse<Repository>(res);
  },

  async connectRepository(repoInput: string): Promise<Repository> {
    const res = await fetch(`${API_BASE}/repositories/connect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ repo_input: repoInput }),
    });
    return handleResponse<Repository>(res);
  },

  // Pull Requests & Diffs
  async fetchDiff(repoFullName: string, pullNumber: number): Promise<DiffSummary> {
    const res = await fetch(`${API_BASE}/pull-requests/fetch-diff`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ repo_full_name: repoFullName, pull_number: pullNumber }),
    });
    return handleResponse<DiffSummary>(res);
  },

  // Reviews
  async startReview(repoFullName: string, pullNumber: number, mode: string = 'deterministic'): Promise<ReviewJob> {
    const res = await fetch(`${API_BASE}/reviews/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ repo_full_name: repoFullName, pull_number: pullNumber, mode }),
    });
    return handleResponse<ReviewJob>(res);
  },

  async getReview(jobId: number): Promise<ReviewJob> {
    const res = await fetch(`${API_BASE}/reviews/${jobId}`);
    return handleResponse<ReviewJob>(res);
  },

  async getReviewHistory(params?: { repo_full_name?: string; status?: string; limit?: number; offset?: number }): Promise<ReviewJob[]> {
    const query = new URLSearchParams();
    if (params?.repo_full_name) query.append('repo_full_name', params.repo_full_name);
    if (params?.status) query.append('status', params.status);
    if (params?.limit) query.append('limit', String(params.limit));
    if (params?.offset) query.append('offset', String(params.offset));

    const res = await fetch(`${API_BASE}/reviews?${query.toString()}`);
    return handleResponse<ReviewJob[]>(res);
  },

  // Findings & Feedback
  async getFinding(id: number): Promise<Finding> {
    const res = await fetch(`${API_BASE}/findings/${id}`);
    return handleResponse<Finding>(res);
  },

  async submitFeedback(data: FeedbackSubmission): Promise<any> {
    const res = await fetch(`${API_BASE}/findings/${data.finding_id}/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        finding_id: data.finding_id,
        feedback_type: data.feedback_type,
        comment: data.comment,
      }),
    });
    return handleResponse<any>(res);
  },

  // Settings & System Status
  async getSettings(): Promise<SystemSettings> {
    const res = await fetch(`${API_BASE}/settings/status`);
    return handleResponse<SystemSettings>(res);
  },

  // Health
  async checkHealth(): Promise<{ status: string }> {
    const res = await fetch(`${API_BASE}/healthz`);
    return handleResponse<{ status: string }>(res);
  },
};
