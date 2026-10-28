import React from 'react';
import { Link } from 'react-router-dom';
import {
  ShieldAlert,
  Cpu,
  Lock,
  Sparkles,
  ArrowRight,
  CheckCircle2,
  Bug,
  Key,
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  return (
    <div className="space-y-24 py-8">
      {/* Hero Section */}
      <section className="text-center max-w-4xl mx-auto space-y-6">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-sky-950/70 border border-sky-800/60 text-sky-300 text-xs font-mono">
          <Sparkles className="w-3.5 h-3.5 text-sky-400" />
          <span>DevGuard AI 1.0 — Deterministic + AI Pull Request Review</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white leading-[1.15]">
          Continuous Code Quality & Security for{' '}
          <span className="bg-gradient-to-r from-sky-400 via-teal-300 to-emerald-400 bg-clip-text text-transparent">
            GitHub Pull Requests
          </span>
        </h1>

        <p className="text-lg sm:text-xl text-slate-300 max-w-2xl mx-auto leading-relaxed">
          Catch critical bugs, security vulnerabilities, secret leaks, and untested code
          before they reach production. Combines fast deterministic static analysis with optional LLM reasoning.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
          <Link
            to="/dashboard"
            className="w-full sm:w-auto inline-flex items-center justify-center px-6 py-3.5 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 font-semibold shadow-lg shadow-sky-500/20 transition-all text-sm group"
          >
            Launch Dashboard
            <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
          </Link>
          <Link
            to="/review"
            className="w-full sm:w-auto inline-flex items-center justify-center px-6 py-3.5 rounded-lg bg-slate-800/80 hover:bg-slate-800 text-white font-medium border border-slate-700 transition-colors text-sm"
          >
            Review a Pull Request
          </Link>
        </div>

        {/* Value proposition checkmarks */}
        <div className="pt-8 flex flex-wrap items-center justify-center gap-6 text-xs text-slate-400 font-medium">
          <div className="flex items-center space-x-1.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>Zero paid LLM dependency required</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>PostgreSQL & Alembic Persistence</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>HMAC Webhook Idempotency</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>Strict Line Number Validation</span>
          </div>
        </div>
      </section>

      {/* Feature Grid */}
      <section className="space-y-12">
        <div className="text-center space-y-3">
          <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
            Multi-Layered Code Review Architecture
          </h2>
          <p className="text-slate-400 text-sm max-w-xl mx-auto">
            Every pull request goes through our rigorous validation pipeline to guarantee accuracy and eliminate hallucinations.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-colors space-y-3">
            <div className="p-2.5 w-fit rounded-lg bg-red-950/50 border border-red-800/50 text-red-400">
              <Key className="w-5 h-5" />
            </div>
            <h3 className="text-base font-semibold text-white">Secret Leak Prevention</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Detects committed AWS keys, GitHub Personal Access Tokens, RSA/EC private keys, and high-entropy credentials before merge.
            </p>
          </div>

          <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-colors space-y-3">
            <div className="p-2.5 w-fit rounded-lg bg-orange-950/50 border border-orange-800/50 text-orange-400">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <h3 className="text-base font-semibold text-white">Vulnerability Detection</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Identifies SQL injection, command execution via shell=True, path traversal, unsafe deserialization (pickle), and weak crypto.
            </p>
          </div>

          <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-colors space-y-3">
            <div className="p-2.5 w-fit rounded-lg bg-amber-950/50 border border-amber-800/50 text-amber-400">
              <Bug className="w-5 h-5" />
            </div>
            <h3 className="text-base font-semibold text-white">Logic Errors & Bug Risks</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Flags bare except blocks, mutable default parameters, tuple assert mistakes, unhandled errors, and resource leaks.
            </p>
          </div>

          <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-colors space-y-3">
            <div className="p-2.5 w-fit rounded-lg bg-emerald-950/50 border border-emerald-800/50 text-emerald-400">
              <Cpu className="w-5 h-5" />
            </div>
            <h3 className="text-base font-semibold text-white">Deterministic Rule Engine</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Sub-second analysis with zero external API calls. Runs natively on your server with 100% reproducible results and validated lines.
            </p>
          </div>

          <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-colors space-y-3">
            <div className="p-2.5 w-fit rounded-lg bg-indigo-950/50 border border-indigo-800/50 text-indigo-400">
              <Sparkles className="w-5 h-5" />
            </div>
            <h3 className="text-base font-semibold text-white">Optional Model Reasoning</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Plug in Google Gemini, OpenAI, or local Ollama with strict Pydantic JSON schema output and untrusted input quarantine.
            </p>
          </div>

          <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-colors space-y-3">
            <div className="p-2.5 w-fit rounded-lg bg-sky-950/50 border border-sky-800/50 text-sky-400">
              <Lock className="w-5 h-5" />
            </div>
            <h3 className="text-base font-semibold text-white">Security & Prompt Injection Defense</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Treats all repository diffs and comments as untrusted input. Protects system instructions from adversarial prompt injection.
            </p>
          </div>
        </div>
      </section>

      {/* Workflow / Architecture Overview */}
      <section className="p-8 rounded-2xl bg-gradient-to-b from-slate-900/80 to-slate-950 border border-slate-800 space-y-6">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <h3 className="text-xl font-bold text-white">How DevGuard Analyzes a Pull Request</h3>
            <p className="text-xs text-slate-400">End-to-end idempotent analysis workflow</p>
          </div>
          <Link
            to="/dashboard"
            className="text-xs font-semibold text-sky-400 hover:text-sky-300 flex items-center"
          >
            Explore Dashboard <ArrowRight className="w-3.5 h-3.5 ml-1" />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pt-4">
          <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 space-y-2">
            <span className="text-xs font-mono text-sky-400 font-semibold">01. INGESTION</span>
            <h4 className="text-sm font-medium text-slate-200">Diff & Metadata Fetch</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Fetches PR commits and raw unified diffs from GitHub REST API with rate-limit retries and size guardrails.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 space-y-2">
            <span className="text-xs font-mono text-sky-400 font-semibold">02. DIFF PARSING</span>
            <h4 className="text-sm font-medium text-slate-200">Hunk & Line Mapping</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Maps old/new line numbers precisely across all hunks to ensure findings link directly to code lines.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 space-y-2">
            <span className="text-xs font-mono text-sky-400 font-semibold">03. HYBRID ANALYSIS</span>
            <h4 className="text-sm font-medium text-slate-200">Rule Engine + AI</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Executes deterministic security rules, secret scanners, bug detectors, and optional sandboxed LLM analysis.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 space-y-2">
            <span className="text-xs font-mono text-sky-400 font-semibold">04. VALIDATION & STORE</span>
            <h4 className="text-sm font-medium text-slate-200">Deduplicate & Persist</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Filters hallucinated lines, deduplicates findings, stores in PostgreSQL, and presents actionable remediations.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};
