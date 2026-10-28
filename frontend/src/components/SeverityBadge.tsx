import React from 'react';
import type { SeverityLevel } from '../types';

interface SeverityBadgeProps {
  severity: SeverityLevel;
  className?: string;
}

export const SeverityBadge: React.FC<SeverityBadgeProps> = ({ severity, className = '' }) => {
  const styles: Record<SeverityLevel, { bg: string; text: string; border: string }> = {
    critical: {
      bg: 'bg-red-950/60',
      text: 'text-red-400',
      border: 'border-red-800/80',
    },
    high: {
      bg: 'bg-orange-950/60',
      text: 'text-orange-400',
      border: 'border-orange-800/80',
    },
    medium: {
      bg: 'bg-amber-950/60',
      text: 'text-amber-400',
      border: 'border-amber-800/80',
    },
    low: {
      bg: 'bg-blue-950/60',
      text: 'text-blue-400',
      border: 'border-blue-800/80',
    },
    info: {
      bg: 'bg-slate-800/80',
      text: 'text-slate-300',
      border: 'border-slate-700',
    },
  };

  const style = styles[severity] || styles.info;

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider border ${style.bg} ${style.text} ${style.border} ${className}`}
    >
      {severity}
    </span>
  );
};
