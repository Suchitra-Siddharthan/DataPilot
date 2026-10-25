import React from 'react';

const formatValue = (value, digits = 3) => {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value.toFixed(digits);
  }
  if (value === null || value === undefined || value === '') return '—';
  return String(value);
};

const ResultCard = ({ title, children }) => (
  <section className="rounded-lg bg-gray-50 p-4">
    {title && <h4 className="mb-3 font-medium text-gray-800">{title}</h4>}
    {children}
  </section>
);

const requestedSummaryMetrics = (question) => {
  const text = (question || '').toLowerCase().replace(/[_-]+/g, ' ');
  const metricTerms = {
    mean: /\b(mean|average|avg)\b/,
    median: /\bmedian\b/,
    min: /\b(minimum|min)\b/,
    max: /\b(maximum|max)\b/,
    std: /\b(standard deviation|standard dev|std)\b/,
    count: /\b(count|number of)\b/
  };
  const requested = Object.entries(metricTerms)
    .filter(([, pattern]) => pattern.test(text))
    .map(([metric]) => metric);

  return requested.length ? requested : ['mean'];
};

const SummaryStatisticsResult = ({ result, question }) => {
  const columns = Object.entries(result.results || {});
  const metrics = requestedSummaryMetrics(question);
  if (!columns.length) {
    return <p className="text-sm text-gray-600">No summary statistics were returned.</p>;
  }

  return (
    <div className="space-y-3">
      {columns.map(([column, stats]) => {
        const grouped = stats?.type === 'grouped' && stats.statistics;
        const means = grouped ? stats.statistics.mean || {} : {};
        const highest = Object.entries(means).sort((a, b) => Number(b[1]) - Number(a[1]))[0];
        const groupedMetrics = grouped
          ? metrics.filter((metric) => stats.statistics[metric])
          : [];
        const groups = grouped
          ? Object.keys(stats.statistics[groupedMetrics[0]] || {})
          : [];
        const metricLabel = (metric) => ({
          mean: 'Average',
          median: 'Median',
          min: 'Minimum',
          max: 'Maximum',
          std: 'Standard deviation',
          count: 'Count'
        }[metric] || metric);
        const title = grouped
          ? `${groupedMetrics.map(metricLabel).join(', ') || 'Summary'} ${column} by ${stats.group_by || 'group'}`
          : column;
        return (
          <ResultCard key={column} title={title}>
            {grouped ? (
              <>
                {metrics.includes('mean') && highest && (
                  <p className="mb-3 rounded bg-green-50 p-3 font-semibold text-green-800">
                    Highest mean: {highest[0]} ({formatValue(highest[1])})
                  </p>
                )}
                {groupedMetrics.length > 0 && groups.length > 0 ? <div className="overflow-auto">
                  <table className="min-w-full text-sm">
                    <thead>
                      <tr className="text-left text-gray-600">
                        <th className="px-2 py-1">{stats.group_by || 'Group'}</th>
                        {groupedMetrics.map((metric) => (
                          <th key={metric} className="px-2 py-1 capitalize">{metric}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {groups.map((group) => (
                        <tr key={group} className="border-t border-gray-200">
                          <td className="px-2 py-2 font-medium">{group}</td>
                          {groupedMetrics.map((metric) => (
                            <td key={metric} className="px-2 py-2">
                              {formatValue(stats.statistics[metric]?.[group])}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div> : <p className="text-sm text-gray-600">No requested grouped statistics were returned.</p>}
              </>
            ) : (
              <dl className="grid grid-cols-2 gap-2 text-sm text-gray-700 md:grid-cols-3">
                {metrics.map((metric) => (
                  stats?.[metric] !== undefined && (
                    <div key={metric}>
                      <dt className="text-gray-500">{metricLabel(metric)}</dt>
                      <dd className="font-medium">{formatValue(stats[metric])}</dd>
                    </div>
                  )
                ))}
              </dl>
            )}
          </ResultCard>
        );
      })}
    </div>
  );
};

const CorrelationResult = ({ result, question }) => {
  const correlations = Array.isArray(result.correlations) ? result.correlations : [];
  const normalizedQuestion = (question || '').toLowerCase();
  const requested = correlations.filter((item) => (
    item?.column_x && item?.column_y &&
    normalizedQuestion.includes(String(item.column_x).toLowerCase()) &&
    normalizedQuestion.includes(String(item.column_y).toLowerCase())
  ));
  const displayed = requested.length ? requested : correlations;

  if (!displayed.length) {
    return <p className="text-sm text-gray-600">No valid column correlations were returned.</p>;
  }

  return (
    <div className="space-y-3">
      {displayed.map((item, index) => (
        <ResultCard key={`${item.column_x}-${item.column_y}-${index}`}>
          <p className="text-lg font-semibold text-gray-800">
            {item.column_x} and {item.column_y}
          </p>
          <p className="mt-1 text-2xl font-bold text-blue-700">
            {formatValue(item.correlation)}
          </p>
          <p className="text-sm text-gray-600">
            {item.interpretation || 'Pearson correlation'}
          </p>
        </ResultCard>
      ))}
      {result.correlation_matrix && (
        <CorrelationHeatmap matrix={result.correlation_matrix} />
      )}
    </div>
  );
};

const CorrelationHeatmap = ({ matrix }) => {
  const columns = Object.keys(matrix || {});
  if (!columns.length) return null;
  const colorFor = (value) => {
    const number = Math.max(-1, Math.min(1, Number(value) || 0));
    if (number > 0) return `rgb(255, ${Math.round(220 - 120 * number)}, ${Math.round(220 - 120 * number)})`;
    if (number < 0) return `rgb(${Math.round(220 - 120 * Math.abs(number))}, ${Math.round(220 - 120 * Math.abs(number))}, 255)`;
    return '#fff';
  };

  return (
    <ResultCard title="Correlation heatmap">
      <div className="overflow-auto">
        <table className="border-collapse text-sm">
          <thead>
            <tr>
              <th className="px-2 py-1" />
              {columns.map((column) => <th key={column} className="px-2 py-1 text-xs text-gray-600">{column}</th>)}
            </tr>
          </thead>
          <tbody>
            {columns.map((row) => (
              <tr key={row}>
                <td className="px-2 py-1 text-xs font-medium text-gray-700">{row}</td>
                {columns.map((column) => {
                  const value = matrix[row]?.[column];
                  return (
                    <td key={column} className="px-1 py-1">
                      <div className="flex h-6 w-12 items-center justify-center rounded" style={{ background: colorFor(value) }}>
                        <span className="text-xs text-gray-800">{value === undefined ? '—' : formatValue(Number(value), 2)}</span>
                      </div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </ResultCard>
  );
};

const DistributionResult = ({ result }) => {
  const entries = Object.entries(result.results || {});
  const visualizations = Array.isArray(result.visualizations) ? result.visualizations : [];
  if (!entries.length && !visualizations.length) {
    return <p className="text-sm text-gray-600">No distribution statistics were returned.</p>;
  }

  return (
    <div className="space-y-4">
      {entries.map(([column, stats]) => {
        const histogram = visualizations.find((visual) => visual?.parameters?.column === column);
        return (
          <ResultCard key={column} title={`${column} distribution`}>
            <dl className="grid grid-cols-2 gap-2 text-sm md:grid-cols-3">
              {['mean', 'median', 'min', 'max', 'q25', 'q75', 'iqr', 'range', 'std', 'skewness', 'kurtosis', 'count'].map((key) => (
                stats?.[key] !== undefined && (
                  <div key={key}>
                    <dt className="capitalize text-gray-500">{key}</dt>
                    <dd className="font-medium">{formatValue(stats[key])}</dd>
                  </div>
                )
              ))}
            </dl>
            {stats.skewness_interpretation && (
              <p className="mt-3 text-sm text-gray-600">{stats.skewness_interpretation}</p>
            )}
            {histogram?.image && (
              <img
                className="mt-4 h-auto max-w-full rounded-lg"
                src={`data:image/png;base64,${histogram.image}`}
                alt={histogram.title || `Histogram of ${column}`}
              />
            )}
          </ResultCard>
        );
      })}
    </div>
  );
};

const ValueView = ({ value }) => {
  if (value === null || value === undefined) return <span className="text-gray-500">Not provided</span>;
  if (Array.isArray(value)) {
    if (!value.length) return <span className="text-gray-500">No items</span>;
    if (value.every((item) => item && typeof item === 'object' && !Array.isArray(item))) {
      const keys = [...new Set(value.flatMap((item) => Object.keys(item)))];
      return (
        <div className="overflow-auto">
          <table className="min-w-full text-sm">
            <thead><tr>{keys.map((key) => <th key={key} className="px-2 py-1 text-left text-gray-600">{key}</th>)}</tr></thead>
            <tbody>
              {value.map((row, index) => (
                <tr key={index} className="border-t border-gray-200">
                  {keys.map((key) => <td key={key} className="px-2 py-2">{formatValue(row[key])}</td>)}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }
    return <ul className="list-inside list-disc space-y-1">{value.map((item, index) => <li key={index}><ValueView value={item} /></li>)}</ul>;
  }
  if (typeof value === 'object') {
    return (
      <dl className="space-y-2">
        {Object.entries(value).map(([key, nested]) => (
          <div key={key} className="rounded bg-white p-2">
            <dt className="text-xs font-medium uppercase tracking-wide text-gray-500">{key.replace(/_/g, ' ')}</dt>
            <dd className="mt-1 break-words text-sm text-gray-800"><ValueView value={nested} /></dd>
          </div>
        ))}
      </dl>
    );
  }
  return <span>{typeof value === 'number' ? formatValue(value) : String(value)}</span>;
};

const ResultDownload = ({ rows, filename, label }) => {
  if (!Array.isArray(rows) || !rows.length) return null;
  const download = () => {
    const columns = [...new Set(rows.flatMap((row) => Object.keys(row || {})))];
    const escape = (value) => `"${String(value ?? '').replace(/"/g, '""')}"`;
    const csv = [
      columns.map(escape).join(','),
      ...rows.map((row) => columns.map((column) => escape(
        row[column] && typeof row[column] === 'object' ? JSON.stringify(row[column]) : row[column]
      )).join(','))
    ].join('\n');
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8;' }));
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = filename;
    anchor.click();
    URL.revokeObjectURL(url);
  };
  return (
    <button type="button" onClick={download} className="rounded bg-primary-600 px-4 py-2 text-white hover:bg-primary-700">
      {label}
    </button>
  );
};

const ToolResultRenderer = ({ tool, result, question }) => {
  if (!result || typeof result !== 'object') {
    return <p className="text-gray-600">{result === undefined || result === null ? 'No result data available.' : String(result)}</p>;
  }
  if (result.error || result.success === false) {
    return <p className="rounded-lg bg-red-50 p-3 text-red-700">{result.error || 'This analysis did not complete successfully.'}</p>;
  }

  const operation = result.operation || tool;
  const predictionRows = result.prediction_dataset;
  const processedRows = result.processed_dataset || result.modified_dataset || result.updated_dataset || result.result_dataset;
  const handled = new Set(['summary_statistics', 'distribution_analysis', 'correlation_analysis']);

  return (
    <div className="space-y-4">
      {operation === 'summary_statistics' && <SummaryStatisticsResult result={result} question={question} />}
      {operation === 'distribution_analysis' && <DistributionResult result={result} />}
      {(operation === 'correlation_analysis' || result.correlations || result.correlation_matrix) && (
        <CorrelationResult result={result} question={question} />
      )}

      {result.transformations?.length > 0 && (
        <ResultCard title="Transformations"><ValueView value={result.transformations} /></ResultCard>
      )}
      {result.new_columns?.length > 0 && (
        <ResultCard title="New columns"><ValueView value={result.new_columns} /></ResultCard>
      )}
      {result.operations_performed?.length > 0 && (
        <ResultCard title="Operations performed"><ValueView value={result.operations_performed} /></ResultCard>
      )}
      {result.results && !handled.has(operation) && (
        <ResultCard title={operation.replace(/_/g, ' ')}><ValueView value={result.results} /></ResultCard>
      )}
      {result.feature_importance && (
        <ResultCard title="Feature importance"><ValueView value={result.feature_importance} /></ResultCard>
      )}
      {['accuracy', 'mse', 'r2_score', 'target_column', 'task_type', 'algorithm', 'dataset_shape', 'columns_analyzed', 'total_outliers'].some((key) => result[key] !== undefined) && (
        <ResultCard title="Analysis details">
          <ValueView value={Object.fromEntries(
            ['accuracy', 'mse', 'r2_score', 'target_column', 'task_type', 'algorithm', 'dataset_shape', 'columns_analyzed', 'total_outliers']
              .filter((key) => result[key] !== undefined)
              .map((key) => [key, result[key]])
          )} />
        </ResultCard>
      )}
      {predictionRows && (
        <ResultCard title="Prediction results">
          <ResultDownload rows={predictionRows} filename="predictions.csv" label="Download Predictions" />
          <ValueView value={predictionRows.slice(0, 10)} />
        </ResultCard>
      )}
      {processedRows && (
        <ResultCard title="Processed dataset">
          <ResultDownload rows={processedRows} filename="processed_dataset.csv" label="Download Processed Dataset" />
          <ValueView value={processedRows.slice(0, 5)} />
        </ResultCard>
      )}
      {result.message && <p className="rounded-lg bg-green-50 p-3 text-green-800">{result.message}</p>}
      {result.success === true && !Object.keys(result).some((key) => key !== 'success' && key !== 'operation') && (
        <p className="text-sm text-gray-600">Analysis completed successfully.</p>
      )}
    </div>
  );
};

export default ToolResultRenderer;
