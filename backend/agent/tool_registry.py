from typing import Dict, Any, List, Callable
import inspect
import sys
import os

# Ensure agent directory is in path
agent_dir = os.path.dirname(os.path.abspath(__file__))
if agent_dir not in sys.path:
    sys.path.insert(0, agent_dir)

class Tool:
    """Represents an analysis tool"""
    
    def __init__(self, name: str, description: str, function: Callable, 
                 input_schema: Dict[str, Any], output_schema: Dict[str, Any]):
        self.name = name
        self.description = description
        self.function = function
        self.input_schema = input_schema
        self.output_schema = output_schema
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool function"""
        try:
            result = self.function(**kwargs)
            if isinstance(result, dict) and result.get('error') and not result.get('success'):
                return {
                    'success': False,
                    'error': result['error'],
                    'result': result,
                    'tool': self.name
                }
            return {
                'success': True,
                'result': result,
                'tool': self.name
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'tool': self.name
            }


class ToolRegistry:
    """Registry for managing analysis tools"""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.intent_to_tools: Dict[str, List[str]] = {}
    
    def register_tool(self, tool: Tool, intents: List[str]):
        """Register a tool for specific intents"""
        self.tools[tool.name] = tool
        
        for intent in intents:
            if intent not in self.intent_to_tools:
                self.intent_to_tools[intent] = []
            self.intent_to_tools[intent].append(tool.name)
    
    def get_tool(self, tool_name: str) -> Tool:
        """Get a specific tool"""
        return self.tools.get(tool_name)
    
    def get_tools_for_intent(self, intent: str) -> List[str]:
        """Get tool names for a specific intent"""
        return self.intent_to_tools.get(intent, [])
    
    def get_all_tools(self) -> Dict[str, Tool]:
        """Get all registered tools"""
        return self.tools.copy()
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all tools with their metadata"""
        return [
            {
                'name': tool.name,
                'description': tool.description,
                'input_schema': tool.input_schema,
                'output_schema': tool.output_schema
            }
            for tool in self.tools.values()
        ]


# Global instance
tool_registry = ToolRegistry()