import React from 'react';
import type { DetectionSource } from '../types';
import { Cpu, Sparkles } from 'lucide-react';

interface SourceBadgeProps {
  source: DetectionSource;
  className?: string;
}

export const SourceBadge: React.FC<SourceBadgeProps> = ({ source, className = '' }) => {
  const isLLM = source === 'llm_suggestion';

  if (isLLM) {
    return (
      <span
        title="Model-generated suggestion (requires developer verification)"
        className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-indigo-950/60 text-indigo-300 border border-indigo-700/60 ${className}`}
      >
        <Sparkles className="w-3 h-3 mr-1 text-indigo-400" />
        AI Suggestion
      </span>
    );
  }

  const labelMap: Record<DetectionSource, string> = {
    deterministic: 'Deterministic Rule',
    bandit: 'Bandit Security',
    ast_check: 'AST Syntax Check',
    regex_secret: 'Entropy & Secret Rule',
    quality_linter: 'Code Quality Linter',
    llm_suggestion: 'AI Suggestion',
  };

  return (
    <span
      title="Verified deterministic static analysis rule"
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-950/60 text-emerald-300 border border-emerald-700/60 ${className}`}
    >
      <Cpu className="w-3 h-3 mr-1 text-emerald-400" />
      {labelMap[source] || 'Deterministic Rule'}
    </span>
  );
};
