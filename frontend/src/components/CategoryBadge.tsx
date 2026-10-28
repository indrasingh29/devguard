import React from 'react';
import type { FindingCategory } from '../types';
import { ShieldAlert, Bug, AlertTriangle, Wrench, FileQuestion, Key } from 'lucide-react';

interface CategoryBadgeProps {
  category: FindingCategory;
  className?: string;
}

export const CategoryBadge: React.FC<CategoryBadgeProps> = ({ category, className = '' }) => {
  const configs: Record<FindingCategory, { label: string; icon: React.ReactNode; color: string }> = {
    security: {
      label: 'Security',
      icon: <ShieldAlert className="w-3.5 h-3.5 mr-1" />,
      color: 'bg-red-950/40 text-red-300 border-red-800/40',
    },
    secret_leak: {
      label: 'Secret Leak',
      icon: <Key className="w-3.5 h-3.5 mr-1" />,
      color: 'bg-rose-950/40 text-rose-300 border-rose-800/40',
    },
    bug_risk: {
      label: 'Bug Risk',
      icon: <Bug className="w-3.5 h-3.5 mr-1" />,
      color: 'bg-amber-950/40 text-amber-300 border-amber-800/40',
    },
    error_handling: {
      label: 'Error Handling',
      icon: <AlertTriangle className="w-3.5 h-3.5 mr-1" />,
      color: 'bg-yellow-950/40 text-yellow-300 border-yellow-800/40',
    },
    maintainability: {
      label: 'Code Quality',
      icon: <Wrench className="w-3.5 h-3.5 mr-1" />,
      color: 'bg-purple-950/40 text-purple-300 border-purple-800/40',
    },
    test_insufficiency: {
      label: 'Missing Tests',
      icon: <FileQuestion className="w-3.5 h-3.5 mr-1" />,
      color: 'bg-cyan-950/40 text-cyan-300 border-cyan-800/40',
    },
  };

  const config = configs[category] || {
    label: category,
    icon: null,
    color: 'bg-slate-800 text-slate-300 border-slate-700',
  };

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium border ${config.color} ${className}`}
    >
      {config.icon}
      {config.label}
    </span>
  );
};
