import React, { useState, useEffect } from 'react';
import Prism from 'prismjs';
import 'prismjs/themes/prism-tomorrow.css';
import 'prismjs/components/prism-typescript';
import 'prismjs/components/prism-jsx';
import 'prismjs/components/prism-tsx';
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-json';

interface DiffLineHalf {
  lineNum: number | null;
  content: string | null;
}

interface DiffRowPairData {
  type: 'equal' | 'insert' | 'delete' | 'replace';
  left: DiffLineHalf | null;
  right: DiffLineHalf | null;
}

interface DiffFileData {
  filename: string;
  status: 'modified' | 'added' | 'deleted';
  rowPairs: DiffRowPairData[];
  isVirtualTests?: boolean;
}

const getLanguage = (filename: string): string => {
  const ext = filename.split('.').pop()?.toLowerCase();
  switch (ext) {
    case 'ts':
    case 'tsx':
      return 'tsx';
    case 'js':
    case 'jsx':
      return 'jsx';
    case 'py':
      return 'python';
    case 'css':
      return 'css';
    case 'json':
      return 'json';
    case 'html':
      return 'markup';
    default:
      return 'javascript';
  }
};

const highlightCode = (content: string | null, lang: string) => {
  if (content === null) return ' ';
  try {
    const grammar = Prism.languages[lang] || Prism.languages.javascript;
    const html = Prism.highlight(content, grammar, lang);
    return <span dangerouslySetInnerHTML={{ __html: html }} />;
  } catch (e) {
    return content;
  }
};

const DiffViewer = ({ ticketId }: { ticketId: string }) => {
  const [diffFiles, setDiffFiles] = useState<DiffFileData[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedFiles, setExpandedFiles] = useState<Record<string, boolean>>({});
  const [visibleLines, setVisibleLines] = useState<Record<string, boolean[]>>({});

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetch(`/api/diff-files/${ticketId}`)
      .then(res => res.json())
      .then((data: { files?: DiffFileData[]; error?: string }) => {
        if (data.error) {
          setError(data.error);
          setLoading(false);
          return;
        }
        const filesData = data.files || [];
        setDiffFiles(filesData);

        const initialVisible: Record<string, boolean[]> = {};

        filesData.forEach((file) => {
          const pairs = file.rowPairs || [];
          const visibility = pairs.map((pair, pairIdx) => {
            if (pair.type !== 'equal') return true;
            
            for (let offset = -10; offset <= 10; offset++) {
              const checkIdx = pairIdx + offset;
              if (checkIdx >= 0 && checkIdx < pairs.length) {
                if (pairs[checkIdx].type !== 'equal') return true;
              }
            }
            return false;
          });
          initialVisible[file.filename] = visibility;
        });

        setVisibleLines(initialVisible);
        setExpandedFiles({}); // Reset expanded states on ticket change
        setLoading(false);
      })
      .catch(e => {
        setError(String(e));
        setLoading(false);
      });
  }, [ticketId]);

  const toggleFileExpand = (filename: string) => {
    setExpandedFiles(prev => {
      const isCurrentlyExpanded = prev[filename] !== undefined
        ? prev[filename]
        : diffFiles.findIndex(f => f.filename === filename) === 0;
      return { ...prev, [filename]: !isCurrentlyExpanded };
    });
  };

  const expandLines = (filename: string, start: number, end: number) => {
    setVisibleLines(prev => {
      const current = prev[filename] ? [...prev[filename]] : [];
      for (let i = start; i <= end; i++) {
        current[i] = true;
      }
      return { ...prev, [filename]: current };
    });
  };

  if (loading) {
    return <div className="text-muted" style={{ padding: '1rem' }}>Loading code diffs...</div>;
  }

  if (error) {
    return (
      <div style={{ color: 'var(--accent-danger)', padding: '1rem', background: 'rgba(239,68,68,0.1)', borderRadius: '6px', border: '1px solid var(--accent-danger)' }}>
        Error loading diff: {error}
      </div>
    );
  }

  if (diffFiles.length === 0) {
    return <div className="text-muted" style={{ padding: '1rem' }}>No code changes found.</div>;
  }

  return (
    <div className="diff-container" style={{ marginBottom: '1.5rem' }}>
      {diffFiles.map(file => {
        const isExpanded = expandedFiles[file.filename] !== undefined
          ? expandedFiles[file.filename]
          : diffFiles.findIndex(f => f.filename === file.filename) === 0;
        const rowPairs = file.rowPairs || [];
        const visibility = visibleLines[file.filename] || [];
        const lang = getLanguage(file.filename);

        const insertions = rowPairs.filter(p => (p.type === 'insert' || p.type === 'replace') && p.right !== null).length;
        const deletions = rowPairs.filter(p => (p.type === 'delete' || p.type === 'replace') && p.left !== null).length;

        const getStatusBadge = () => {
          switch (file.status) {
            case 'added':
              return <span className="badge" style={{ background: 'rgba(16, 185, 129, 0.2)', color: '#4ade80', border: '1px solid #10b981' }}>Added</span>;
            case 'deleted':
              return <span className="badge" style={{ background: 'rgba(239, 68, 68, 0.2)', color: '#f87171', border: '1px solid #ef4444' }}>Deleted</span>;
            default:
              return <span className="badge" style={{ background: 'rgba(99, 102, 241, 0.2)', color: '#818cf8', border: '1px solid #6366f1' }}>Modified</span>;
          }
        };

        return (
          <div key={file.filename} className={`diff-file-section ${isExpanded ? 'expanded' : ''}`}>
            <div className="diff-file-bar" onClick={() => toggleFileExpand(file.filename)}>
              <div className="diff-file-info">
                <span className="diff-file-toggle">{isExpanded ? '▼' : '▶'}</span>
                <span className="diff-file-name">{file.filename}</span>
                {getStatusBadge()}
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem', fontSize: '0.85rem' }}>
                {insertions > 0 && <span style={{ color: '#4ade80', fontWeight: 'bold' }}>+{insertions}</span>}
                {deletions > 0 && <span style={{ color: '#f87171', fontWeight: 'bold' }}>-{deletions}</span>}
              </div>
            </div>

            {isExpanded && (
              <div className="diff-table-wrapper">
                <table className="diff-table">
                  <tbody>
                    {(() => {
                      const rows: React.ReactNode[] = [];
                      for (let i = 0; i < rowPairs.length; i++) {
                        if (visibility[i]) {
                          const pair = rowPairs[i];
                          const left = pair.left;
                          const right = pair.right;

                          let leftClass = 'diff-cell-equal';
                          if (pair.type === 'delete' || pair.type === 'replace') {
                            if (left) leftClass = 'diff-cell-delete';
                          }
                          
                          let rightClass = 'diff-cell-equal';
                          if (pair.type === 'insert' || pair.type === 'replace') {
                            if (right) rightClass = 'diff-cell-insert';
                          }

                          rows.push(
                            <tr key={i} className="diff-row-pair">
                              <td className={`diff-line-num ${leftClass}-num`}>{left?.lineNum ?? ''}</td>
                              <td className={`diff-line-code ${leftClass}-code`}>
                                <pre className="diff-pre">{left ? highlightCode(left.content, lang) : ' '}</pre>
                              </td>
                              <td className={`diff-line-num ${rightClass}-num`}>{right?.lineNum ?? ''}</td>
                              <td className={`diff-line-code ${rightClass}-code`}>
                                <pre className="diff-pre">{right ? highlightCode(right.content, lang) : ' '}</pre>
                              </td>
                            </tr>
                          );
                        } else {
                          let start = i;
                          while (i < rowPairs.length && !visibility[i]) {
                            i++;
                          }
                          const end = i - 1;
                          const count = end - start + 1;
                          i--;

                          const isAtTop = start === 0;
                          const isAtBottom = end === rowPairs.length - 1;

                          let showTopBar = false;
                          let showBottomBar = false;
                          let showPlaceholder = false;

                          if (isAtTop && isAtBottom) {
                            showTopBar = true;
                          } else if (isAtTop) {
                            showBottomBar = true;
                          } else if (isAtBottom) {
                            showTopBar = true;
                          } else {
                            showTopBar = true;
                            showBottomBar = true;
                            showPlaceholder = true;
                          }

                          rows.push(
                            <tr key={`expand-${start}`} className="diff-expand-row">
                              <td colSpan={4} className="diff-expand-cell">
                                <div className="diff-expand-container">
                                  {showTopBar && (
                                    <div className="diff-expand-bar diff-expand-bar-down">
                                      {count > 10 && (
                                        <button 
                                          className="btn-expand"
                                          onClick={(e) => {
                                            e.stopPropagation();
                                            expandLines(file.filename, start, start + 9);
                                          }}
                                        >
                                          ▼ +10 lines
                                        </button>
                                      )}
                                      {count > 0 && (
                                        <button 
                                          className="btn-expand btn-expand-all"
                                          onClick={(e) => {
                                            e.stopPropagation();
                                            expandLines(file.filename, start, end);
                                          }}
                                        >
                                          ▼ +{count} common lines
                                        </button>
                                      )}
                                    </div>
                                  )}

                                  {showPlaceholder && (
                                    <div className="diff-expand-placeholder">
                                      ↕ {count} common lines hidden
                                    </div>
                                  )}

                                  {showBottomBar && (
                                    <div className="diff-expand-bar diff-expand-bar-up">
                                      {count > 0 && (
                                        <button 
                                          className="btn-expand btn-expand-all"
                                          onClick={(e) => {
                                            e.stopPropagation();
                                            expandLines(file.filename, start, end);
                                          }}
                                        >
                                          ▲ +{count} common lines
                                        </button>
                                      )}
                                      {count > 10 && (
                                        <button 
                                          className="btn-expand"
                                          onClick={(e) => {
                                            e.stopPropagation();
                                            expandLines(file.filename, end - 9, end);
                                          }}
                                        >
                                          ▲ +10 lines
                                        </button>
                                      )}
                                    </div>
                                  )}
                                </div>
                              </td>
                            </tr>
                          );
                        }
                      }
                      return rows;
                    })()}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};