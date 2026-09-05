# DataPilot - Intelligent AI Agent for Natural-Language Data Analysis

DataPilot is an intelligent AI agent system that enables natural-language data analysis using supervised machine learning intent classification and autonomous tool selection.

## 🎯 Project Overview

DataPilot allows users to upload CSV datasets and ask questions in plain English, such as "What is the average salary by department?" The system uses a trained ML model to predict the analytical intent, then an AI agent selects and executes the appropriate analysis tools.

### Research Objective

"To investigate whether a lightweight supervised NLP classifier can identify natural-language data-analysis intents and support autonomous tool selection by an AI agent."

## 🏗️ System Architecture

```
User → Frontend → Backend API → Dataset Manager → ML Intent Classifier → AI Agent → Tool Selection → Analysis Tool → Result Validation → Visualization → Explanation → Frontend
```

### Key Components

1. **ML Intent Classifier**: TF-IDF + Linear SVM model trained on DABench-derived questions
2. **AI Agent**: ReAct-style agent that observes, reasons, selects tools, and validates results
3. **Tool Registry**: Safe, predefined analysis tools (no arbitrary code execution)
4. **Dataset Manager**: Handles CSV upload, inspection, and metadata extraction
5. **Analysis Tools**: Summary statistics, correlation, distribution, preprocessing, outlier detection, ML

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- pip
- npm

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Place your trained ML model in `backend/models/datapilot_intent_svm.joblib` (already included)
4. Note: The model was trained with scikit-learn 1.6.1, but the current environment uses 1.6.0. This may cause version warnings but should still function correctly.

4. Start the Flask server:
```bash
python app.py
```

The backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:3000`

## 📊 Supported Analysis Types

1. **Summary Statistics**: Mean, median, min, max, standard deviation
2. **Correlation Analysis**: Pearson correlation between numerical variables
3. **Distribution Analysis**: Histograms, skewness, percentiles
4. **Feature Engineering**: Create new columns, transformations
5. **Data Preprocessing**: Handle missing values, remove duplicates
6. **Outlier Detection**: IQR and Z-score methods
7. **Machine Learning**: Classification and regression tasks

## 🧪 Running Tests

Navigate to the project root and run:

```bash
python -m pytest tests/
```

Or run individual test files:

```bash
python tests/test_intent_classifier.py
python tests/test_dataset_manager.py
python tests/test_analysis_tools.py
python tests/test_agent.py
```

## 📁 Project Structure

```
AI_PROJECT/
├── backend/
│   ├── app.py                          # Flask application entry point
│   ├── requirements.txt                # Python dependencies
│   ├── api/                            # API routes
│   │   ├── dataset_routes.py
│   │   ├── analysis_routes.py
│   │   └── history_routes.py
│   ├── ml/                             # ML components
│   │   └── intent_classifier.py        # TF-IDF + SVM classifier
│   ├── agent/                          # AI Agent
│   │   ├── agent.py                    # Main agent logic
│   │   ├── state.py                    # Agent state management
│   │   ├── tool_registry.py            # Tool registration
│   │   └── tools/                      # Analysis tools
│   │       ├── summary_statistics.py
│   │       ├── correlation.py
│   │       ├── distribution.py
│   │       ├── feature_engineering.py
│   │       ├── preprocessing.py
│   │       ├── outlier_detection.py
│   │       ├── machine_learning.py
│   │       ├── visualization.py
│   │       └── register_tools.py
│   ├── data/                           # Data management
│   │   └── dataset_manager.py
│   ├── services/                       # Business logic services
│   └── models/                         # ML model storage
│       └── datapilot_intent_svm.joblib # Trained model
├── frontend/
│   ├── package.json                    # Node dependencies
│   ├── vite.config.js                  # Vite configuration
│   ├── index.html                      # HTML entry point
│   ├── tailwind.config.js              # Tailwind CSS config
│   └── src/
│       ├── main.jsx                    # React entry point
│       ├── App.jsx                     # Main React component
│       ├── services/
│       │   └── api.js                  # API client
│       ├── components/
│       │   └── Navbar.jsx              # Navigation component
│       └── pages/
│           ├── Dashboard.jsx            # Home page
│           ├── Dataset.jsx              # Dataset upload/overview
│           ├── Analyze.jsx              # Natural language analysis
│           ├── Results.jsx              # Analysis results display
│           ├── History.jsx              # Analysis history
│           └── About.jsx                # Project/research info
├── tests/                              # Test suite
│   ├── test_intent_classifier.py
│   ├── test_dataset_manager.py
│   ├── test_analysis_tools.py
│   └── test_agent.py
└── README.md                           # This file
```

## 🔒 Security Features

- No arbitrary Python code execution
- File type validation (CSV only)
- File size limits (16MB max)
- Filename sanitization
- Predefined safe analysis tools only
- Input validation on all endpoints

## 📈 ML Model Evaluation

The trained ML model (TF-IDF + Linear SVM) achieved the following evaluation metrics on the DABench-derived test set:

- **Accuracy**: 88.46%
- **Precision**: 89.12%
- **Recall**: 88.46%
- **F1 Score**: 88.40%

*Note: These metrics represent the model's performance during training and should not be interpreted as universal performance claims. Results may vary with different datasets and question distributions.*

**Model Details:**
- Algorithm: Linear Support Vector Machine (LinearSVC)
- Feature Extraction: TF-IDF (ngram_range=(1,2), sublinear_tf=True)
- Training Data: DABench-derived natural language questions
- Intent Classes: 7 (summary_statistics, correlation_analysis, distribution_analysis, feature_engineering, data_preprocessing, outlier_detection, machine_learning)
- Model Format: scikit-learn Pipeline (.joblib file)

## 🎓 Research Contribution

This project demonstrates:

1. **Intent Classification**: TF-IDF + Linear SVM achieves competitive performance on data-analysis intent recognition
2. **Agent Architecture**: ReAct-style agent combining ML predictions with dataset-aware reasoning
3. **Tool Registry**: Safe, predefined analysis tools preventing arbitrary code execution
4. **Explainability**: Transparent execution traces for research validation
5. **Validation**: Multi-layer validation combining ML confidence, dataset compatibility, and result verification

## 🛠️ Technology Stack

### Backend
- Flask (Python web framework)
- pandas (data manipulation)
- scikit-learn (ML algorithms)
- scipy (statistical functions)
- matplotlib/seaborn (visualization)
- joblib (model persistence)

### Frontend
- React (UI framework)
- React Router (navigation)
- Axios (HTTP client)
- Tailwind CSS (styling)
- Lucide React (icons)
- Vite (build tool)

## 📝 Example Usage

1. Upload a CSV dataset via the Dataset page
2. Navigate to the Analyze page
3. Ask a question like "What is the average salary by department?"
4. View the results, visualizations, and agent reasoning trace
5. Access analysis history anytime

## 🔧 Troubleshooting

### Backend Issues

- **Model not loading**: Ensure `datapilot_intent_svm.joblib` is in `backend/models/`
- **Port already in use**: Change port in `backend/app.py` (default: 5000)
- **Dependencies error**: Run `pip install -r requirements.txt` in backend directory

### Frontend Issues

- **API connection error**: Ensure backend is running on port 5000
- **Build errors**: Delete `node_modules` and run `npm install`
- **Port conflicts**: Change port in `frontend/vite.config.js` (default: 3000)

## 📄 License

This project is for academic and research purposes.

## 👥 Contributors

- Developed as a final-year AI project
- Research focus: NLP intent classification for data analysis

## 🙏 Acknowledgments

- DABench dataset for training data
- scikit-learn for ML algorithms
- Flask and React communities