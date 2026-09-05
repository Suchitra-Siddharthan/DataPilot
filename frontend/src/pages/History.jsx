import React, { useState, useEffect } from 'react';
import { Clock, Trash2, Eye, ChevronDown, ChevronUp } from 'lucide-react';
import { getHistory, deleteHistoryItem, clearHistory } from '../services/api';
import { useNavigate } from 'react-router-dom';

const History = () => {
  const navigate = useNavigate();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedItems, setExpandedItems] = useState({});

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      setLoading(true);
      const response = await getHistory(50);
      if (response.success) {
        setHistory(response.history);
      }
    } catch (error) {
      console.error('Failed to load history:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteItem = async (id) => {
    if (!window.confirm('Are you sure you want to delete this analysis?')) {
      return;
    }

    try {
      await deleteHistoryItem(id);
      setHistory(history.filter(item => item.id !== id));
    } catch (error) {
      console.error('Failed to delete item:', error);
    }
  };

  const handleClearAll = async () => {
    if (!window.confirm('Are you sure you want to clear all history?')) {
      return;
    }

    try {
      await clearHistory();
      setHistory([]);
    } catch (error) {
      console.error('Failed to clear history:', error);
    }
  };

  const toggleExpand = (id) => {
    setExpandedItems(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  const viewDetails = (item) => {
    navigate('/results', { state: { analysis: item } });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading history...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-800">Analysis History</h1>
        {history.length > 0 && (
          <button
            onClick={handleClearAll}
            className="flex items-center space-x-2 px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
          >
            <Trash2 className="w-4 h-4" />
            <span>Clear All</span>
          </button>
        )}
      </div>

      {history.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <Clock className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <h2 className="text-xl font-semibold text-gray-800 mb-2">No Analysis History</h2>
          <p className="text-gray-600 mb-4">
            Start analyzing your data to build up your history
          </p>
          <button
            onClick={() => navigate('/analyze')}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            Start Analyzing
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {history.map((item) => (
            <div key={item.id} className="bg-white rounded-lg shadow">
              <div className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="px-2 py-1 bg-primary-100 text-primary-700 text-xs font-medium rounded">
                        {item.intent}
                      </span>
                      <span className="text-sm text-gray-500">
                        {new Date(item.timestamp).toLocaleString()}
                      </span>
                    </div>
                    <h3 className="text-lg font-medium text-gray-800 mb-2">
                      {item.question}
                    </h3>
                    <div className="flex items-center space-x-4 text-sm text-gray-600">
                      <span>Tool: {item.selected_tool}</span>
                      {item.validation?.success ? (
                        <span className="text-green-600">✓ Validated</span>
                      ) : (
                        <span className="text-red-600">✗ Failed</span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2 ml-4">
                    <button
                      onClick={() => viewDetails(item)}
                      className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                      title="View Details"
                    >
                      <Eye className="w-4 h-4 text-gray-600" />
                    </button>
                    <button
                      onClick={() => toggleExpand(item.id)}
                      className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                      title="Toggle Trace"
                    >
                      {expandedItems[item.id] ? (
                        <ChevronUp className="w-4 h-4 text-gray-600" />
                      ) : (
                        <ChevronDown className="w-4 h-4 text-gray-600" />
                      )}
                    </button>
                    <button
                      onClick={() => handleDeleteItem(item.id)}
                      className="p-2 hover:bg-red-100 rounded-lg transition-colors"
                      title="Delete"
                    >
                      <Trash2 className="w-4 h-4 text-red-600" />
                    </button>
                  </div>
                </div>

                {expandedItems[item.id] && item.trace && item.trace.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <h4 className="font-medium text-gray-700 mb-3">Execution Trace</h4>
                    <div className="space-y-2">
                      {item.trace.map((entry, idx) => (
                        <div key={idx} className="flex items-start space-x-2 text-sm">
                          <span className="text-gray-500">{idx + 1}.</span>
                          <span className="text-gray-600">{entry.step}: {entry.message}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default History;