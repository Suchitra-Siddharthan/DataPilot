import React, { useState, useEffect } from 'react';
import { Upload, X, Database, Table, Trash2 } from 'lucide-react';
import { uploadDataset, getDatasetInfo, getDatasetPreview, clearDataset } from '../services/api';

const Dataset = () => {
  const [datasetInfo, setDatasetInfo] = useState(null);
  const [preview, setPreview] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDatasetData();
  }, []);

  const loadDatasetData = async () => {
    try {
      const [infoResponse, previewResponse] = await Promise.all([
        getDatasetInfo(),
        getDatasetPreview(10)
      ]);

      if (infoResponse.success) {
        setDatasetInfo(infoResponse.metadata);
      }

      if (previewResponse.success) {
        setPreview(previewResponse.preview);
      }

      setError(null);
    } catch (err) {
      if (err.response && err.response.status === 404) {
        setDatasetInfo(null);
        setPreview(null);
        setError(null);
        return;
      }
      setError('Failed to load dataset information');
      console.error(err);
    }
  };

  const handleFileSelection = async (file) => {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith('.csv')) {
      setError('Only CSV files are allowed');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const response = await uploadDataset(file);

      if (response.success) {
        await loadDatasetData();
      } else {
        setError(response.error || 'Upload failed');
      }
    } catch (err) {
      setError('Failed to upload dataset');
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files?.[0];
    if (event.target) {
      event.target.value = '';
    }
    await handleFileSelection(file);
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'copy';
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
  };

  const handleDrop = async (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files?.[0];
    await handleFileSelection(file);
  };

  const handleClearDataset = async () => {
    if (!window.confirm('Are you sure you want to clear the current dataset?')) {
      return;
    }

    try {
      await clearDataset();
      setDatasetInfo(null);
      setPreview(null);
      setError(null);
    } catch (err) {
      setError('Failed to clear dataset');
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-800">Dataset</h1>
        {datasetInfo && (
          <button
            onClick={handleClearDataset}
            className="flex items-center space-x-2 px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
          >
            <Trash2 className="w-4 h-4" />
            <span>Clear Dataset</span>
          </button>
        )}
      </div>

      {/* Upload Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Upload className="w-5 h-5 text-gray-600" />
          <h3 className="text-lg font-semibold">Upload Dataset</h3>
        </div>

        <div
          className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary-400 transition-colors"
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <input
            type="file"
            accept=".csv"
            onChange={handleFileUpload}
            disabled={uploading}
            className="hidden"
            id="file-upload"
          />
          <label
            htmlFor="file-upload"
            className="cursor-pointer"
          >
            <Database className="w-12 h-12 mx-auto mb-4 text-gray-400" />
            <p className="text-gray-600 mb-2">
              {uploading ? 'Uploading...' : 'Click to upload or drag and drop'}
            </p>
            <p className="text-sm text-gray-500">CSV files only (max 16MB)</p>
          </label>
        </div>

        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}
      </div>

      {/* Dataset Information */}
      {datasetInfo && (
        <>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-2 mb-4">
              <Database className="w-5 h-5 text-gray-600" />
              <h3 className="text-lg font-semibold">Dataset Information</h3>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
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

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Numeric Columns</h4>
                <div className="flex flex-wrap gap-2">
                  {datasetInfo.numeric_columns.map((col) => (
                    <span
                      key={col}
                      className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
                    >
                      {col}
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Categorical Columns</h4>
                <div className="flex flex-wrap gap-2">
                  {datasetInfo.categorical_columns.map((col) => (
                    <span
                      key={col}
                      className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm"
                    >
                      {col}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {Object.keys(datasetInfo.missing_values).some(key => datasetInfo.missing_values[key] > 0) && (
              <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <h4 className="font-medium text-yellow-800 mb-2">Missing Values</h4>
                <div className="space-y-1">
                  {Object.entries(datasetInfo.missing_values)
                    .filter(([_, count]) => count > 0)
                    .map(([col, count]) => (
                      <div key={col} className="flex justify-between text-sm">
                        <span className="text-yellow-700">{col}</span>
                        <span className="text-yellow-800 font-medium">{count}</span>
                      </div>
                    ))}
                </div>
              </div>
            )}

            {datasetInfo.duplicate_rows > 0 && (
              <div className="mt-4 p-4 bg-orange-50 border border-orange-200 rounded-lg">
                <p className="text-orange-800">
                  <span className="font-medium">{datasetInfo.duplicate_rows}</span> duplicate rows detected
                </p>
              </div>
            )}
          </div>

          {/* Data Preview */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-2 mb-4">
              <Table className="w-5 h-5 text-gray-600" />
              <h3 className="text-lg font-semibold">Data Preview</h3>
            </div>

            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    {datasetInfo.column_names.map((col) => (
                      <th
                        key={col}
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {preview && preview.map((row, idx) => (
                    <tr key={idx}>
                      {datasetInfo.column_names.map((col) => (
                        <td
                          key={col}
                          className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                        >
                          {row[col] !== null && row[col] !== undefined
                            ? String(row[col])
                            : '-'}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Dataset;