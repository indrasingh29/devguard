import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api/client';
import type { ReviewJob } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { SeverityBadge } from '../components/SeverityBadge';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { EmptyState } from '../components/EmptyState';
import { History, Search, Filter, ArrowRight } from 'lucide-react';

export const ReviewHistoryPage: React.FC = () => {
  const [reviews, setReviews] = useState<ReviewJob[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [_error, setError] = useState<string | null>(null);

  const [searchRepo, setSearchRepo] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  const loadHistory = async () => {
    try {
      setLoading(true);
      const params: any = { limit: 50 };
      if (searchRepo.trim()) params.repo_full_name = searchRepo.trim();
      if (statusFilter !== 'all') params.status = statusFilter;

      const data = await api.getReviewHistory(params);
      setReviews(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load review history');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, [statusFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadHistory();
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Review Audit & History</h1>
        <p className="text-sm text-slate-400">
          Chronological record of all pull request security audits and code quality reviews.
        </p>
      </div>

      {/* Search and Filters Bar */}
      <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3">
        <form onSubmit={handleSearchSubmit} className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search by repo (e.g. facebook/react)..."
            value={searchRepo}
            onChange={(e) => setSearchRepo(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-lg bg-slate-950 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
          />
        </form>

        <div className="flex items-center space-x-2 w-full sm:w-auto">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-sky-500"
          >
            <option value="all">All Statuses</option>
            <option value="COMPLETED">Completed</option>
            <option value="PROCESSING">Processing</option>
            <option value="QUEUED">Queued</option>
            <option value="FAILED">Failed</option>
          </select>
        </div>
      </div>

      {/* History List */}
      {loading ? (
        <LoadingSpinner label="Loading review history..." />
      ) : reviews.length === 0 ? (
        <EmptyState
          icon={History}
          title="No Reviews Recorded"
          description="Pull request reviews will appear here once executed via dashboard or webhook."
          actionText="Run a Code Review"
          onAction={() => (window.location.href = '/review')}
        />
      ) : (
        <div className="border border-slate-800 rounded-xl overflow-hidden bg-slate-900/60 divide-y divide-slate-800 shadow-sm">
          {reviews.map((job) => (
            <div
              key={job.id}
              className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-slate-800/30 transition-colors"
            >
              <div className="space-y-1.5 flex-1">
                <div className="flex items-center space-x-2 flex-wrap gap-1">
                  <span className="font-mono text-xs font-bold text-sky-400">
                    {job.repo_full_name || 'Repository'} #{job.pr_number || ''}
                  </span>
                  <StatusBadge status={job.status} />
                  <span className="text-[11px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">
                    Mode: {job.mode}
                  </span>
                </div>

                <h3 className="text-sm font-semibold text-slate-100">
                  {job.pr_title || job.summary || `Pull Request Review #${job.id}`}
                </h3>

                <div className="flex flex-wrap items-center gap-4 text-xs font-mono text-slate-400">
                  <span>Timestamp: {new Date(job.created_at).toLocaleString()}</span>
                  <span>Commit: {job.commit_sha.slice(0, 8)}</span>
                  {job.execution_time_ms && <span>Latency: {job.execution_time_ms}ms</span>}
                  <span>Files: {job.total_files_analyzed}</span>
                </div>
              </div>

              <div className="flex items-center space-x-4 shrink-0">
                <div className="flex items-center space-x-1.5">
                  {job.severity_counts && job.severity_counts.critical > 0 && (
                    <SeverityBadge severity="critical" className="text-[10px]" />
                  )}
                  {job.severity_counts && job.severity_counts.high > 0 && (
                    <SeverityBadge severity="high" className="text-[10px]" />
                  )}
                  <span className="text-xs font-semibold text-slate-300 ml-1">
                    {job.total_findings} finding{job.total_findings !== 1 ? 's' : ''}
                  </span>
                </div>

                <Link
                  to={`/review?job_id=${job.id}`}
                  className="inline-flex items-center px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-sky-400 border border-slate-700 transition-colors"
                >
                  Inspect <ArrowRight className="w-3.5 h-3.5 ml-1" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
