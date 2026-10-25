import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { ArrowLeft, ChevronDown, ChevronUp, BarChart3, Brain, CheckCircle, AlertCircle } from 'lucide-react';
import ToolResultRenderer from '../components/ToolResultRenderer';

const Results = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [showTrace, setShowTrace] = useState(false);
  const analysis = location.state?.analysis;

  if (!analysis) {
    return (
      <div className="py-12 text-center">
        <AlertCircle className="mx-auto mb-4 h-16 w-16 text-gray-400" />
        <h2 className="mb-2 text-xl font-semibold text-gray-800">No Analysis Results</h2>
        <p className="mb-4 text-gray-600">No analysis data available to display</p>
        <button onClick={() => navigate('/analyze')} className="rounded-lg bg-primary-600 px-4 py-2 text-white hover:bg-primary-700">
          Go to Analyze
        </button>
      </div>
    );
  }

  const question = analysis.question || '';
  const confidence = Number(analysis.confidence) || 0;
  const selectedTool = analysis.selected_tool || analysis.tool;
  const selectedTools = Array.isArray(analysis.selected_tools) && analysis.selected_tools.length
    ? analysis.selected_tools
    : selectedTool ? [selectedTool] : [];
  const result = analysis.result;
  const multiToolResults = Array.isArray(analysis.tool_results) && analysis.tool_results.length
    ? analysis.tool_results
    : Array.isArray(result?.tool_results) ? result.tool_results : [];
  const isMultiTool = result?.operation === 'multi_tool_analysis' || multiToolResults.length > 1;
  const explanation = analysis.explanation || analysis.answer;
  const validation = analysis.validation;
  const trace = Array.isArray(analysis.trace) ? analysis.trace : [];
  const rawPayload = multiToolResults.length ? multiToolResults : result;

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <button onClick={() => navigate('/analyze')} className="rounded-lg p-2 transition-colors hover:bg-gray-100" aria-label="Back to analyze">
          <ArrowLeft className="h-5 w-5 text-gray-600" />
        </button>
        <h1 className="text-3xl font-bold text-gray-800">Analysis Results</h1>
      </div>

      <section className="rounded-lg bg-white p-6 shadow">
        <div className="mb-4 flex items-center space-x-2">
          <Brain className="h-5 w-5 text-primary-600" />
          <h3 className="text-lg font-semibold">Your Question</h3>
        </div>
        <p className="text-xl text-gray-800">{question || 'Question unavailable'}</p>
      </section>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <section className="rounded-lg bg-white p-6 shadow">
          <div className="mb-2 flex items-center space-x-2">
            <Brain className="h-5 w-5 text-purple-600" />
            <h4 className="font-medium text-gray-700">Detected Intent</h4>
          </div>
          <p className="text-lg font-semibold text-purple-700">{analysis.intent || 'Unavailable'}</p>
          <p className="text-sm text-gray-500">Confidence: {(confidence * 100).toFixed(1)}%</p>
        </section>

        <section className="rounded-lg bg-white p-6 shadow">
          <div className="mb-2 flex items-center space-x-2">
            <BarChart3 className="h-5 w-5 text-blue-600" />
            <h4 className="font-medium text-gray-700">{selectedTools.length > 1 ? 'Selected Tools' : 'Selected Tool'}</h4>
          </div>
          {selectedTools.length ? (
            <div className="flex flex-wrap gap-2">
              {selectedTools.map((tool) => (
                <span key={tool} className="rounded bg-blue-50 px-2 py-1 text-sm font-semibold text-blue-700">{tool}</span>
              ))}
            </div>
          ) : <p className="text-sm text-gray-500">No tool information available.</p>}
        </section>

        <section className="rounded-lg bg-white p-6 shadow">
          <div className="mb-2 flex items-center space-x-2">
            {validation?.success
              ? <CheckCircle className="h-5 w-5 text-green-600" />
              : <AlertCircle className="h-5 w-5 text-red-600" />}
            <h4 className="font-medium text-gray-700">Validation</h4>
          </div>
          <p className={`text-lg font-semibold ${validation?.success ? 'text-green-700' : 'text-red-700'}`}>
            {validation?.success ? 'Successful' : validation ? 'Failed' : 'Unavailable'}
          </p>
          {validation?.message && <p className="text-sm text-gray-500">{validation.message}</p>}
        </section>
      </div>

      <section className="rounded-lg bg-white p-6 shadow">
        <div className="mb-4 flex items-center space-x-2">
          <BarChart3 className="h-5 w-5 text-gray-600" />
          <h3 className="text-lg font-semibold">Analysis Result</h3>
        </div>

        {isMultiTool ? (
          <div className="space-y-4">
            {multiToolResults.length ? multiToolResults.map((item, index) => (
              <section key={`${item.tool || 'tool'}-${index}`} className="rounded-lg border border-gray-200 p-4">
                <h4 className="mb-3 text-base font-semibold capitalize text-gray-800">
                  {(item.tool || 'Analysis tool').replace(/_/g, ' ')}
                </h4>
                <ToolResultRenderer tool={item.tool} result={item.result} question={question} />
              </section>
            )) : (
              <p className="text-gray-600">Tool results are not available for this multi-tool analysis.</p>
            )}

            <section className="rounded-lg border border-primary-200 bg-primary-50 p-4">
              <h4 className="mb-2 font-semibold text-gray-800">Combined Summary</h4>
              <p className="whitespace-pre-line text-gray-700">
                {explanation || 'The individual results above answer the requested analysis tasks.'}
              </p>
            </section>
          </div>
        ) : result ? (
          <section className="rounded-lg border border-gray-200 p-4">
            {selectedTools[0] && (
              <h4 className="mb-3 text-base font-semibold capitalize text-gray-800">
                {selectedTools[0].replace(/_/g, ' ')}
              </h4>
            )}
            <ToolResultRenderer tool={selectedTools[0]} result={result} question={question} />
          </section>
        ) : (
          <p className="text-gray-600">No result data is available for this analysis.</p>
        )}

        <details className="mt-4 rounded-lg bg-gray-100">
          <summary className="flex cursor-pointer list-none items-center justify-between p-3 font-medium text-gray-700">
            <span>View Raw Result (JSON)</span>
            <ChevronDown className="h-5 w-5" />
          </summary>
          <pre className="max-h-96 overflow-auto whitespace-pre-wrap break-words p-3 pt-0 text-sm text-gray-700">
            {JSON.stringify(rawPayload ?? { message: 'No raw result data available' }, null, 2)}
          </pre>
        </details>
      </section>

      {!isMultiTool && <section className="rounded-lg bg-white p-6 shadow">
        <div className="mb-4 flex items-center space-x-2">
          <Brain className="h-5 w-5 text-gray-600" />
          <h3 className="text-lg font-semibold">Explanation</h3>
        </div>
        <p className="whitespace-pre-line text-gray-700">{explanation || 'No explanation provided.'}</p>
      </section>}

      <section className="rounded-lg bg-white p-6 shadow">
        <button onClick={() => setShowTrace(!showTrace)} className="flex w-full items-center justify-between">
          <div className="flex items-center space-x-2">
            <Brain className="h-5 w-5 text-gray-600" />
            <h3 className="text-lg font-semibold">Agent Reasoning / Execution Trace</h3>
          </div>
          {showTrace ? <ChevronUp className="h-5 w-5 text-gray-600" /> : <ChevronDown className="h-5 w-5 text-gray-600" />}
        </button>
        {showTrace && (
          trace.length ? (
            <div className="mt-4 space-y-3">
              {trace.map((entry, index) => (
                <div key={`${entry.timestamp || 'trace'}-${index}`} className="flex items-start space-x-3 rounded-lg bg-gray-50 p-3">
                  <div className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-primary-100 text-sm font-medium text-primary-700">
                    {index + 1}
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-gray-800">{entry.step || entry.action || 'Step'}</p>
                    <p className="text-sm text-gray-600">{entry.message || entry.detail || 'No trace details available.'}</p>
                  </div>
                </div>
              ))}
            </div>
          ) : <p className="mt-4 text-sm text-gray-500">No execution trace is available.</p>
        )}
      </section>

      <div className="flex space-x-4">
        <button onClick={() => navigate('/analyze')} className="rounded-lg bg-primary-600 px-6 py-3 text-white hover:bg-primary-700">
          Ask Another Question
        </button>
        <button onClick={() => navigate('/history')} className="rounded-lg bg-gray-200 px-6 py-3 text-gray-800 hover:bg-gray-300">
          View History
        </button>
      </div>
    </div>
  );
};

export default Results;
