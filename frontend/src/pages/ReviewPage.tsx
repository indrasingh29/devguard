import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import type { ReviewJob, DiffSummary } from '../types';
import { DiffViewer } from '../components/DiffViewer';
import { SeverityBadge } from '../components/SeverityBadge';
import { CategoryBadge } from '../components/CategoryBadge';
import { SourceBadge } from '../components/SourceBadge';
import { StatusBadge } from '../components/StatusBadge';
import { LoadingSpinner } from '../components/LoadingSpinner';
import {
  GitPullRequest,
  Search,
  AlertTriangle,
  FileCode,
  ShieldAlert,
} from 'lucide-react';

export const ReviewPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  const [repoInput, setRepoInput] = useState<string>(
    searchParams.get('repo') || 'octocat/Hello-World'
  );
  const [prNumberInput, setPrNumberInput] = useState<string>(
    searchParams.get('pr') || '12'
  );
  const [mode, setMode] = useState<string>('deterministic');

  const [reviewJob, setReviewJob] = useState<ReviewJob | null>(null);
  const [diffSummary, setDiffSummary] = useState<DiffSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [selectedSeverity, setSelectedSeverity] = useState<string>('all');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedFile, setSelectedFile] = useState<string>('all');

  // Load existing job if jobId in query param
  useEffect(() => {
    const jobIdParam = searchParams.get('job_id');
    if (jobIdParam) {
      const loadJob = async () => {
        try {
          setLoading(true);
          const job = await api.getReview(Number(jobIdParam));
          setReviewJob(job);
          if (job.repo_full_name && job.pr_number) {
            setRepoInput(job.repo_full_name);
            setPrNumberInput(String(job.pr_number));
            const diff = await api.fetchDiff(job.repo_full_name, job.pr_number);
            setDiffSummary(diff);
          }
        } catch (err: any) {
          setError(err.message || 'Failed to load review job');
        } finally {
          setLoading(false);
        }
      };
      loadJob();
    }
  }, [searchParams]);

  const handleStartReview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!repoInput.trim() || !prNumberInput.trim()) return;

    try {
      setLoading(true);
      setError(null);
      setReviewJob(null);
      setDiffSummary(null);

      const pullNum = parseInt(prNumberInput.trim(), 10);
      const cleanRepo = repoInput.trim();

      // Fetch diff and run review
      const [diff, job] = await Promise.all([
        api.fetchDiff(cleanRepo, pullNum),
        api.startReview(cleanRepo, pullNum, mode),
      ]);

      setDiffSummary(diff);
      setReviewJob(job);
      setSearchParams({ repo: cleanRepo, pr: String(pullNum), job_id: String(job.id) });
    } catch (err: any) {
      setError(err.message || 'Failed to complete review. Please check repo name and PR number.');
    } finally {
      setLoading(false);
    }
  };

  // Filtered findings
  const allFindings = reviewJob?.findings || [];
  const filteredFindings = allFindings.filter((f) => {
    if (selectedSeverity !== 'all' && f.severity !== selectedSeverity) return false;
    if (selectedCategory !== 'all' && f.category !== selectedCategory) return false;
    if (selectedFile !== 'all' && f.file_path !== selectedFile) return false;
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      return (
        f.title.toLowerCase().includes(query) ||
        f.message.toLowerCase().includes(query) ||
        f.file_path.toLowerCase().includes(query)
      );
    }
    return true;
  });

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Pull Request Review Hub</h1>
        <p className="text-sm text-slate-400">
          Run automated deterministic code reviews and security inspections on any GitHub pull request.
        </p>
      </div>

      {/* Review Trigger Form */}
      <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 space-y-5">
        <form onSubmit={handleStartReview} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-12 gap-3">
            <div className="sm:col-span-6">
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                GitHub Repository (owner/repo or URL)
              </label>
              <input
                type="text"
                placeholder="e.g. octocat/Hello-World"
                value={repoInput}
                onChange={(e) => setRepoInput(e.target.value)}
                className="w-full px-3.5 py-2 rounded-lg bg-slate-950 border border-slate-700 text-sm text-white font-mono focus:outline-none focus:border-sky-500"
              />
            </div>

            <div className="sm:col-span-3">
              <label className="block text-xs font-medium text-slate-300 mb-1.5">PR Number</label>
              <input
                type="number"
                placeholder="e.g. 12"
                value={prNumberInput}
                onChange={(e) => setPrNumberInput(e.target.value)}
                className="w-full px-3.5 py-2 rounded-lg bg-slate-950 border border-slate-700 text-sm text-white font-mono focus:outline-none focus:border-sky-500"
              />
            </div>

            <div className="sm:col-span-3">
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Review Engine</label>
              <select
                value={mode}
                onChange={(e) => setMode(e.target.value)}
                className="w-full px-3.5 py-2 rounded-lg bg-slate-950 border border-slate-700 text-sm text-white focus:outline-none focus:border-sky-500"
              >
                <option value="deterministic">Deterministic Engine (Local, Instant)</option>
                <option value="hybrid_llm">Hybrid AI + Deterministic</option>
              </select>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">
            <div className="flex flex-wrap items-center gap-2 text-xs text-slate-400">
              <span>Quick tests:</span>
              <button
                type="button"
                onClick={() => {
                  setRepoInput('octocat/Hello-World');
                  setPrNumberInput('12');
                }}
                className="text-sky-400 hover:underline font-mono"
              >
                octocat/Hello-World #12
              </button>
              <span>•</span>
              <button
                type="button"
                onClick={() => {
                  setRepoInput('pallets/flask');
                  setPrNumberInput('5612');
                }}
                className="text-sky-400 hover:underline font-mono"
              >
                pallets/flask #5612
              </button>
            </div>

            <button
              type="submit"
              disabled={loading || !repoInput.trim() || !prNumberInput.trim()}
              className="w-full sm:w-auto px-6 py-2.5 rounded-lg bg-sky-500 hover:bg-sky-400 disabled:bg-slate-800 disabled:text-slate-500 text-slate-950 font-semibold text-sm transition-colors shadow-sm flex items-center justify-center shrink-0"
            >
              {loading ? (
                <>
                  <LoadingSpinner size="sm" label="" />
                  <span className="ml-2">Analyzing Diff...</span>
                </>
              ) : (
                <>
                  <GitPullRequest className="w-4 h-4 mr-2" />
                  Run Code Review
                </>
              )}
            </button>
          </div>
        </form>

        {error && (
          <div className="p-4 rounded-lg bg-red-950/50 border border-red-800 text-red-300 text-xs flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 shrink-0 text-red-400" />
            <div className="flex-1">{error}</div>
          </div>
        )}
      </div>

      {/* Review Results Summary Card */}
      {reviewJob && (
        <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
            <div>
              <div className="flex items-center space-x-2.5">
                <span className="font-mono text-sm font-bold text-white">
                  {reviewJob.repo_full_name} #{reviewJob.pr_number}
                </span>
                <StatusBadge status={reviewJob.status} />
                <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">
                  {reviewJob.mode}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                Commit: <code className="text-sky-400 font-mono">{reviewJob.commit_sha.slice(0, 8)}</code> •
                Execution time: {reviewJob.execution_time_ms || 0}ms
              </p>
            </div>

            <div className="flex items-center space-x-3 text-xs">
              <div className="text-right">
                <span className="text-slate-400 block">Total Issues</span>
                <span className="text-lg font-bold text-white">{reviewJob.total_findings}</span>
              </div>
            </div>
          </div>

          <p className="text-sm text-slate-300 leading-relaxed">{reviewJob.summary}</p>
        </div>
      )}

      {/* Findings & Diff Viewer Section */}
      {diffSummary && (
        <div className="space-y-6">
          {/* Controls Bar: Search, Category, Severity Filters */}
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-3">
            <div className="relative w-full md:w-72">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="text"
                placeholder="Search findings..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-4 py-2 rounded-lg bg-slate-950 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
              />
            </div>

            <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
              {/* Severity Filter */}
              <select
                value={selectedSeverity}
                onChange={(e) => setSelectedSeverity(e.target.value)}
                className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-sky-500"
              >
                <option value="all">All Severities</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>

              {/* Category Filter */}
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-sky-500"
              >
                <option value="all">All Categories</option>
                <option value="security">Security</option>
                <option value="secret_leak">Secret Leak</option>
                <option value="bug_risk">Bug Risk</option>
                <option value="error_handling">Error Handling</option>
                <option value="maintainability">Code Quality</option>
                <option value="test_insufficiency">Missing Tests</option>
              </select>

              {/* File Filter */}
              <select
                value={selectedFile}
                onChange={(e) => setSelectedFile(e.target.value)}
                className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-sky-500 max-w-[200px]"
              >
                <option value="all">All Files ({diffSummary.files.length})</option>
                {diffSummary.files.map((f) => (
                  <option key={f.path} value={f.path}>
                    {f.path}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Grouped Findings Cards & Diff List */}
          <div className="space-y-6">
            {/* Findings List Banner if matches exist */}
            {filteredFindings.length > 0 && (
              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-white flex items-center">
                  <ShieldAlert className="w-4 h-4 mr-2 text-amber-400" />
                  Flagged Findings ({filteredFindings.length})
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {filteredFindings.map((finding) => (
                    <div
                      key={finding.id}
                      onClick={() => navigate(`/findings/${finding.id}`)}
                      className="p-4 rounded-xl bg-slate-900 border border-slate-800 hover:border-sky-500/80 cursor-pointer transition-all space-y-2 group shadow-sm"
                    >
                      <div className="flex items-center justify-between flex-wrap gap-2">
                        <div className="flex items-center space-x-2">
                          <SeverityBadge severity={finding.severity} />
                          <CategoryBadge category={finding.category} />
                        </div>
                        <SourceBadge source={finding.detection_source} />
                      </div>

                      <h4 className="text-sm font-semibold text-slate-100 group-hover:text-sky-300 transition-colors">
                        {finding.title}
                      </h4>

                      <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                        <span className="truncate max-w-[240px]">{finding.file_path}:{finding.line_start || 1}</span>
                        <span className="text-sky-400 flex items-center group-hover:translate-x-0.5 transition-transform">
                          Details &rarr;
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Changed Files & Diffs */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-white flex items-center">
                  <FileCode className="w-4 h-4 mr-2 text-sky-400" />
                  Changed Files & Unified Diff ({diffSummary.files.length})
                </h3>
                <div className="text-xs font-mono text-slate-400">
                  <span className="text-emerald-400">+{diffSummary.total_additions}</span> /{' '}
                  <span className="text-rose-400">-{diffSummary.total_deletions}</span>
                </div>
              </div>

              {diffSummary.files
                .filter((f) => selectedFile === 'all' || f.path === selectedFile)
                .map((file) => (
                  <DiffViewer
                    key={file.path}
                    file={file}
                    findings={reviewJob?.findings?.filter((f) => f.file_path === file.path) || []}
                    onSelectFinding={(f) => navigate(`/findings/${f.id}`)}
                  />
                ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
