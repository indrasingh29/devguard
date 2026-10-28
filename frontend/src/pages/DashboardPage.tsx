import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  GitPullRequest,
  ArrowRight,
  FolderGit2,
  AlertTriangle,
  History,
  ExternalLink,
} from 'lucide-react';
import { api } from '../api/client';
import type { ReviewJob, Repository } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { SeverityBadge } from '../components/SeverityBadge';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { EmptyState } from '../components/EmptyState';

export const DashboardPage: React.FC = () => {
  const [reviews, setReviews] = useState<ReviewJob[]>([]);
  const [repos, setRepos] = useState<Repository[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    const loadDashboardData = async () => {
      try {
        setLoading(true);
        const [reviewsData, reposData] = await Promise.all([
          api.getReviewHistory({ limit: 10 }),
          api.getRepositories(),
        ]);
        if (isMounted) {
          setReviews(reviewsData);
          setRepos(reposData);
          setError(null);
        }
      } catch (err: any) {
        if (isMounted) setError(err.message || 'Failed to load dashboard data');
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    loadDashboardData();
    return () => {
      isMounted = false;
    };
  }, []);

  // Compute aggregate real metrics from database reviews
  const totalFindingsCount = reviews.reduce((acc, r) => acc + (r.total_findings || 0), 0);
  const totalCriticalCount = reviews.reduce((acc, r) => acc + (r.severity_counts?.critical || 0), 0);
  const totalHighCount = reviews.reduce((acc, r) => acc + (r.severity_counts?.high || 0), 0);
  const totalMediumCount = reviews.reduce((acc, r) => acc + (r.severity_counts?.medium || 0), 0);
  const totalLowCount = reviews.reduce(
    (acc, r) => acc + (r.severity_counts?.low || 0) + (r.severity_counts?.info || 0),
    0
  );

  if (loading) {
    return <LoadingSpinner label="Loading dashboard metrics..." size="lg" />;
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Security & Quality Dashboard</h1>
          <p className="text-sm text-slate-400">
            Real-time pull request review status and findings summary
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <Link
            to="/review"
            className="inline-flex items-center px-4 py-2 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 font-semibold text-sm transition-colors shadow-sm"
          >
            <GitPullRequest className="w-4 h-4 mr-2" />
            New Review
          </Link>
          <Link
            to="/repositories"
            className="inline-flex items-center px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium border border-slate-700 transition-colors"
          >
            <FolderGit2 className="w-4 h-4 mr-2" />
            Connect Repo
          </Link>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-red-950/40 border border-red-800 text-red-300 text-sm flex items-center space-x-2">
          <AlertTriangle className="w-4 h-4 shrink-0 text-red-400" />
          <span>{error}</span>
        </div>
      )}

      {/* Aggregate Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
          <span className="text-xs font-medium text-slate-400 uppercase tracking-wider block">Total Findings</span>
          <span className="text-2xl font-bold text-white mt-1 block">{totalFindingsCount}</span>
          <span className="text-[11px] text-slate-400 block mt-1">Across all reviews</span>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-red-950/80">
          <span className="text-xs font-semibold text-red-400 uppercase tracking-wider block">Critical</span>
          <span className="text-2xl font-bold text-red-400 mt-1 block">{totalCriticalCount}</span>
          <span className="text-[11px] text-red-400/80 block mt-1">Urgent action</span>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-orange-950/80">
          <span className="text-xs font-semibold text-orange-400 uppercase tracking-wider block">High</span>
          <span className="text-2xl font-bold text-orange-400 mt-1 block">{totalHighCount}</span>
          <span className="text-[11px] text-orange-400/80 block mt-1">Security & bugs</span>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-amber-950/80">
          <span className="text-xs font-semibold text-amber-400 uppercase tracking-wider block">Medium</span>
          <span className="text-2xl font-bold text-amber-400 mt-1 block">{totalMediumCount}</span>
          <span className="text-[11px] text-amber-400/80 block mt-1">Missing tests & quality</span>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-blue-950/80">
          <span className="text-xs font-semibold text-blue-400 uppercase tracking-wider block">Low & Info</span>
          <span className="text-2xl font-bold text-blue-400 mt-1 block">{totalLowCount}</span>
          <span className="text-[11px] text-blue-400/80 block mt-1">Style & suggestions</span>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
          <span className="text-xs font-medium text-slate-400 uppercase tracking-wider block">Repositories</span>
          <span className="text-2xl font-bold text-white mt-1 block">{repos.length}</span>
          <span className="text-[11px] text-slate-400 block mt-1">Connected repos</span>
        </div>
      </div>

      {/* Main Content: Recent Reviews & Connected Repos */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Reviews Table */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white flex items-center">
              <History className="w-5 h-5 mr-2 text-sky-400" />
              Recent Pull Request Reviews
            </h2>
            <Link
              to="/history"
              className="text-xs text-sky-400 hover:text-sky-300 font-medium flex items-center"
            >
              View all ({reviews.length}) <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </Link>
          </div>

          {reviews.length === 0 ? (
            <EmptyState
              icon={GitPullRequest}
              title="No Reviews Yet"
              description="Connect a repository or enter a GitHub pull request URL to run your first review."
              actionText="Review a Pull Request"
              onAction={() => (window.location.href = '/review')}
            />
          ) : (
            <div className="border border-slate-800 rounded-xl overflow-hidden bg-slate-900/60 shadow-sm divide-y divide-slate-800">
              {reviews.map((job) => (
                <Link
                  key={job.id}
                  to={`/review?job_id=${job.id}`}
                  className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-800/40 transition-colors block"
                >
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-mono text-xs text-sky-400 font-semibold">
                        {job.repo_full_name || 'Repository'} #{job.pr_number || ''}
                      </span>
                      <StatusBadge status={job.status} />
                      <span className="text-[11px] text-slate-400 font-mono">
                        {job.mode === 'hybrid_llm' ? 'AI+Deterministic' : 'Deterministic'}
                      </span>
                    </div>
                    <h3 className="text-sm font-medium text-slate-100 line-clamp-1">
                      {job.pr_title || job.summary || `Pull Request Review #${job.id}`}
                    </h3>
                    <div className="flex items-center space-x-4 text-xs text-slate-400">
                      <span>{new Date(job.created_at).toLocaleDateString()}</span>
                      <span>Commit: {job.commit_sha.slice(0, 7)}</span>
                      {job.execution_time_ms && (
                        <span>{job.execution_time_ms}ms</span>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center space-x-3 shrink-0">
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
                    <ArrowRight className="w-4 h-4 text-slate-400" />
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Connected Repositories Sidebar */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white flex items-center">
              <FolderGit2 className="w-5 h-5 mr-2 text-sky-400" />
              Connected Repos
            </h2>
            <Link
              to="/repositories"
              className="text-xs text-sky-400 hover:text-sky-300 font-medium"
            >
              Manage
            </Link>
          </div>

          {repos.length === 0 ? (
            <div className="p-6 rounded-xl border border-dashed border-slate-800 bg-slate-900/40 text-center">
              <p className="text-xs text-slate-400 mb-3">No repositories connected yet.</p>
              <Link
                to="/repositories"
                className="inline-flex items-center text-xs font-medium text-sky-400 hover:text-sky-300"
              >
                Add repository &rarr;
              </Link>
            </div>
          ) : (
            <div className="border border-slate-800 rounded-xl overflow-hidden bg-slate-900/60 divide-y divide-slate-800">
              {repos.slice(0, 5).map((repo) => (
                <div key={repo.id} className="p-3.5 hover:bg-slate-800/30 transition-colors">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-mono text-xs font-semibold text-slate-200 truncate max-w-[200px]">
                      {repo.full_name}
                    </span>
                    <a
                      href={repo.html_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-slate-400 hover:text-slate-200"
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  </div>
                  <div className="flex items-center justify-between text-xs text-slate-400">
                    <span>Branch: {repo.default_branch}</span>
                    <span>{repo.total_reviews_count || 0} reviews</span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Quick Start Tip Card */}
          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2 text-xs">
            <h4 className="font-semibold text-slate-200">How to run a review:</h4>
            <p className="text-slate-400 leading-relaxed">
              Navigate to <strong>Review PR</strong>, enter any public repository (e.g.{' '}
              <code className="text-sky-300 font-mono">owner/repo</code>) and pull request number. DevGuard will
              stream diffs and execute deterministic rules in seconds.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
