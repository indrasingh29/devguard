import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { SeverityBadge } from '../components/SeverityBadge';
import { CategoryBadge } from '../components/CategoryBadge';
import { SourceBadge } from '../components/SourceBadge';
import { StatusBadge } from '../components/StatusBadge';
import { DiffViewer } from '../components/DiffViewer';
import type { ChangedFile, Finding } from '../types';

describe('UI Badges and Components', () => {
  it('renders severity badge correctly for critical', () => {
    render(<SeverityBadge severity="critical" />);
    expect(screen.getByText('critical')).toBeInTheDocument();
  });

  it('renders category badge correctly for security and secret leaks', () => {
    const { rerender } = render(<CategoryBadge category="security" />);
    expect(screen.getByText('Security')).toBeInTheDocument();

    rerender(<CategoryBadge category="secret_leak" />);
    expect(screen.getByText('Secret Leak')).toBeInTheDocument();
  });

  it('clearly distinguishes deterministic findings from AI suggestions', () => {
    const { rerender } = render(<SourceBadge source="deterministic" />);
    expect(screen.getByText('Deterministic Rule')).toBeInTheDocument();

    rerender(<SourceBadge source="llm_suggestion" />);
    expect(screen.getByText('AI Suggestion')).toBeInTheDocument();
  });

  it('renders review status badge properly', () => {
    const { rerender } = render(<StatusBadge status="COMPLETED" />);
    expect(screen.getByText('Completed')).toBeInTheDocument();

    rerender(<StatusBadge status="FAILED" />);
    expect(screen.getByText('Failed')).toBeInTheDocument();
  });

  it('renders DiffViewer with file path, hunks, and inline findings', () => {
    const mockFile: ChangedFile = {
      path: 'app/auth.py',
      change_type: 'modified',
      additions: 1,
      deletions: 0,
      hunks: [
        {
          old_start: 1,
          old_length: 2,
          new_start: 1,
          new_length: 3,
          header: '@@ -1,2 +1,3 @@',
          lines: [' context line', '+api_key = "AKIA1234567890EXAMPLE"'],
        },
      ],
      is_binary: false,
    };

    const mockFinding: Finding = {
      id: 101,
      review_job_id: 1,
      file_path: 'app/auth.py',
      line_start: 2,
      severity: 'critical',
      category: 'secret_leak',
      title: 'Hardcoded AWS Key',
      message: 'AWS key detected on line 2',
      detection_source: 'regex_secret',
      confidence: 'deterministic',
      rule_id: 'SEC-001',
      created_at: new Date().toISOString(),
    };

    render(<DiffViewer file={mockFile} findings={[mockFinding]} />);

    expect(screen.getByText('app/auth.py')).toBeInTheDocument();
    expect(screen.getByText('Hardcoded AWS Key')).toBeInTheDocument();
    expect(screen.getByText('AWS key detected on line 2')).toBeInTheDocument();
  });
});
