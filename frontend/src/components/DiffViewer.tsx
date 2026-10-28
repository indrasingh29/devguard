import React, { useState } from 'react';
import type { ChangedFile, Finding } from '../types';
import { SeverityBadge } from './SeverityBadge';
import { CategoryBadge } from './CategoryBadge';
import { SourceBadge } from './SourceBadge';
import { FileCode, ChevronDown, ChevronRight, AlertCircle } from 'lucide-react';

interface DiffViewerProps {
  file: ChangedFile;
  findings?: Finding[];
  onSelectFinding?: (finding: Finding) => void;
}

export const DiffViewer: React.FC<DiffViewerProps> = ({
  file,
  findings = [],
  onSelectFinding,
}) => {
  const [isExpanded, setIsExpanded] = useState<boolean>(true);

  // Group findings by line number for this file
  const findingsByLine: Record<number, Finding[]> = {};
  findings.forEach((f) => {
    if (f.file_path === file.path && f.line_start) {
      if (!findingsByLine[f.line_start]) {
        findingsByLine[f.line_start] = [];
      }
      findingsByLine[f.line_start].push(f);
    }
  });

  return (
    <div className="border border-slate-800 rounded-lg overflow-hidden bg-slate-900/90 mb-4 shadow-sm">
      {/* File Header */}
      <div
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center justify-between px-4 py-3 bg-slate-800/80 cursor-pointer hover:bg-slate-800 border-b border-slate-800 transition-colors select-none"
      >
        <div className="flex items-center space-x-2.5">
          {isExpanded ? (
            <ChevronDown className="w-4 h-4 text-slate-400" />
          ) : (
            <ChevronRight className="w-4 h-4 text-slate-400" />
          )}
          <FileCode className="w-4 h-4 text-sky-400" />
          <span className="font-mono text-sm text-slate-200 font-medium">{file.path}</span>
          {file.change_type !== 'modified' && (
            <span className="text-xs px-2 py-0.5 rounded bg-slate-700/60 text-slate-300 capitalize">
              {file.change_type}
            </span>
          )}
        </div>

        <div className="flex items-center space-x-3 text-xs font-mono">
          {findings.length > 0 && (
            <span className="flex items-center px-2 py-0.5 rounded-full bg-red-950/60 text-red-400 border border-red-800/60 font-sans">
              <AlertCircle className="w-3.5 h-3.5 mr-1" />
              {findings.length} issue{findings.length > 1 ? 's' : ''}
            </span>
          )}
          <span className="text-emerald-400 font-medium">+{file.additions}</span>
          <span className="text-rose-400 font-medium">-{file.deletions}</span>
        </div>
      </div>

      {/* Diff Content */}
      {isExpanded && (
        <div className="overflow-x-auto font-mono text-xs leading-5">
          {file.is_binary ? (
            <div className="p-4 text-slate-400 italic">Binary file not shown</div>
          ) : file.hunks.length === 0 ? (
            <div className="p-4 text-slate-400 italic">No text changes</div>
          ) : (
            file.hunks.map((hunk, hIdx) => {
              let currentOldLine = hunk.old_start;
              let currentNewLine = hunk.new_start;

              return (
                <div key={hIdx} className="border-b border-slate-800/50 last:border-b-0">
                  {/* Hunk Header */}
                  <div className="bg-slate-950/80 text-slate-400 px-4 py-1 select-none font-semibold border-y border-slate-800/60">
                    {hunk.header}
                  </div>

                  {/* Hunk Lines */}
                  {hunk.lines.map((line, lIdx) => {
                    const isAddition = line.startsWith('+');
                    const isDeletion = line.startsWith('-');
                    
                    let oldLineDisplay: number | string = '';
                    let newLineDisplay: number | string = '';
                    let lineNumberForFindings: number | null = null;

                    if (isAddition) {
                      newLineDisplay = currentNewLine;
                      lineNumberForFindings = currentNewLine;
                      currentNewLine++;
                    } else if (isDeletion) {
                      oldLineDisplay = currentOldLine;
                      currentOldLine++;
                    } else {
                      oldLineDisplay = currentOldLine;
                      newLineDisplay = currentNewLine;
                      lineNumberForFindings = currentNewLine;
                      currentOldLine++;
                      currentNewLine++;
                    }

                    const lineFindings = lineNumberForFindings ? findingsByLine[lineNumberForFindings] : null;

                    return (
                      <React.Fragment key={lIdx}>
                        <div
                          className={`flex items-start group hover:bg-slate-800/40 transition-colors ${
                            isAddition
                              ? 'bg-emerald-950/20 text-emerald-100'
                              : isDeletion
                              ? 'bg-rose-950/20 text-rose-100'
                              : 'text-slate-300'
                          } ${lineFindings ? 'border-l-4 border-amber-500 bg-amber-950/20' : ''}`}
                        >
                          {/* Line numbers */}
                          <div className="flex select-none text-slate-400 w-24 shrink-0 text-right pr-3 bg-slate-950/40 border-r border-slate-800/60 py-0.5">
                            <span className="w-1/2 pr-2">{oldLineDisplay}</span>
                            <span className="w-1/2">{newLineDisplay}</span>
                          </div>

                          {/* Line code */}
                          <div className="px-3 py-0.5 whitespace-pre flex-1 overflow-x-auto">
                            <span
                              className={`select-none inline-block w-4 font-bold ${
                                isAddition ? 'text-emerald-400' : isDeletion ? 'text-rose-400' : 'text-slate-400'
                              }`}
                            >
                              {line[0]}
                            </span>
                            {line.slice(1)}
                          </div>
                        </div>

                        {/* Inline Findings Card if issues flagged on this line */}
                        {lineFindings && (
                          <div className="bg-slate-900 border-y border-amber-800/60 px-4 py-3 pl-28 space-y-2">
                            {lineFindings.map((finding) => (
                              <div
                                key={finding.id}
                                onClick={() => onSelectFinding?.(finding)}
                                className="p-3 bg-slate-800/90 rounded-lg border border-slate-700/80 cursor-pointer hover:border-amber-600 transition-all font-sans text-sm shadow-md"
                              >
                                <div className="flex items-center justify-between mb-1.5 flex-wrap gap-2">
                                  <div className="flex items-center space-x-2">
                                    <SeverityBadge severity={finding.severity} />
                                    <CategoryBadge category={finding.category} />
                                    <SourceBadge source={finding.detection_source} />
                                  </div>
                                  <span className="text-xs font-mono text-slate-400">Rule: {finding.rule_id}</span>
                                </div>
                                <h4 className="font-semibold text-slate-100 mb-1">{finding.title}</h4>
                                <p className="text-xs text-slate-300 leading-relaxed mb-2">{finding.message}</p>
                                {finding.suggested_remediation && (
                                  <div className="text-xs bg-slate-900/80 p-2.5 rounded border border-slate-800 text-sky-300 font-mono">
                                    <span className="text-slate-400 block font-sans font-semibold mb-1">
                                      Suggested Remediation:
                                    </span>
                                    {finding.suggested_remediation}
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        )}
                      </React.Fragment>
                    );
                  })}
                </div>
              );
            })
          )}
        </div>
      )}
    </div>
  );
};
