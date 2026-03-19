"""
Module Orchestrator for Music AI System

Coordinates collaboration between:
- ChatGPT Module (creative direction)
- Live Studio (production)
- AI Model (generation)
"""

from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import json
from enum import Enum


class ModuleState(Enum):
    """Possible module states."""
    IDLE = "idle"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class ModuleOrchestrator:
    """Orchestrates modules for collaborative music AI production."""
    
    def __init__(self):
        """Initialize orchestrator."""
        self.modules: Dict[str, Any] = {}
        self.module_states: Dict[str, ModuleState] = {}
        self.event_log: List[Dict[str, Any]] = []
        self.callbacks: Dict[str, List[Callable]] = {}
        self.session_data: Dict[str, Any] = {
            "created_at": datetime.now().isoformat(),
            "projects": []
        }
    
    def register_module(self, module_name: str, module_instance: Any) -> None:
        """
        Register a module with the orchestrator.
        
        Args:
            module_name: Unique identifier for module
            module_instance: Module instance to register
        """
        self.modules[module_name] = module_instance
        self.module_states[module_name] = ModuleState.READY
        self._log_event("module_registered", {"module": module_name})
    
    def unregister_module(self, module_name: str) -> None:
        """Unregister a module."""
        if module_name in self.modules:
            del self.modules[module_name]
            del self.module_states[module_name]
            self._log_event("module_unregistered", {"module": module_name})
    
    def get_module(self, module_name: str) -> Any:
        """Get a registered module."""
        return self.modules.get(module_name)
    
    def set_module_state(self, module_name: str, state: ModuleState) -> None:
        """Update module state."""
        if module_name in self.module_states:
            self.module_states[module_name] = state
            self._log_event("state_change", {
                "module": module_name,
                "state": state.value
            })
    
    def on_event(self, event_name: str, callback: Callable) -> None:
        """
        Register a callback for an event.
        
        Args:
            event_name: Name of event
            callback: Function to call when event occurs
        """
        if event_name not in self.callbacks:
            self.callbacks[event_name] = []
        self.callbacks[event_name].append(callback)
    
    def emit_event(self, event_name: str, data: Dict[str, Any]) -> None:
        """
        Emit an event and trigger callbacks.
        
        Args:
            event_name: Name of event
            data: Event data
        """
        self._log_event(event_name, data)
        
        if event_name in self.callbacks:
            for callback in self.callbacks[event_name]:
                try:
                    callback(data)
                except Exception as e:
                    self._log_event("callback_error", {
                        "event": event_name,
                        "error": str(e)
                    })
    
    def process_music_request(self, request: str) -> Dict[str, Any]:
        """
        Process a complete music production request.
        
        Flow: ChatGPT interprets -> Studio prepares -> Generation -> Mixing
        
        Args:
            request: User's music request
            
        Returns:
            Result with generated music and metadata
        """
        self._log_event("music_request_started", {"request": request})
        
        result = {
            "request": request,
            "stages": {}
        }
        
        # Stage 1: ChatGPT interpretation
        self.set_module_state("chatgpt", ModuleState.PROCESSING)
        chatgpt = self.get_module("chatgpt")
        
        if chatgpt:
            interpretation = chatgpt.interpret_music_prompt(request)
            result["stages"]["interpretation"] = interpretation
            self.emit_event("interpretation_complete", interpretation)
        
        # Stage 2: Studio setup
        self.set_module_state("studio", ModuleState.PROCESSING)
        studio = self.get_module("studio")
        
        if studio and "interpretation" in result["stages"]:
            interp = result["stages"]["interpretation"]
            if "tempo" in interp:
                studio.set_tempo(interp["tempo"])
            result["stages"]["studio_setup"] = {
                "tempo": studio.tempo,
                "tracks": list(studio.tracks.keys())
            }
            self.emit_event("studio_ready", result["stages"]["studio_setup"])
        
        # Stage 3: Model inference (if available)
        model = self.get_module("model")
        if model:
            self.set_module_state("model", ModuleState.PROCESSING)
            # Would perform actual generation here
            result["stages"]["generation"] = {"status": "model_available"}
        
        self.set_module_state("chatgpt", ModuleState.READY)
        self.set_module_state("studio", ModuleState.READY)
        
        self._log_event("music_request_completed", result)
        
        return result
    
    def collaborate_modules(self, task: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute collaborative task across modules.
        
        Args:
            task: Type of task (e.g., "generate_music", "refine_composition")
            params: Task parameters
            
        Returns:
            Collaboration result
        """
        self._log_event("collaboration_started", {"task": task, "params": params})
        
        collaboration_result = {
            "task": task,
            "modules_involved": list(self.modules.keys()),
            "results": {}
        }
        
        chatgpt = self.get_module("chatgpt")
        studio = self.get_module("studio")
        model = self.get_module("model")
        
        # Each module contributes to the task
        if chatgpt and task == "compose":
            collaboration_result["results"]["chatgpt"] = {
                "suggestion": "Try a minor key progression for emotional depth"
            }
        
        if studio and task == "compose":
            collaboration_result["results"]["studio"] = {
                "state": studio.get_studio_state()
            }
        
        self._log_event("collaboration_complete", collaboration_result)
        
        return collaboration_result
    
    def save_session(self, filepath: str) -> None:
        """Save orchestrator session to file."""
        session = {
            "session_data": self.session_data,
            "module_states": {k: v.value for k, v in self.module_states.items()},
            "recent_events": self.event_log[-50:]  # Last 50 events
        }
        
        with open(filepath, 'w') as f:
            json.dump(session, f, indent=2)
        
        self._log_event("session_saved", {"filepath": filepath})
    
    def load_session(self, filepath: str) -> None:
        """Load orchestrator session from file."""
        with open(filepath, 'r') as f:
            session = json.load(f)
        
        self.session_data = session.get("session_data", self.session_data)
        self._log_event("session_loaded", {"filepath": filepath})
    
    def get_module_status(self) -> Dict[str, str]:
        """Get status of all registered modules."""
        return {
            module: state.value
            for module, state in self.module_states.items()
        }
    
    def get_event_log(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get event log.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of events
        """
        if limit:
            return self.event_log[-limit:]
        return self.event_log.copy()
    
    def _log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log an event internally."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "data": data
        }
        self.event_log.append(event)
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        return {
            "modules": list(self.modules.keys()),
            "module_count": len(self.modules),
            "module_states": self.get_module_status(),
            "event_count": len(self.event_log),
            "session_created": self.session_data.get("created_at")
        }
