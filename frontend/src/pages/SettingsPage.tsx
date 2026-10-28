import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import type { SystemSettings } from '../types';
import { LoadingSpinner } from '../components/LoadingSpinner';
import {
  Database,
  GitBranch,
  Cpu,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  Lock,
} from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<SystemSettings | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    const loadSettings = async () => {
      try {
        setLoading(true);
        const data = await api.getSettings();
        if (isMounted) {
          setSettings(data);
          setError(null);
        }
      } catch (err: any) {
        if (isMounted) setError(err.message || 'Failed to load system settings');
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    loadSettings();
    return () => {
      isMounted = false;
    };
  }, []);

  if (loading) {
    return <LoadingSpinner label="Checking system configuration & health..." size="lg" />;
  }

  if (error || !settings) {
    return (
      <div className="p-8 text-center space-y-4">
        <div className="p-4 rounded-xl bg-red-950/40 border border-red-800 text-red-300 text-sm max-w-md mx-auto">
          {error || 'Unable to connect to settings service.'}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">System Configuration & Health</h1>
        <p className="text-sm text-slate-400">
          Inspection of backend integrations, security boundaries, and runtime configurations.
        </p>
      </div>

      {/* Security Note Banner */}
      <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-start space-x-3 text-xs text-slate-300">
        <Lock className="w-4 h-4 text-sky-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-white block mb-0.5">Zero Secret Exposure Policy</span>
          DevGuard strictly separates configuration from credentials. All API tokens, HMAC webhook secrets,
          and database passwords remain encrypted on the server environment and are never transmitted to the browser bundle.
        </div>
      </div>

      <div className="space-y-6">
        {/* Core Architecture Card */}
        <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 space-y-4">
          <h2 className="text-base font-semibold text-white flex items-center">
            <Cpu className="w-4 h-4 mr-2 text-sky-400" />
            Runtime Environment & Server
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 space-y-1">
              <span className="text-slate-400">Application Name</span>
              <span className="font-mono text-slate-200 block font-semibold">{settings.project_name}</span>
            </div>
            <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 space-y-1">
              <span className="text-slate-400">Version</span>
              <span className="font-mono text-slate-200 block font-semibold">v{settings.version}</span>
            </div>
            <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 space-y-1">
              <span className="text-slate-400">Environment</span>
              <span className="font-mono text-slate-200 block font-semibold uppercase">{settings.environment}</span>
            </div>
            <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 space-y-1">
              <span className="text-slate-400">Max PR Diff Byte Limits</span>
              <span className="font-mono text-slate-200 block font-semibold">
                {settings.max_diff_bytes / 1000} KB ({settings.max_diff_files} files max)
              </span>
            </div>
          </div>
        </div>

        {/* Database Status Card */}
        <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-white flex items-center">
              <Database className="w-4 h-4 mr-2 text-sky-400" />
              Database Engine (PostgreSQL / Alembic)
            </h2>
            <div className="flex items-center space-x-1.5 text-xs font-mono">
              {settings.database_connected ? (
                <>
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span className="text-emerald-300">Connected</span>
                </>
              ) : (
                <>
                  <XCircle className="w-4 h-4 text-rose-400" />
                  <span className="text-rose-300">Disconnected</span>
                </>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 space-y-1">
              <span className="text-slate-400">Active Dialect</span>
              <span className="font-mono text-slate-200 block font-semibold uppercase">{settings.database_dialect}</span>
            </div>
            <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 space-y-1">
              <span className="text-slate-400">Schema Migrations</span>
              <span className="font-mono text-emerald-400 block font-semibold">Alembic Version 001_initial_schema</span>
            </div>
          </div>
        </div>

        {/* GitHub Integration Card */}
        <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 space-y-4">
          <h2 className="text-base font-semibold text-white flex items-center">
            <GitBranch className="w-4 h-4 mr-2 text-sky-400" />
            GitHub API & Webhooks
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 space-y-1">
              <span className="text-slate-400">API Token Configured</span>
              <div className="flex items-center space-x-1 mt-0.5">
                {settings.github_token_configured ? (
                  <span className="text-emerald-400 font-semibold font-mono">Yes (Authenticated)</span>
                ) : (
                  <span className="text-amber-400 font-semibold font-mono">No (Public 60 req/hr)</span>
                )}
              </div>
            </div>

            <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 space-y-1">
              <span className="text-slate-400">Rate Limit Remaining</span>
              <span className="font-mono text-slate-200 block font-semibold">
                {settings.github_rate_limit_remaining !== null
                  ? `${settings.github_rate_limit_remaining} requests`
                  : 'Checking...'}
              </span>
            </div>

            <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 space-y-1">
              <span className="text-slate-400">Webhook HMAC Secret</span>
              <div className="flex items-center space-x-1 mt-0.5">
                {settings.github_webhook_configured ? (
                  <span className="text-emerald-400 font-semibold font-mono">Configured</span>
                ) : (
                  <span className="text-slate-400 font-mono">Optional (Dev Mode)</span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* AI & Model Providers Card */}
        <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-white flex items-center">
              <ShieldCheck className="w-4 h-4 mr-2 text-sky-400" />
              Review Engine & Model Providers
            </h2>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 uppercase">
              Provider: {settings.llm_provider}
            </span>
          </div>

          <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-slate-300 font-medium">Deterministic Rule Engine</span>
              <span className="text-emerald-400 font-mono font-semibold">Active & Operational</span>
            </div>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              Deterministic checks (secrets, security AST, bug detection, test coverage, code smells) always run
              regardless of external LLM availability. Zero paid dependencies are required.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-slate-300 font-medium">Optional LLM Provider</span>
              <span className={settings.llm_configured ? 'text-emerald-400 font-mono' : 'text-slate-500 font-mono'}>
                {settings.llm_configured ? 'Configured & Ready' : 'Unconfigured (Fallback active)'}
              </span>
            </div>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              Available adapters: <code>gemini</code>, <code>openai</code>, <code>ollama</code>. Model outputs are strictly
              validated through Pydantic JSON schemas and checked against actual PR line numbers to eliminate hallucinations.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
