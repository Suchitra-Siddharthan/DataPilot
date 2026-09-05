import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Send, Loader2, AlertCircle } from 'lucide-react';
import { analyzeQuestion, saveToHistory, getDatasetInfo } from '../services/api';

const Analyze = () => {
  const navigate = useNavigate();
  const [question, setQuestion] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  const [pipelineStatus, setPipelineStatus] = useState([]);
  const [datasetInfo, setDatasetInfo] = useState(null);

  // Load dataset metadata on mount for client-side validations
  React.useEffect(() => {
    (async () => {
      try {
        const info = await getDatasetInfo();
        if (info && info.success) setDatasetInfo(info.metadata);
      } catch (e) {
        // ignore, metadata is optional for client-side checks
      }
    })();
  }, []);

  const handleAnalyze = async () => {
    if (!question.trim()) {
      setError('Please enter a question');
      return;
    }

    setError(null);

    // Client-side pre-validation: if the user asked about correlations, ensure at least
    // two valid numeric (non-identifier) columns are available before sending request.
    try {
      const q = question.toLowerCase();
      const correlation_keywords = ['correlation', 'correlate', 'relationship', 'related', 'associated', 'connection'];
      const correlation_between = ['between', 'vs', 'versus', 'and'];
      const isCorrelation = (correlation_keywords.some(k => q.includes(k)) && correlation_between.some(k => q.includes(k)));

      if (isCorrelation) {
        // ensure we have metadata (try to fetch if not yet loaded)
        let info = datasetInfo;
        if (!info) {
          try {
            const res = await getDatasetInfo();
            if (res && res.success) {
              info = res.metadata;
              setDatasetInfo(info);
            }
          } catch (e) {
            // ignore fetch error and allow backend to validate
            info = null;
          }
        }

        if (info) {
          const id_keywords = ['id', 'employee_id', 'customer_id', 'order_id', 'user_id', 'uid'];
          const numericCols = info.numeric_columns || [];
          const validNumeric = numericCols.filter(col => {
            const colLower = String(col).toLowerCase();
            // Only exclude actual identifier-like columns by name.
            // Do not drop other numeric analytical columns just because they are mostly unique.
            return !id_keywords.some(k => colLower === k || colLower.endsWith(`_${k}`) || colLower.includes(k));
          });

          if (validNumeric.length < 2) {
            setError(`Correlation analysis requires at least 2 numerical columns, found ${validNumeric.length}`);
            return;
          }
        }
      }
    } catch (e) {
      // if pre-validation fails unexpectedly, fall back to server-side validation
    }

    setAnalyzing(true);
    setPipelineStatus([
      { step: 'Understanding question', status: 'in_progress' },
      { step: 'Detecting intent', status: 'pending' },
      { step: 'Agent selecting tool', status: 'pending' },
      { step: 'Executing analysis', status: 'pending' },
      { step: 'Validating result', status: 'pending' },
      { step: 'Generating response', status: 'pending' },
    ]);

    try {
      // Simulate pipeline progress
      await new Promise(resolve => setTimeout(resolve, 500));
      updatePipelineStatus(0, 'completed');
      updatePipelineStatus(1, 'in_progress');

      await new Promise(resolve => setTimeout(resolve, 500));
      updatePipelineStatus(1, 'completed');
      updatePipelineStatus(2, 'in_progress');

      const response = await analyzeQuestion(question);

      if (response.success || response.status === 'success') {
        updatePipelineStatus(2, 'completed');
        updatePipelineStatus(3, 'in_progress');

        await new Promise(resolve => setTimeout(resolve, 500));
        updatePipelineStatus(3, 'completed');
        updatePipelineStatus(4, 'in_progress');

        await new Promise(resolve => setTimeout(resolve, 300));
        updatePipelineStatus(4, 'completed');
        updatePipelineStatus(5, 'in_progress');

        await new Promise(resolve => setTimeout(resolve, 300));
        updatePipelineStatus(5, 'completed');

        const analysis = {
          ...response,
          selected_tool: response.selected_tool || response.tool,
          explanation: response.explanation || response.answer,
        };

        try {
          await saveToHistory({
            question: analysis.question,
            intent: analysis.intent,
            selected_tool: analysis.selected_tool,
            result: analysis.result,
            explanation: analysis.explanation,
            validation: analysis.validation,
            trace: analysis.trace || [],
          });
        } catch (historyError) {
          console.error(historyError);
        }

        navigate('/results', { state: { analysis } });
      } else {
        setError(response.error || 'Analysis failed');
        setPipelineStatus([]);
      }
    } catch (err) {
      const apiError = err.response && err.response.data && err.response.data.error;
      setError(apiError || 'Failed to analyze question. Please try again.');
      console.error(err);
      setPipelineStatus([]);
    } finally {
      setAnalyzing(false);
    }
  };

  const updatePipelineStatus = (index, status) => {
    setPipelineStatus(prev => {
      const updated = [...prev];
      updated[index] = { ...updated[index], status };
      return updated;
    });
  };

  const exampleQuestions = [
    "What is the average salary?",
    "Is salary related to experience?",
    "Show the distribution of ages",
    "Find unusual salary values",
    "Handle missing values",
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold text-gray-800">Analyze Data</h1>

      {/* Question Input */}
      <div className="bg-white rounded-lg shadow p-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Ask a question about your data
        </label>
        <div className="flex space-x-4">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAnalyze()}
            placeholder="e.g., What is the average salary by department?"
            disabled={analyzing}
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
          <button
            onClick={handleAnalyze}
            disabled={analyzing || !question.trim()}
            className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {analyzing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                <span>Analyze</span>
              </>
            )}
          </button>
        </div>

        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 flex items-center space-x-2">
            <AlertCircle className="w-4 h-4" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* Example Questions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Example Questions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {exampleQuestions.map((q, idx) => (
            <button
              key={idx}
              onClick={() => setQuestion(q)}
              disabled={analyzing}
              className="text-left px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-lg text-gray-700 transition-colors disabled:opacity-50"
            >
              "{q}"
            </button>
          ))}
        </div>
      </div>

      {/* Pipeline Status */}
      {pipelineStatus.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Analysis Pipeline</h3>
          <div className="space-y-3">
            {pipelineStatus.map((item, idx) => (
              <div key={idx} className="flex items-center space-x-3">
                <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                  item.status === 'completed' ? 'bg-green-500' :
                  item.status === 'in_progress' ? 'bg-primary-500 animate-pulse' :
                  'bg-gray-300'
                }`}>
                  {item.status === 'completed' && (
                    <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                  {item.status === 'in_progress' && (
                    <Loader2 className="w-4 h-4 text-white animate-spin" />
                  )}
                </div>
                <span className={`${
                  item.status === 'completed' ? 'text-green-700' :
                  item.status === 'in_progress' ? 'text-primary-700' :
                  'text-gray-500'
                }`}>
                  {item.step}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Analysis Capabilities */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Analysis Capabilities</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="p-4 bg-blue-50 rounded-lg">
            <h4 className="font-medium text-blue-800 mb-2">Summary Statistics</h4>
            <p className="text-sm text-blue-700">Mean, median, min, max, standard deviation</p>
          </div>
          <div className="p-4 bg-green-50 rounded-lg">
            <h4 className="font-medium text-green-800 mb-2">Correlation Analysis</h4>
            <p className="text-sm text-green-700">Relationships between numerical variables</p>
          </div>
          <div className="p-4 bg-purple-50 rounded-lg">
            <h4 className="font-medium text-purple-800 mb-2">Distribution Analysis</h4>
            <p className="text-sm text-purple-700">Histograms, skewness, percentiles</p>
          </div>
          <div className="p-4 bg-orange-50 rounded-lg">
            <h4 className="font-medium text-orange-800 mb-2">Feature Engineering</h4>
            <p className="text-sm text-orange-700">Create new columns and transformations</p>
          </div>
          <div className="p-4 bg-red-50 rounded-lg">
            <h4 className="font-medium text-red-800 mb-2">Data Preprocessing</h4>
            <p className="text-sm text-red-700">Handle missing values and clean data</p>
          </div>
          <div className="p-4 bg-teal-50 rounded-lg">
            <h4 className="font-medium text-teal-800 mb-2">Outlier Detection</h4>
            <p className="text-sm text-teal-700">Identify unusual values using IQR method</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analyze;