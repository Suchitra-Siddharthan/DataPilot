import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { ArrowLeft, ChevronDown, ChevronUp, BarChart3, Brain, CheckCircle, AlertCircle } from 'lucide-react';

const Results = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [showTrace, setShowTrace] = useState(false);
  const [showRaw, setShowRaw] = useState(false);
  const analysis = location.state?.analysis;

  if (!analysis) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="w-16 h-16 mx-auto mb-4 text-gray-400" />
        <h2 className="text-xl font-semibold text-gray-800 mb-2">No Analysis Results</h2>
        <p className="text-gray-600 mb-4">No analysis data available to display</p>
        <button
          onClick={() => navigate('/analyze')}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
        >
          Go to Analyze
        </button>
      </div>
    );
  }

  const question = analysis.question;
  const intent = analysis.intent;
  const confidence = analysis.confidence || 0;
  const selected_tool = analysis.selected_tool || analysis.tool;
  const result = analysis.result;
  const explanation = analysis.explanation || analysis.answer;
  const validation = analysis.validation;
  const trace = analysis.trace;

  // Helper: download array-of-objects as CSV
  const downloadJsonAsCsv = (arr, filename = 'data.csv') => {
    try {
      if (!Array.isArray(arr) || arr.length === 0) return;
      const keys = Array.from(arr.reduce((acc, o) => { Object.keys(o || {}).forEach(k => acc.add(k)); return acc; }, new Set()));
      const header = keys.join(',');
      const lines = arr.map(row => keys.map(k => {
        const v = row[k];
        if (v === null || v === undefined) return '';
        if (typeof v === 'object') return '"' + JSON.stringify(v).replace(/"/g, '""') + '"';
        return '"' + String(v).replace(/"/g, '""') + '"';
      }).join(','));
      const csv = [header, ...lines].join('\n');
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error('Download failed', e);
    }
  };

  const getProcessedDataset = () => {
    const candidates = ['processed_dataset','modified_dataset','updated_dataset','dataset','result_dataset'];
    for (const key of candidates) {
      if (Array.isArray(result[key]) && result[key].length > 0) return result[key];
    }
    return null;
  };

  const getPredictionDataset = () => (
    Array.isArray(result?.prediction_dataset) && result.prediction_dataset.length > 0
      ? result.prediction_dataset
      : null
  );

  const valueToHeatColor = (v) => {
    // v expected in [-1,1]
    const clamp = Math.max(-1, Math.min(1, Number(v) || 0));
    if (clamp > 0) {
      const intensity = Math.round(240 * clamp) + 15; // 15-255
      return `rgb(${intensity},${220 - Math.round(120 * clamp)},${220 - Math.round(120 * clamp)})`;
    } else if (clamp < 0) {
      const intensity = Math.round(240 * -clamp) + 15;
      return `rgb(${220 - Math.round(120 * -clamp)},${220 - Math.round(120 * -clamp)},${intensity})`;
    }
    return '#fff';
  };

  const renderCorrelationHeatmap = (matrixObj) => {
    try {
      const cols = Object.keys(matrixObj || {});
      if (!cols || cols.length === 0) return null;
      return (
        <div>
          <h4 className="font-medium text-gray-700 mb-2">Correlation Heatmap</h4>
          <div className="overflow-auto">
            <table className="border-collapse text-sm">
              <thead>
                <tr>
                  <th className="px-2 py-1"></th>
                  {cols.map((c) => (
                    <th key={c} className="px-2 py-1 text-xs text-gray-600">{c}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {cols.map((r) => (
                  <tr key={r}>
                    <td className="px-2 py-1 text-xs font-medium text-gray-700">{r}</td>
                    {cols.map((c) => {
                      const v = matrixObj[r] && matrixObj[r][c] !== undefined ? Number(matrixObj[r][c]) : 0;
                      return (
                        <td key={c} className="px-1 py-1">
                          <div style={{background: valueToHeatColor(v), width: 48, height: 24, display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: 4}}>
                            <span className="text-xs text-gray-800">{v ? v.toFixed(2) : '-'}</span>
                          </div>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      );
    } catch (e) {
      return null;
    }
  };

  const summaryColumnsToShow = () => {
    if (result?.operation !== 'summary_statistics' || !result?.results) {
      return Object.keys(result?.results || {});
    }

    const questionText = (analysis?.question || '').toLowerCase().replace(/[_-]+/g, ' ');
    const resultKeys = Object.keys(result.results);
    const requested = resultKeys.filter((col) => {
      const normalizedCol = col.toLowerCase().replace(/[_-]+/g, ' ');
      return questionText.includes(normalizedCol) || questionText.includes(normalizedCol.replace(/\s+/g, ''));
    });

    return requested.length > 0 ? requested : resultKeys;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate('/analyze')}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </button>
        <h1 className="text-3xl font-bold text-gray-800">Analysis Results</h1>
      </div>

      {/* Question Card */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Brain className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-semibold">Your Question</h3>
        </div>
        <p className="text-xl text-gray-800">{question}</p>
      </div>

      {/* Analysis Metadata */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center space-x-2 mb-2">
            <Brain className="w-5 h-5 text-purple-600" />
            <h4 className="font-medium text-gray-700">Detected Intent</h4>
          </div>
          <p className="text-lg font-semibold text-purple-700">{intent}</p>
          <p className="text-sm text-gray-500">Confidence: {(confidence * 100).toFixed(1)}%</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center space-x-2 mb-2">
            <BarChart3 className="w-5 h-5 text-blue-600" />
            <h4 className="font-medium text-gray-700">Selected Tool</h4>
          </div>
          <p className="text-lg font-semibold text-blue-700">{selected_tool}</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center space-x-2 mb-2">
            {validation?.success ? (
              <CheckCircle className="w-5 h-5 text-green-600" />
            ) : (
              <AlertCircle className="w-5 h-5 text-red-600" />
            )}
            <h4 className="font-medium text-gray-700">Validation</h4>
          </div>
          <p className={`text-lg font-semibold ${validation?.success ? 'text-green-700' : 'text-red-700'}`}>
            {validation?.success ? 'Successful' : 'Failed'}
          </p>
          <p className="text-sm text-gray-500">{validation?.message}</p>
        </div>
      </div>

      {/* Analysis Result */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-2 mb-4">
          <BarChart3 className="w-5 h-5 text-gray-600" />
          <h3 className="text-lg font-semibold">Analysis Result</h3>
        </div>
        
        {result && typeof result === 'object' ? (
          <div className="space-y-4">
            {result.operation && (
              <div className="p-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700">Operation: </span>
                <span className="text-gray-800">{result.operation}</span>
              </div>
            )}

            {result.operation === 'classification' || result.operation === 'regression' ? (
              <>
                {result.target_column && (
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <span className="font-medium text-gray-700">Target Column: </span>
                    <span className="text-gray-800">{result.target_column}</span>
                  </div>
                )}
                {getPredictionDataset() && (
                  <div className="space-y-3">
                    <button
                      onClick={() => downloadJsonAsCsv(getPredictionDataset(), 'predictions.csv')}
                      className="px-4 py-2 bg-primary-600 text-white rounded-lg"
                    >
                      Download Predictions
                    </button>
                    <div>
                      <h4 className="font-medium text-gray-700 mb-2">Prediction Results</h4>
                      <div className="overflow-auto">
                        <table className="min-w-full text-sm">
                          <thead>
                            <tr className="text-left text-gray-600">
                              <th className="px-2 py-1">Row</th>
                              <th className="px-2 py-1">Predicted Value</th>
                            </tr>
                          </thead>
                          <tbody>
                            {getPredictionDataset().map((row, idx) => (
                              <tr key={idx} className="bg-gray-50 even:bg-white">
                                <td className="px-2 py-2">{idx + 1}</td>
                                <td className="px-2 py-2 font-semibold">{String(row.prediction)}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                )}
              </>
            ) : null}

            {/* Download processed dataset when backend returned an actual dataset object */}
            {result.operation !== 'feature_engineering' && (() => {
              const ds = getProcessedDataset();
              return ds ? (
                <div className="flex items-center space-x-3">
                  <button
                    onClick={() => downloadJsonAsCsv(ds, 'processed_dataset.csv')}
                    className="px-4 py-2 bg-primary-600 text-white rounded-lg"
                  >
                    Download Processed Dataset
                  </button>
                  <span className="text-sm text-gray-500">Backend returned a processed dataset</span>
                </div>
              ) : null;
            })()}
            
            {/* Summary statistics */}
            {result.operation === 'summary_statistics' && result.results && Object.keys(result.results).length > 0 && (
              <div className="space-y-2">
                <h4 className="font-medium text-gray-700">Summary Statistics</h4>
                {Object.entries(result.results)
                  .filter(([col]) => summaryColumnsToShow().includes(col))
                  .map(([col, stats]) => (
                    <div key={col} className="p-3 bg-gray-50 rounded-lg">
                      <div className="font-medium text-gray-800 mb-2">{col}</div>
                      <div className="grid grid-cols-2 gap-2 text-sm text-gray-700">
                        <div>Mean: {stats.mean !== undefined ? Number(stats.mean).toFixed(3) : '-'}</div>
                        <div>Median: {stats.median !== undefined ? Number(stats.median).toFixed(3) : '-'}</div>
                        <div>Min: {stats.min !== undefined ? Number(stats.min).toFixed(3) : '-'}</div>
                        <div>Max: {stats.max !== undefined ? Number(stats.max).toFixed(3) : '-'}</div>
                        <div>Std: {stats.std !== undefined ? Number(stats.std).toFixed(3) : '-'}</div>
                        <div>Count: {stats.count !== undefined ? stats.count : '-'}</div>
                      </div>
                    </div>
                  ))}
              </div>
            )}

            {/* Distribution statistics */}
            {result.operation === 'distribution_analysis' && result.results && Object.keys(result.results).length > 0 && (
              <div className="space-y-2">
                <h4 className="font-medium text-gray-700">Distribution Statistics</h4>
                {Object.entries(result.results).map(([col, stats]) => (
                  <div key={col} className="p-3 bg-gray-50 rounded-lg">
                    <div className="font-medium text-gray-800 mb-2">{col}</div>
                    <div className="grid grid-cols-2 gap-2 text-sm text-gray-700">
                      <div>Mean: {stats.mean !== undefined ? Number(stats.mean).toFixed(3) : '-'}</div>
                      <div>Median: {stats.median !== undefined ? Number(stats.median).toFixed(3) : '-'}</div>
                      <div>Q1: {stats.q25 !== undefined ? Number(stats.q25).toFixed(3) : '-'}</div>
                      <div>Q3: {stats.q75 !== undefined ? Number(stats.q75).toFixed(3) : '-'}</div>
                      <div>IQR: {stats.iqr !== undefined ? Number(stats.iqr).toFixed(3) : '-'}</div>
                      <div>Range: {stats.range !== undefined ? Number(stats.range).toFixed(3) : '-'}</div>
                      <div>Std: {stats.std !== undefined ? Number(stats.std).toFixed(3) : '-'}</div>
                      <div>Skewness: {stats.skewness !== undefined ? Number(stats.skewness).toFixed(3) : '-'}</div>
                      <div>Kurtosis: {stats.kurtosis !== undefined ? Number(stats.kurtosis).toFixed(3) : '-'}</div>
                      <div>Count: {stats.count !== undefined ? stats.count : '-'}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {result.correlations && result.correlations.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-medium text-gray-700">Correlations</h4>
                <div className="overflow-auto">
                  <table className="min-w-full text-sm">
                    <thead>
                      <tr className="text-left text-gray-600">
                        <th className="px-2 py-1">Column X</th>
                        <th className="px-2 py-1">Column Y</th>
                        <th className="px-2 py-1">Correlation</th>
                        <th className="px-2 py-1">Interpretation</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.correlations.map((corr, idx) => (
                        <tr key={idx} className="bg-gray-50 even:bg-white">
                          <td className="px-2 py-2">{corr.column_x}</td>
                          <td className="px-2 py-2">{corr.column_y}</td>
                          <td className="px-2 py-2 font-semibold text-blue-600">{Number(corr.correlation).toFixed(3)}</td>
                          <td className="px-2 py-2 text-gray-600">{corr.interpretation}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
            {result.correlation_matrix && Object.keys(result.correlation_matrix).length > 0 && (
              <div className="mt-3">
                {renderCorrelationHeatmap(result.correlation_matrix)}
              </div>
            )}
            {result.transformations && result.transformations.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-medium text-gray-700">Feature Engineering</h4>
                {result.transformations.map((t, idx) => (
                  <div key={idx} className="p-3 bg-gray-50 rounded-lg">
                    <span className="text-gray-800">{t}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Outlier detailed view */}
            {result.operation === 'outlier_detection' && result.results && Object.keys(result.results).length > 0 && (
              <div className="space-y-2">
                <h4 className="font-medium text-gray-700">Outlier Detection Results</h4>
                {Object.entries(result.results).map(([col, info]) => (
                  <div key={col} className="p-3 bg-gray-50 rounded-lg">
                    <div className="font-medium text-gray-800 mb-1">{col}</div>
                    <div className="grid grid-cols-2 gap-2 text-sm text-gray-700">
                      <div>Method: {info.method || info.detect_method || 'iqr'}</div>
                      <div>Outlier Count: {info.count ?? 0}</div>
                      <div>Lower Bound: {info.lower_bound !== undefined ? Number(info.lower_bound).toFixed(3) : '-'}</div>
                      <div>Upper Bound: {info.upper_bound !== undefined ? Number(info.upper_bound).toFixed(3) : '-'}</div>
                      <div>Percentage: {info.percentage !== undefined ? Number(info.percentage).toFixed(2) + '%' : '-'}</div>
                      <div>Sample Outliers: {Array.isArray(info.outliers) ? info.outliers.slice(0,10).join(', ') : '-'}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {result.new_columns && result.new_columns.length > 0 && (
              <div className="p-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700">New Columns: </span>
                <span className="text-gray-800">{result.new_columns.join(', ')}</span>
              </div>
            )}

            {result.operation === 'data_preprocessing' && result.message && (
              <div className="p-3 bg-green-50 border border-green-200 rounded-lg text-green-800">
                {result.message}
              </div>
            )}

            {result.operations_performed && result.operations_performed.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-medium text-gray-700">Preprocessing Operations</h4>
                {result.operations_performed.map((op, idx) => (
                  <div key={idx} className="p-3 bg-gray-50 rounded-lg">
                    <span className="text-gray-800">{op}</span>
                  </div>
                ))}
              </div>
            )}

            {result.feature_importance && Object.keys(result.feature_importance).length > 0 && (
              <div className="space-y-2">
                <h4 className="font-medium text-gray-700">Feature Importance</h4>
                <div className="overflow-auto">
                  <table className="min-w-full text-sm">
                    <thead>
                      <tr className="text-left text-gray-600">
                        <th className="px-2 py-1">Feature</th>
                        <th className="px-2 py-1">Importance</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(result.feature_importance).map(([k, v]) => (
                        <tr key={k} className="bg-gray-50 even:bg-white">
                          <td className="px-2 py-2">{k}</td>
                          <td className="px-2 py-2 font-semibold">{Number(v).toFixed(6)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {result.accuracy !== undefined && (
              <div className="p-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700">Accuracy: </span>
                <span className="text-gray-800">{Number(result.accuracy).toFixed(3)}</span>
              </div>
            )}

            {result.mse !== undefined && (
              <div className="p-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700">MSE: </span>
                <span className="text-gray-800">{Number(result.mse).toFixed(3)}</span>
              </div>
            )}

            {result.r2_score !== undefined && (
              <div className="p-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700">R²: </span>
                <span className="text-gray-800">{Number(result.r2_score).toFixed(3)}</span>
              </div>
            )}

            {result.operation === 'feature_engineering' && getProcessedDataset() && (
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => downloadJsonAsCsv(getProcessedDataset(), 'processed_dataset.csv')}
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg"
                >
                  Download Processed Dataset
                </button>
                <span className="text-sm text-gray-500">Backend returned a processed dataset</span>
              </div>
            )}

            {result.dataset_shape && (
              <div className="p-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700">Dataset Shape: </span>
                <span className="text-gray-800">{result.dataset_shape.join ? result.dataset_shape.join(' x ') : String(result.dataset_shape)}</span>
              </div>
            )}

            {result.columns_analyzed && result.columns_analyzed.length > 0 && (
              <div className="p-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700">Columns Analyzed: </span>
                <span className="text-gray-800">{result.columns_analyzed.join(', ')}</span>
              </div>
            )}

            {result.success !== undefined && (
              <div className={`p-3 rounded-lg ${result.success ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
                {result.success ? 'Analysis completed successfully' : result.error || 'Analysis failed'}
              </div>
            )}

            {/* Show any other result fields not explicitly rendered */}
            {/* Collapsible raw JSON for any remaining fields */}
            {Object.keys(result).filter(k => !['operation','results','correlations','transformations','new_columns','operations_performed','feature_importance','accuracy','mse','r2_score','dataset_shape','columns_analyzed','success','error'].includes(k)).length > 0 && (
              <div className="mt-2">
                <button
                  onClick={() => setShowRaw(!showRaw)}
                  className="flex items-center justify-between w-full p-2 bg-gray-100 rounded-lg"
                >
                  <span className="font-medium text-gray-700">View Raw Result (JSON)</span>
                  {showRaw ? <ChevronUp className="w-5 h-5 text-gray-600" /> : <ChevronDown className="w-5 h-5 text-gray-600" />}
                </button>
                {showRaw && (
                  <pre className="text-sm bg-gray-50 p-3 rounded-lg overflow-auto mt-2">{JSON.stringify(result, null, 2)}</pre>
                )}
              </div>
            )}
          </div>
        ) : (
          <p className="text-gray-600">{result ? String(result) : 'No result data available'}</p>
        )}
      </div>

      {/* Explanation */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Brain className="w-5 h-5 text-gray-600" />
          <h3 className="text-lg font-semibold">Explanation</h3>
        </div>
        <p className="text-gray-700">{explanation || 'No explanation provided'}</p>
      </div>

      {/* Agent Trace */}
      <div className="bg-white rounded-lg shadow p-6">
        <button
          onClick={() => setShowTrace(!showTrace)}
          className="flex items-center justify-between w-full"
        >
          <div className="flex items-center space-x-2">
            <Brain className="w-5 h-5 text-gray-600" />
            <h3 className="text-lg font-semibold">Agent Reasoning / Execution Trace</h3>
          </div>
          {showTrace ? (
            <ChevronUp className="w-5 h-5 text-gray-600" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-600" />
          )}
        </button>

        {showTrace && trace && trace.length > 0 && (
          <div className="mt-4 space-y-3">
            {trace.map((entry, idx) => (
              <div key={idx} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                <div className="flex-shrink-0 w-6 h-6 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center text-sm font-medium">
                  {idx + 1}
                </div>
                <div className="flex-1">
                  <p className="font-medium text-gray-800">{entry.step || entry.action || 'Step'}</p>
                  <p className="text-sm text-gray-600">{entry.message || entry.detail || JSON.stringify(entry)}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex space-x-4">
        <button
          onClick={() => navigate('/analyze')}
          className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
        >
          Ask Another Question
        </button>
        <button
          onClick={() => navigate('/history')}
          className="px-6 py-3 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300"
        >
          View History
        </button>
      </div>
    </div>
  );
};

export default Results;