import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import type { Repository } from '../types';
import { FolderGit2, Plus, ExternalLink, History, CheckCircle2, AlertCircle } from 'lucide-react';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { EmptyState } from '../components/EmptyState';
import { Link } from 'react-router-dom';

export const RepositoriesPage: React.FC = () => {
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [connecting, setConnecting] = useState<boolean>(false);
  const [inputVal, setInputVal] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const loadRepositories = async () => {
    try {
      setLoading(true);
      const data = await api.getRepositories();
      setRepositories(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load repositories');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRepositories();
  }, []);

  const handleConnect = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputVal.trim()) return;

    try {
      setConnecting(true);
      setError(null);
      setSuccess(null);
      const newRepo = await api.connectRepository(inputVal.trim());
      setSuccess(`Successfully connected '${newRepo.full_name}'!`);
      setInputVal('');
      loadRepositories();
    } catch (err: any) {
      setError(err.message || 'Failed to connect repository');
    } finally {
      setConnecting(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Repository Management</h1>
        <p className="text-sm text-slate-400">
          Connect public or authorized GitHub repositories for continuous code analysis and automated reviews.
        </p>
      </div>

      {/* Connect Repository Card */}
      <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 space-y-4">
        <h2 className="text-base font-semibold text-white flex items-center">
          <Plus className="w-4 h-4 mr-2 text-sky-400" />
          Connect a GitHub Repository
        </h2>
        <form onSubmit={handleConnect} className="flex flex-col sm:flex-row gap-3">
          <div className="flex-1">
            <input
              type="text"
              placeholder="e.g. facebook/react or https://github.com/octocat/Hello-World"
              value={inputVal}
              onChange={(e) => setInputVal(e.target.value)}
              className="w-full px-4 py-2.5 rounded-lg bg-slate-950 border border-slate-700 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500 font-mono"
            />
          </div>
          <button
            type="submit"
            disabled={connecting || !inputVal.trim()}
            className="px-5 py-2.5 rounded-lg bg-sky-500 hover:bg-sky-400 disabled:bg-slate-800 disabled:text-slate-500 text-slate-950 font-semibold text-sm transition-colors flex items-center justify-center shrink-0"
          >
            {connecting ? 'Validating...' : 'Connect Repository'}
          </button>
        </form>

        {error && (
          <div className="p-3 rounded-lg bg-red-950/50 border border-red-800/80 text-red-300 text-xs flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-red-400" />
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="p-3 rounded-lg bg-emerald-950/50 border border-emerald-800/80 text-emerald-300 text-xs flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-400" />
            <span>{success}</span>
          </div>
        )}

        <div className="flex flex-wrap gap-2 text-xs text-slate-400">
          <span>Popular presets:</span>
          <button
            type="button"
            onClick={() => setInputVal('octocat/Hello-World')}
            className="text-sky-400 hover:underline font-mono"
          >
            octocat/Hello-World
          </button>
          <span>•</span>
          <button
            type="button"
            onClick={() => setInputVal('pallets/flask')}
            className="text-sky-400 hover:underline font-mono"
          >
            pallets/flask
          </button>
          <span>•</span>
          <button
            type="button"
            onClick={() => setInputVal('fastapi/fastapi')}
            className="text-sky-400 hover:underline font-mono"
          >
            fastapi/fastapi
          </button>
        </div>
      </div>

      {/* Connected Repositories Grid */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-white">Connected Repositories ({repositories.length})</h2>

        {loading ? (
          <LoadingSpinner label="Loading repositories..." />
        ) : repositories.length === 0 ? (
          <EmptyState
            icon={FolderGit2}
            title="No Repositories Connected"
            description="Add your first repository above to start analyzing pull requests and running security audits."
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {repositories.map((repo) => (
              <div
                key={repo.id}
                className="p-5 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition-all flex flex-col justify-between space-y-4 shadow-sm"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">
                      {repo.default_branch}
                    </span>
                    <a
                      href={repo.html_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-slate-400 hover:text-slate-200"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  </div>
                  <h3 className="text-base font-semibold text-white font-mono truncate">{repo.full_name}</h3>
                  <p className="text-xs text-slate-400 mt-1">
                    Connected: {new Date(repo.created_at).toLocaleDateString()}
                  </p>
                </div>

                <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
                  <div className="flex items-center space-x-1">
                    <History className="w-3.5 h-3.5 text-slate-400" />
                    <span>{repo.total_reviews_count || 0} reviews</span>
                  </div>
                  <Link
                    to={`/review?repo=${repo.full_name}`}
                    className="inline-flex items-center font-medium text-sky-400 hover:text-sky-300"
                  >
                    Review PR &rarr;
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
