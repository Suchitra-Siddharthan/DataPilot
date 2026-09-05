from typing import Dict, Any, Optional, List
from datetime import datetime

class AgentState:
    """Manages the state of the AI agent during analysis"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset agent state to initial values"""
        self.current_step = "idle"
        self.observation = None
        self.intent = None
        self.dataset_metadata = None
        self.candidate_tools = []
        self.selected_tool = None
        self.tool_parameters = {}
        self.action_result = None
        self.validation_result = None
        self.final_response = None
        self.error = None
        self.execution_trace = []
        self.start_time = None
        self.end_time = None
    
    def update_observation(self, observation: Dict[str, Any]):
        """Update agent observation"""
        self.observation = observation
        self._add_trace("OBSERVE", f"Observed: {observation}")
    
    def set_intent(self, intent: str, confidence: float):
        """Set predicted intent from ML classifier"""
        self.intent = intent
        self._add_trace("INTENT", f"Intent predicted: {intent} (confidence: {confidence:.2f})")
    
    def set_dataset_metadata(self, metadata: Dict[str, Any]):
        """Set dataset metadata"""
        self.dataset_metadata = metadata
        self._add_trace("DATASET", f"Dataset loaded: {metadata.get('rows', 0)} rows, {metadata.get('columns', 0)} columns")
    
    def set_candidate_tools(self, tools: List[str]):
        """Set candidate tools for current intent"""
        self.candidate_tools = tools
        self._add_trace("CANDIDATE_TOOLS", f"Candidate tools: {', '.join(tools)}")
    
    def select_tool(self, tool_name: str, parameters: Dict[str, Any]):
        """Select tool and its parameters"""
        self.selected_tool = tool_name
        self.tool_parameters = {k: v for k, v in parameters.items() if k != 'dataset'}
        param_names = [k for k in parameters.keys() if k != 'dataset']
        self._add_trace("SELECT_TOOL", f"Selected tool: {tool_name} with parameters: {param_names}")
    
    def set_action_result(self, result: Dict[str, Any]):
        """Set result from tool execution"""
        self.action_result = result
        self._add_trace("ACTION_RESULT", f"Tool executed: {result.get('status', 'unknown')}")
    
    def set_validation_result(self, result: Dict[str, Any]):
        """Set validation result"""
        self.validation_result = result
        self._add_trace("VALIDATION", f"Validation: {result.get('success', False)} - {result.get('message', '')}")
    
    def set_final_response(self, response: Dict[str, Any]):
        """Set final response"""
        self.final_response = response
        self._add_trace("COMPLETE", "Analysis completed successfully")
    
    def set_error(self, error: str):
        """Set error state"""
        self.error = error
        self._add_trace("ERROR", f"Error: {error}")
    
    def _add_trace(self, step: str, message: str):
        """Add entry to execution trace"""
        self.execution_trace.append({
            'step': step,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_trace(self) -> List[Dict[str, str]]:
        """Get execution trace"""
        return self.execution_trace.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary"""
        return {
            'current_step': self.current_step,
            'intent': self.intent,
            'selected_tool': self.selected_tool,
            'tool_parameters': self.tool_parameters,
            'error': self.error,
            'execution_trace': self.execution_trace,
            'start_time': self.start_time,
            'end_time': self.end_time
        }


# Global instance
agent_state = AgentState()