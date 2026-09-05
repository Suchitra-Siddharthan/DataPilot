import React from 'react';
import { Brain, BookOpen, Target, Award, Users, Zap } from 'lucide-react';

const About = () => {
  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold text-gray-800">About DataPilot</h1>

      {/* Project Overview */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Brain className="w-6 h-6 text-primary-600" />
          <h2 className="text-2xl font-semibold">Project Overview</h2>
        </div>
        <p className="text-gray-700 leading-relaxed mb-4">
          DataPilot is an intelligent AI agent system for natural-language data analysis. 
          The system combines supervised machine learning intent classification with autonomous 
          tool selection to enable users to analyze datasets using plain English questions.
        </p>
        <p className="text-gray-700 leading-relaxed">
          Unlike traditional data analysis tools that require knowledge of query languages or 
          statistical methods, DataPilot allows users to simply ask questions like 
          "What is the average salary by department?" and receive both numerical results and 
          visualizations along with clear explanations.
        </p>
      </div>

      {/* Research Objective */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Target className="w-6 h-6 text-purple-600" />
          <h2 className="text-2xl font-semibold">Research Objective</h2>
        </div>
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <p className="text-purple-800 font-medium text-lg">
            "To investigate whether a lightweight supervised NLP classifier can identify 
            natural-language data-analysis intents and support autonomous tool selection by an AI agent."
          </p>
        </div>
      </div>

      {/* System Architecture */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Zap className="w-6 h-6 text-yellow-600" />
          <h2 className="text-2xl font-semibold">System Architecture</h2>
        </div>
        <div className="space-y-4">
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center font-bold flex-shrink-0">
              1
            </div>
            <div>
              <h3 className="font-semibold text-gray-800">User Input</h3>
              <p className="text-gray-600">User uploads CSV dataset and asks natural-language question</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center font-bold flex-shrink-0">
              2
            </div>
            <div>
              <h3 className="font-semibold text-gray-800">ML Intent Classification</h3>
              <p className="text-gray-600">TF-IDF + Linear SVM model predicts analytical intent from question</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center font-bold flex-shrink-0">
              3
            </div>
            <div>
              <h3 className="font-semibold text-gray-800">AI Agent Reasoning</h3>
              <p className="text-gray-600">ReAct-style agent observes intent, dataset metadata, and selects appropriate tool</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center font-bold flex-shrink-0">
              4
            </div>
            <div>
              <h3 className="font-semibold text-gray-800">Tool Execution</h3>
              <p className="text-gray-600">Registered analysis tools perform actual data operations using pandas/scikit-learn</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center font-bold flex-shrink-0">
              5
            </div>
            <div>
              <h3 className="font-semibold text-gray-800">Result Validation</h3>
              <p className="text-gray-600">Agent validates results and generates human-readable explanations</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center font-bold flex-shrink-0">
              6
            </div>
            <div>
              <h3 className="font-semibold text-gray-800">Visualization & Response</h3>
              <p className="text-gray-600">Generate appropriate charts and present results with explanations</p>
            </div>
          </div>
        </div>
      </div>

      {/* ML Model Information */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-2 mb-4">
          <BookOpen className="w-6 h-6 text-blue-600" />
          <h2 className="text-2xl font-semibold">Machine Learning Model</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-semibold text-gray-800 mb-2">Model Architecture</h3>
            <ul className="space-y-2 text-gray-600">
              <li>• <strong>Algorithm:</strong> Linear Support Vector Machine (LinearSVC)</li>
              <li>• <strong>Feature Extraction:</strong> TF-IDF (Term Frequency-Inverse Document Frequency)</li>
              <li>• <strong>Training Dataset:</strong> DABench-derived questions</li>
              <li>• <strong>Model Format:</strong> .joblib (saved via joblib)</li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold text-gray-800 mb-2">Supported Intents</h3>
            <ul className="space-y-1 text-gray-600">
              <li>• Summary Statistics</li>
              <li>• Correlation Analysis</li>
              <li>• Distribution Analysis</li>
              <li>• Feature Engineering</li>
              <li>• Data Preprocessing</li>
              <li>• Outlier Detection</li>
              <li>• Machine Learning</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Model Evaluation */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Award className="w-6 h-6 text-green-600" />
          <h2 className="text-2xl font-semibold">Model Evaluation</h2>
        </div>
        
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
          <p className="text-yellow-800 text-sm">
            <strong>Note:</strong> These metrics evaluate the intent-classification component that supports the DataPilot AI-agent workflow. They are development results for this controlled evaluation setup and should not be interpreted as universal performance claims or externally benchmarked results.
          </p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-6 text-center">
            <p className="text-sm text-blue-600 font-medium mb-1">Accuracy</p>
            <p className="text-3xl font-bold text-blue-700">88.46%</p>
          </div>
          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-6 text-center">
            <p className="text-sm text-green-600 font-medium mb-1">Precision</p>
            <p className="text-3xl font-bold text-green-700">89.12%</p>
          </div>
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-6 text-center">
            <p className="text-sm text-purple-600 font-medium mb-1">Recall</p>
            <p className="text-3xl font-bold text-purple-700">88.46%</p>
          </div>
          <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-6 text-center">
            <p className="text-sm text-orange-600 font-medium mb-1">F1 Score</p>
            <p className="text-3xl font-bold text-orange-700">88.40%</p>
          </div>
        </div>

        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="font-semibold text-gray-800 mb-2">Evaluation Details</h3>
          <ul className="space-y-1 text-gray-600 text-sm">
            <li>• <strong>Dataset:</strong> 257 natural-language questions</li>
            <li>• <strong>Intent Classes:</strong> 7</li>
            <li>• <strong>Split:</strong> 80:20 stratified split</li>
            <li>• <strong>Training/Test:</strong> 205/52</li>
            <li>• <strong>Model:</strong> TF-IDF + Linear SVM</li>
            <li>• <strong>Confidence Scores:</strong> Normalized decision-function values (not calibrated probabilities)</li>
          </ul>
        </div>

        <div className="mt-6 p-4 bg-slate-50 border border-slate-200 rounded-lg">
          <h3 className="font-semibold text-gray-800 mb-3">AI-Agent Workflow Evaluation</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm text-gray-700">
            <p>• <strong>Tool Selection Accuracy:</strong> 90.00% (63/70)</p>
            <p>• <strong>Tool Execution Success Rate:</strong> 100.00% (70/70)</p>
            <p>• <strong>Result Validation Rate:</strong> 97.14% (68/70)</p>
            <p>• <strong>End-to-End Task Success Rate:</strong> 97.14% (68/70)</p>
            <p>• <strong>Tool Failure Rate:</strong> 0.00%</p>
            <p>• <strong>Average Agent Response Latency:</strong> 0.0325 s</p>
          </div>
          <p className="mt-4 text-sm text-gray-600">
            These agent-level results were measured on 70 controlled natural-language analytical requests, with 10 requests per intent, to assess the DataPilot workflow for tool routing, validation, execution, and result presentation.
          </p>
        </div>
      </div>

      {/* Research Contribution */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Users className="w-6 h-6 text-red-600" />
          <h2 className="text-2xl font-semibold">Research Contribution</h2>
        </div>
        <p className="text-gray-700 leading-relaxed mb-4">
          This project focuses on a controlled AI-agent workflow that translates natural-language analytical requests into safe, dataset-aware analysis operations. The key contribution is not unrestricted automation, but a structured process that connects intent prediction with validated tool execution and transparent result presentation.
        </p>
        <ul className="space-y-3 text-gray-700">
          <li className="flex items-start space-x-2">
            <span className="text-primary-600 mt-1">•</span>
            <span><strong>AI-Agent Workflow:</strong> controlled workflow that maps natural-language requests to predefined analytical tools and manages tool selection, parameter/column selection, validation, execution, and result presentation.</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-primary-600 mt-1">•</span>
            <span><strong>Controlled Tool Selection:</strong> predefined analysis tools are selected based on the detected analytical intent rather than unrestricted code generation or arbitrary tool execution.</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-primary-600 mt-1">•</span>
            <span><strong>Dataset and Tool Validation:</strong> validates dataset compatibility and tool requirements before analysis execution.</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-primary-600 mt-1">•</span>
            <span><strong>Result Validation:</strong> verifies analytical results before presenting them to the user.</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-primary-600 mt-1">•</span>
            <span><strong>Explainable Workflow:</strong> provides transparent execution information so the analysis process is understandable and traceable.</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-primary-600 mt-1">•</span>
            <span><strong>Intent Classification Support:</strong> TF-IDF + Linear SVM provides the intent prediction used by the AI-agent workflow.</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-primary-600 mt-1">•</span>
            <span><strong>Seven Analytical Capabilities:</strong> Summary Statistics, Correlation Analysis, Distribution Analysis, Feature Engineering, Comprehensive Data Preprocessing, Outlier Detection, and Machine Learning.</span>
          </li>
        </ul>
      </div>

      {/* Technical Details */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Zap className="w-6 h-6 text-gray-600" />
          <h2 className="text-2xl font-semibold">Technical Stack</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-semibold text-gray-800 mb-2">Backend</h3>
            <ul className="space-y-1 text-gray-600">
              <li>• Flask (Python web framework)</li>
              <li>• pandas (data manipulation)</li>
              <li>• scikit-learn (ML algorithms)</li>
              <li>• scipy (statistical functions)</li>
              <li>• matplotlib/seaborn (visualization)</li>
              <li>• joblib (model persistence)</li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold text-gray-800 mb-2">Frontend</h3>
            <ul className="space-y-1 text-gray-600">
              <li>• React (UI framework)</li>
              <li>• React Router (navigation)</li>
              <li>• Axios (HTTP client)</li>
              <li>• Tailwind CSS (styling)</li>
              <li>• Lucide React (icons)</li>
              <li>• Vite (build tool)</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default About;