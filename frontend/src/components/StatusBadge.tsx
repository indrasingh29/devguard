import React from 'react';
import type { ReviewStatus } from '../types';
import { CheckCircle2, Clock, AlertOctagon, Loader2 } from 'lucide-react';

interface StatusBadgeProps {
  status: ReviewStatus;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className = '' }) => {
  const configs: Record<ReviewStatus, { label: string; icon: React.ReactNode; color: string }> = {
    COMPLETED: {
      label: 'Completed',
      icon: <CheckCircle2 className="w-3.5 h-3.5 mr-1" />,
      color: 'bg-emerald-950/60 text-emerald-300 border-emerald-800/80',
    },
    PROCESSING: {
      label: 'Processing',
      icon: <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" />,
      color: 'bg-blue-950/60 text-blue-300 border-blue-800/80',
    },
    QUEUED: {
      label: 'Queued',
      icon: <Clock className="w-3.5 h-3.5 mr-1" />,
      color: 'bg-slate-800 text-slate-300 border-slate-700',
    },
    FAILED: {
      label: 'Failed',
      icon: <AlertOctagon className="w-3.5 h-3.5 mr-1" />,
      color: 'bg-red-950/60 text-red-300 border-red-800/80',
    },
  };

  const config = configs[status] || configs.QUEUED;

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${config.color} ${className}`}
    >
      {config.icon}
      {config.label}
    </span>
  );
};
