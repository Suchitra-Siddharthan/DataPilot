import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from typing import Dict, Any, List, Optional
import os

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)

def create_visualization(dataset: pd.DataFrame, metadata: Dict[str, Any], 
                       chart_type: str = None, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Create data visualizations.
    Supported types: histogram, bar, line, scatter, boxplot, heatmap, correlation
    """
    try:
        if dataset is None or len(dataset) == 0:
            return {'success': False, 'error': 'Dataset is empty or not loaded'}
        
        if parameters is None:
            parameters = {}
        
        if chart_type is None:
            return {'success': False, 'error': 'No chart type specified'}
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if chart_type == 'histogram':
            result = _create_histogram(dataset, ax, parameters)
        elif chart_type == 'bar':
            result = _create_bar_chart(dataset, ax, parameters)
        elif chart_type == 'line':
            result = _create_line_chart(dataset, ax, parameters)
        elif chart_type == 'scatter':
            result = _create_scatter_plot(dataset, ax, parameters)
        elif chart_type == 'boxplot':
            result = _create_boxplot(dataset, ax, parameters)
        elif chart_type == 'heatmap':
            result = _create_heatmap(dataset, ax, parameters)
        elif chart_type == 'correlation':
            result = _create_correlation_matrix(dataset, ax, parameters)
        else:
            plt.close(fig)
            return {'success': False, 'error': f'Unsupported chart type: {chart_type}'}
        
        if not result['success']:
            plt.close(fig)
            return result
        
        # Convert plot to base64 string
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
        img_buffer.seek(0)
        img_str = base64.b64encode(img_buffer.read()).decode()
        plt.close(fig)
        
        return {
            'success': True,
            'operation': 'visualization',
            'chart_type': chart_type,
            'image': img_str,
            'title': parameters.get('title', f'{chart_type} chart'),
            'parameters': parameters
        }
        
    except Exception as e:
        plt.close('all')
        return {'success': False, 'error': f'Visualization creation failed: {str(e)}'}


def _create_histogram(dataset: pd.DataFrame, ax, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Create histogram"""
    column = parameters.get('column')
    bins = parameters.get('bins', 10)
    
    if column is None:
        # Use first numeric column
        numeric_cols = dataset.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            return {'success': False, 'error': 'No numeric columns for histogram'}
        column = numeric_cols[0]
    
    if column not in dataset.columns:
        return {'success': False, 'error': f'Column {column} not found'}
    
    data = dataset[column].dropna()
    ax.hist(data, bins=bins, edgecolor='black', alpha=0.7)
    ax.set_xlabel(column)
    ax.set_ylabel('Frequency')
    ax.set_title(f'Distribution of {column}')
    
    return {'success': True}


def _create_bar_chart(dataset: pd.DataFrame, ax, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Create bar chart"""
    x_column = parameters.get('x_column')
    y_column = parameters.get('y_column')
    
    if x_column is None or y_column is None:
        return {'success': False, 'error': 'Both x_column and y_column required for bar chart'}
    
    if x_column not in dataset.columns or y_column not in dataset.columns:
        return {'success': False, 'error': 'One or both columns not found'}
    
    # Aggregate data if needed
    if dataset[x_column].nunique() > 20:
        # Show top 20 categories
        top_values = dataset.groupby(x_column)[y_column].mean().nlargest(20)
        top_values.plot(kind='bar', ax=ax)
    else:
        dataset.groupby(x_column)[y_column].mean().plot(kind='bar', ax=ax)
    
    ax.set_xlabel(x_column)
    ax.set_ylabel(f'Mean {y_column}')
    ax.set_title(f'Mean {y_column} by {x_column}')
    plt.xticks(rotation=45)
    
    return {'success': True}


def _create_line_chart(dataset: pd.DataFrame, ax, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Create line chart"""
    x_column = parameters.get('x_column')
    y_column = parameters.get('y_column')
    
    if x_column is None or y_column is None:
        return {'success': False, 'error': 'Both x_column and y_column required for line chart'}
    
    if x_column not in dataset.columns or y_column not in dataset.columns:
        return {'success': False, 'error': 'One or both columns not found'}
    
    # Sort by x column
    sorted_data = dataset.sort_values(x_column)
    ax.plot(sorted_data[x_column], sorted_data[y_column], marker='o')
    ax.set_xlabel(x_column)
    ax.set_ylabel(y_column)
    ax.set_title(f'{y_column} vs {x_column}')
    
    return {'success': True}


def _create_scatter_plot(dataset: pd.DataFrame, ax, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Create scatter plot"""
    x_column = parameters.get('x_column')
    y_column = parameters.get('y_column')
    
    if x_column is None or y_column is None:
        return {'success': False, 'error': 'Both x_column and y_column required for scatter plot'}
    
    if x_column not in dataset.columns or y_column not in dataset.columns:
        return {'success': False, 'error': 'One or both columns not found'}
    
    ax.scatter(dataset[x_column], dataset[y_column], alpha=0.6)
    ax.set_xlabel(x_column)
    ax.set_ylabel(y_column)
    ax.set_title(f'{y_column} vs {x_column}')
    
    return {'success': True}


def _create_boxplot(dataset: pd.DataFrame, ax, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Create boxplot"""
    column = parameters.get('column')
    group_by = parameters.get('group_by')
    
    if column is None:
        numeric_cols = dataset.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            return {'success': False, 'error': 'No numeric columns for boxplot'}
        column = numeric_cols[0]
    
    if column not in dataset.columns:
        return {'success': False, 'error': f'Column {column} not found'}
    
    if group_by and group_by in dataset.columns:
        # Grouped boxplot
        dataset.boxplot(column=column, by=group_by, ax=ax)
        ax.set_title(f'{column} by {group_by}')
    else:
        # Single boxplot
        dataset[column].plot(kind='box', ax=ax)
        ax.set_title(f'Boxplot of {column}')
    
    return {'success': True}


def _create_heatmap(dataset: pd.DataFrame, ax, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Create heatmap"""
    # Create correlation matrix for numeric columns
    numeric_data = dataset.select_dtypes(include=[np.number])
    
    if numeric_data.empty:
        return {'success': False, 'error': 'No numeric columns for heatmap'}
    
    correlation_matrix = numeric_data.corr()
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, ax=ax)
    ax.set_title('Correlation Heatmap')
    
    return {'success': True}


def _create_correlation_matrix(dataset: pd.DataFrame, ax, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Create correlation matrix visualization"""
    numeric_data = dataset.select_dtypes(include=[np.number])
    
    if numeric_data.empty:
        return {'success': False, 'error': 'No numeric columns for correlation matrix'}
    
    correlation_matrix = numeric_data.corr()
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
                linewidths=0.5, fmt='.2f', ax=ax)
    ax.set_title('Correlation Matrix')
    
    return {'success': True}


def create_summary_visualization(dataset: pd.DataFrame, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Create a summary dashboard with multiple visualizations"""
    try:
        if dataset is None or len(dataset) == 0:
            return {'success': False, 'error': 'Dataset is empty or not loaded'}
        
        numeric_cols = dataset.select_dtypes(include=[np.number]).columns.tolist()
        
        if not numeric_cols:
            return {'success': False, 'error': 'No numeric columns for visualization'}
        
        # Create multi-panel figure
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Dataset Summary Dashboard', fontsize=16)
        
        # 1. Histogram of first numeric column
        if len(numeric_cols) > 0:
            dataset[numeric_cols[0]].hist(bins=20, ax=axes[0, 0], edgecolor='black')
            axes[0, 0].set_title(f'Distribution of {numeric_cols[0]}')
            axes[0, 0].set_xlabel(numeric_cols[0])
            axes[0, 0].set_ylabel('Frequency')
        
        # 2. Correlation heatmap
        if len(numeric_cols) > 1:
            corr_matrix = dataset[numeric_cols].corr()
            sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, ax=axes[0, 1])
            axes[0, 1].set_title('Correlation Matrix')
        
        # 3. Boxplot of numeric columns
        if len(numeric_cols) > 0:
            dataset[numeric_cols[:5]].boxplot(ax=axes[1, 0])
            axes[1, 0].set_title('Boxplot of Numeric Columns')
            axes[1, 0].tick_params(axis='x', rotation=45)
        
        # 4. Missing values heatmap
        missing_data = dataset.isnull()
        sns.heatmap(missing_data, cbar=False, cmap='viridis', ax=axes[1, 1])
        axes[1, 1].set_title('Missing Values Pattern')
        
        plt.tight_layout()
        
        # Convert to base64
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
        img_buffer.seek(0)
        img_str = base64.b64encode(img_buffer.read()).decode()
        plt.close(fig)
        
        return {
            'success': True,
            'operation': 'summary_visualization',
            'image': img_str,
            'title': 'Dataset Summary Dashboard'
        }
        
    except Exception as e:
        plt.close('all')
        return {'success': False, 'error': f'Summary visualization failed: {str(e)}'}