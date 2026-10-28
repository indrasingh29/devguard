import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import type { Finding } from '../types';
import { SeverityBadge } from '../components/SeverityBadge';
import { CategoryBadge } from '../components/CategoryBadge';
import { SourceBadge } from '../components/SourceBadge';
import { LoadingSpinner } from '../components/LoadingSpinner';
import {
  ArrowLeft,
  FileCode,
  ThumbsUp,
  ThumbsDown,
  EyeOff,
  CheckCircle2,
  Lightbulb,
} from 'lucide-react';

export const FindingDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [finding, setFinding] = useState<Finding | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Feedback state
  const [feedbackType, setFeedbackType] = useState<'helpful' | 'false_positive' | 'ignored' | null>(null);
  const [feedbackComment, setFeedbackComment] = useState<string>('');
  const [submittingFeedback, setSubmittingFeedback] = useState<boolean>(false);
  const [feedbackSuccess, setFeedbackSuccess] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    const loadFinding = async () => {
      if (!id) return;
      try {
        setLoading(true);
        const data = await api.getFinding(Number(id));
        if (isMounted) {
          setFinding(data);
          if (data.feedback_type) {
            setFeedbackType(data.feedback_type as any);
          }
          setError(null);
        }
      } catch (err: any) {
        if (isMounted) setError(err.message || 'Failed to load finding details');
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    loadFinding();
    return () => {
      isMounted = false;
    };
  }, [id]);

  const handleFeedbackSubmit = async (type: 'helpful' | 'false_positive' | 'ignored') => {
    if (!finding) return;
    try {
      setSubmittingFeedback(true);
      await api.submitFeedback({
        finding_id: finding.id,
        feedback_type: type,
        comment: feedbackComment.trim() || undefined,
      });
      setFeedbackType(type);
      setFeedbackSuccess(`Feedback marked as '${type}'. Thank you for improving detection accuracy!`);
    } catch (err: any) {
      setError(err.message || 'Failed to submit feedback');
    } finally {
      setSubmittingFeedback(false);
    }
  };

  if (loading) {
    return <LoadingSpinner label="Loading finding details..." size="lg" />;
  }

  if (error || !finding) {
    return (
      <div className="p-8 text-center space-y-4">
        <div className="p-4 rounded-xl bg-red-950/40 border border-red-800 text-red-300 text-sm max-w-md mx-auto">
          {error || 'Finding not found.'}
        </div>
        <button
          onClick={() => navigate(-1)}
          className="inline-flex items-center text-sm text-sky-400 hover:text-sky-300"
        >
          <ArrowLeft className="w-4 h-4 mr-1" /> Go back
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Navigation breadcrumb */}
      <div>
        <button
          onClick={() => navigate(-1)}
          className="inline-flex items-center text-xs font-semibold text-slate-400 hover:text-white transition-colors mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-1" />
          Back to Review Findings
        </button>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2.5 mb-2">
              <SeverityBadge severity={finding.severity} />
              <CategoryBadge category={finding.category} />
              <SourceBadge source={finding.detection_source} />
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">{finding.title}</h1>
          </div>
          <div className="font-mono text-xs px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 shrink-0">
            Rule: {finding.rule_id}
          </div>
        </div>
      </div>

      {/* Finding Location Card */}
      <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between font-mono text-xs">
        <div className="flex items-center space-x-2 text-slate-200 truncate">
          <FileCode className="w-4 h-4 text-sky-400 shrink-0" />
          <span className="font-semibold">{finding.file_path}</span>
          <span className="text-slate-500">
            (Lines {finding.line_start || 1}{finding.line_end && finding.line_end !== finding.line_start ? `-${finding.line_end}` : ''})
          </span>
        </div>
        <span className="text-slate-400 font-sans text-xs">
          Confidence: <span className="text-sky-400 uppercase font-semibold">{finding.confidence}</span>
        </span>
      </div>

      {/* Explanation & Evidence */}
      <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 space-y-6">
        <div>
          <h2 className="text-sm font-semibold text-white uppercase tracking-wider mb-2">
            Issue Description
          </h2>
          <p className="text-sm text-slate-300 leading-relaxed whitespace-pre-line">
            {finding.message}
          </p>
        </div>

        {/* Evidence Code Snippet */}
        {finding.evidence && (
          <div>
            <h2 className="text-sm font-semibold text-white uppercase tracking-wider mb-2">
              Supporting Evidence
            </h2>
            <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 font-mono text-xs text-rose-300 overflow-x-auto">
              <pre className="whitespace-pre">{finding.evidence}</pre>
            </div>
          </div>
        )}

        {/* Remediation Advice */}
        {finding.suggested_remediation && (
          <div className="p-4 rounded-lg bg-sky-950/40 border border-sky-800/60 space-y-2">
            <h2 className="text-xs font-bold text-sky-300 uppercase tracking-wider flex items-center">
              <Lightbulb className="w-4 h-4 mr-1.5 text-sky-400" />
              Suggested Remediation
            </h2>
            <p className="text-xs text-sky-200 leading-relaxed font-mono whitespace-pre-line">
              {finding.suggested_remediation}
            </p>
          </div>
        )}
      </div>

      {/* Feedback & Quality Audit Card */}
      <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 space-y-4">
        <div>
          <h2 className="text-sm font-semibold text-white">Reviewer Feedback & Quality Audit</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Help improve DevGuard's precision. Your feedback helps benchmark deterministic rule accuracy and prevents false positives.
          </p>
        </div>

        {feedbackSuccess && (
          <div className="p-3 rounded-lg bg-emerald-950/50 border border-emerald-800 text-emerald-300 text-xs flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>{feedbackSuccess}</span>
          </div>
        )}

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={() => handleFeedbackSubmit('helpful')}
            disabled={submittingFeedback}
            className={`flex items-center px-4 py-2 rounded-lg text-xs font-medium border transition-colors ${
              feedbackType === 'helpful'
                ? 'bg-emerald-950 border-emerald-600 text-emerald-300'
                : 'bg-slate-950 border-slate-800 text-slate-300 hover:border-slate-700'
            }`}
          >
            <ThumbsUp className="w-3.5 h-3.5 mr-1.5 text-emerald-400" />
            Helpful Finding
          </button>

          <button
            onClick={() => handleFeedbackSubmit('false_positive')}
            disabled={submittingFeedback}
            className={`flex items-center px-4 py-2 rounded-lg text-xs font-medium border transition-colors ${
              feedbackType === 'false_positive'
                ? 'bg-rose-950 border-rose-600 text-rose-300'
                : 'bg-slate-950 border-slate-800 text-slate-300 hover:border-slate-700'
            }`}
          >
            <ThumbsDown className="w-3.5 h-3.5 mr-1.5 text-rose-400" />
            False Positive
          </button>

          <button
            onClick={() => handleFeedbackSubmit('ignored')}
            disabled={submittingFeedback}
            className={`flex items-center px-4 py-2 rounded-lg text-xs font-medium border transition-colors ${
              feedbackType === 'ignored'
                ? 'bg-slate-800 border-slate-600 text-slate-200'
                : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
            }`}
          >
            <EyeOff className="w-3.5 h-3.5 mr-1.5 text-slate-400" />
            Ignore / Accept Risk
          </button>
        </div>

        <div>
          <textarea
            placeholder="Optional comment on this finding (e.g. why it's a false positive or intentional design)..."
            value={feedbackComment}
            onChange={(e) => setFeedbackComment(e.target.value)}
            rows={2}
            className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
          />
        </div>
      </div>
    </div>
  );
};
