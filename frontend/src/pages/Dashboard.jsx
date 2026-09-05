import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Upload, BarChart3, Database, ArrowRight, CheckCircle } from 'lucide-react';
import { getDatasetInfo, healthCheck } from '../services/api';

const Dashboard = () => {
  const [datasetInfo, setDatasetInfo] = useState(null);
  const [apiStatus, setApiStatus] = useState('checking');
  const [recentAnalyses, setRecentAnalyses] = useState([]);

  useEffect(() => {
    checkApiStatus();
    loadDatasetInfo();
    loadRecentAnalyses();
  }, []);

  const checkApiStatus = async () => {
    try {
      await healthCheck();
      setApiStatus('healthy');
    } catch (error) {
      setApiStatus('unhealthy');
    }
  };

  const loadDatasetInfo = async () => {
    try {
      const response = await getDatasetInfo();
      if (response.success) {
        setDatasetInfo(response.metadata);
      }
    } catch (error) {
      console.error('Failed to load dataset info:', error);
    }
  };

  const loadRecentAnalyses = async () => {
    try {
      const { getHistory } = await import('../services/api');
      const response = await getHistory(5);
      if (response.success) {
        setRecentAnalyses(response.history);
      }
    } catch (error) {
      console.error('Failed to load recent analyses:', error);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-800 mb-2">DataPilot</h1>
        <p className="text-gray-600 text-lg">
          Intelligent AI Agent for Natural-Language Data Analysis
        </p>
      </div>

      {/* API Status */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {apiStatus === 'healthy' ? (
              <CheckCircle className="w-5 h-5 text-green-500" />
            ) : (
              <div className="w-5 h-5 bg-red-500 rounded-full animate-pulse" />
            )}
            <span className="font-medium">
              {apiStatus === 'healthy' ? 'API Connected' : 'API Disconnected'}
            </span>
          </div>
          <button
            onClick={checkApiStatus}
            className="text-primary-600 hover:text-primary-700 text-sm"
          >
            Refresh Status
          </button>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Link
          to="/dataset"
          className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
        >
          <div className="flex items-start space-x-4">
            <div className="bg-primary-100 p-3 rounded-lg">
              <Upload className="w-6 h-6 text-primary-600" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold mb-2">Upload Dataset</h3>
              <p className="text-gray-600 text-sm mb-4">
                Upload your CSV dataset to begin analysis
              </p>
              <div className="flex items-center text-primary-600">
                <span className="text-sm font-medium">Upload Now</span>
                <ArrowRight className="w-4 h-4 ml-2" />
              </div>
            </div>
          </div>
        </Link>

        <Link
          to="/analyze"
          className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
        >
          <div className="flex items-start space-x-4">
            <div className="bg-primary-100 p-3 rounded-lg">
              <BarChart3 className="w-6 h-6 text-primary-600" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold mb-2">Analyze Data</h3>
              <p className="text-gray-600 text-sm mb-4">
                Ask questions about your data in natural language
              </p>
              <div className="flex items-center text-primary-600">
                <span className="text-sm font-medium">Start Analysis</span>
                <ArrowRight className="w-4 h-4 ml-2" />
              </div>
            </div>
          </div>
        </Link>
      </div>

      {/* Dataset Status */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Database className="w-5 h-5 text-gray-600" />
          <h3 className="text-lg font-semibold">Current Dataset</h3>
        </div>
        
        {datasetInfo ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-600 mb-1">Rows</p>
              <p className="text-2xl font-bold text-gray-800">{datasetInfo.rows}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-600 mb-1">Columns</p>
              <p className="text-2xl font-bold text-gray-800">{datasetInfo.columns}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-600 mb-1">Numeric</p>
              <p className="text-2xl font-bold text-gray-800">{datasetInfo.numeric_columns.length}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-600 mb-1">Categorical</p>
              <p className="text-2xl font-bold text-gray-800">{datasetInfo.categorical_columns.length}</p>
            </div>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <Database className="w-12 h-12 mx-auto mb-2 text-gray-300" />
            <p>No dataset loaded</p>
            <Link to="/dataset" className="text-primary-600 hover:underline">
              Upload a dataset to get started
            </Link>
          </div>
        )}
      </div>

      {/* Recent Analyses */}
      {recentAnalyses.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Recent Analyses</h3>
          <div className="space-y-3">
            {recentAnalyses.map((analysis) => (
              <div
                key={analysis.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div>
                  <p className="font-medium text-gray-800">{analysis.question}</p>
                  <p className="text-sm text-gray-600">
                    {analysis.intent} • {new Date(analysis.timestamp).toLocaleString()}
                  </p>
                </div>
                <Link
                  to="/results"
                  state={{ analysis }}
                  className="text-primary-600 hover:text-primary-700 text-sm"
                >
                  View Details
                </Link>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;