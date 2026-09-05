try:
    from ..tool_registry import tool_registry, Tool
except ImportError:
    from agent.tool_registry import tool_registry, Tool

from .summary_statistics import summary_statistics
from .correlation import correlation_analysis
from .distribution import distribution_analysis
from .feature_engineering import feature_engineering
from .preprocessing import data_preprocessing
from .outlier_detection import outlier_detection
from .machine_learning import machine_learning
from .visualization import create_visualization

def register_all_tools():
    """Register all analysis tools with the tool registry"""
    if tool_registry.tools:
        return
    
    # Summary Statistics Tool
    summary_tool = Tool(
        name='summary_statistics',
        description='Calculate summary statistics (mean, median, min, max, std) for numerical columns',
        function=summary_statistics,
        input_schema={
            'dataset': 'pd.DataFrame',
            'metadata': 'Dict[str, Any]',
            'columns': 'List[str] (optional)',
            'group_by': 'str (optional)'
        },
        output_schema={
            'success': 'bool',
            'results': 'Dict[str, Any]',
            'operation': 'str'
        }
    )
    tool_registry.register_tool(summary_tool, ['summary_statistics'])
    
    # Correlation Analysis Tool
    correlation_tool = Tool(
        name='correlation_analysis',
        description='Perform correlation analysis between numerical columns using Pearson correlation',
        function=correlation_analysis,
        input_schema={
            'dataset': 'pd.DataFrame',
            'metadata': 'Dict[str, Any]',
            'columns': 'List[str] (optional)'
        },
        output_schema={
            'success': 'bool',
            'correlation_matrix': 'Dict[str, Any]',
            'correlations': 'List[Dict[str, Any]]',
            'method': 'str'
        }
    )
    tool_registry.register_tool(correlation_tool, ['correlation_analysis'])
    
    # Distribution Analysis Tool
    distribution_tool = Tool(
        name='distribution_analysis',
        description='Analyze distribution of numerical columns including histograms, skewness, and percentiles',
        function=distribution_analysis,
        input_schema={
            'dataset': 'pd.DataFrame',
            'metadata': 'Dict[str, Any]',
            'columns': 'List[str] (optional)'
        },
        output_schema={
            'success': 'bool',
            'results': 'Dict[str, Any]',
            'columns_analyzed': 'List[str]'
        }
    )
    tool_registry.register_tool(distribution_tool, ['distribution_analysis'])
    
    # Feature Engineering Tool
    feature_tool = Tool(
        name='feature_engineering',
        description='Perform safe feature engineering operations like creating sum columns, ratios, and age groups',
        function=feature_engineering,
        input_schema={
            'dataset': 'pd.DataFrame',
            'metadata': 'Dict[str, Any]',
            'operation': 'str',
            'parameters': 'Dict[str, Any] (optional)'
        },
        output_schema={
            'success': 'bool',
            'transformations': 'List[str]',
            'new_columns': 'List[str]'
        }
    )
    tool_registry.register_tool(feature_tool, ['feature_engineering'])
    
    # Data Preprocessing Tool
    preprocessing_tool = Tool(
        name='data_preprocessing',
        description='Handle missing values, remove duplicates, and inspect data types',
        function=data_preprocessing,
        input_schema={
            'dataset': 'pd.DataFrame',
            'metadata': 'Dict[str, Any]',
            'operation': 'str',
            'parameters': 'Dict[str, Any] (optional)'
        },
        output_schema={
            'success': 'bool',
            'operations_performed': 'List[str]',
            'dataset_shape': 'Tuple[int, int]'
        }
    )
    tool_registry.register_tool(preprocessing_tool, ['data_preprocessing'])
    
    # Outlier Detection Tool
    outlier_tool = Tool(
        name='outlier_detection',
        description='Detect outliers in numerical columns using IQR or Z-score methods',
        function=outlier_detection,
        input_schema={
            'dataset': 'pd.DataFrame',
            'metadata': 'Dict[str, Any]',
            'columns': 'List[str] (optional)',
            'method': 'str (default: iqr)'
        },
        output_schema={
            'success': 'bool',
            'results': 'Dict[str, Any]',
            'total_outliers': 'int'
        }
    )
    tool_registry.register_tool(outlier_tool, ['outlier_detection'])
    
    # Machine Learning Tool
    ml_tool = Tool(
        name='machine_learning',
        description='Train machine learning models for classification or regression tasks',
        function=machine_learning,
        input_schema={
            'dataset': 'pd.DataFrame',
            'metadata': 'Dict[str, Any]',
            'target_column': 'str (optional)',
            'task_type': 'str (optional)',
            'algorithm': 'str (default: random_forest)'
        },
        output_schema={
            'success': 'bool',
            'task_type': 'str',
            'algorithm': 'str',
            'metrics': 'Dict[str, float]'
        }
    )
    tool_registry.register_tool(ml_tool, ['machine_learning'])
    
    # Visualization Tool
    visualization_tool = Tool(
        name='create_visualization',
        description='Create data visualizations including histograms, bar charts, scatter plots, and heatmaps',
        function=create_visualization,
        input_schema={
            'dataset': 'pd.DataFrame',
            'metadata': 'Dict[str, Any]',
            'chart_type': 'str',
            'parameters': 'Dict[str, Any] (optional)'
        },
        output_schema={
            'success': 'bool',
            'image': 'str (base64)',
            'chart_type': 'str'
        }
    )
    tool_registry.register_tool(visualization_tool, [
        'summary_statistics',
        'correlation_analysis',
        'distribution_analysis',
        'outlier_detection'
    ])  # Visualization can be used with multiple intents