"""
event_stream.py
===============
MVP Event Stream System
Phase 1.4: Basic event logging
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any

class EventStream:
    """Event Stream for tracking user activity"""
    
    def __init__(self, event_file="memory/event_stream.json"):
        self.event_file = event_file
        self.phase = "Phase 1.4"
        os.makedirs(os.path.dirname(event_file), exist_ok=True)
        self.events = self._load_events()
    
    def _load_events(self) -> List[Dict]:
        """Load events from file - ensure it's always a list"""
        if os.path.exists(self.event_file):
            try:
                with open(self.event_file, 'r') as f:
                    data = json.load(f)
                    # Ensure we always return a list
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict) and "events" in data:
                        return data.get("events", [])
                    else:
                        print("⚠ Event file has unexpected format, starting fresh")
                        return []
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        return []  # Always return a list
    
    def add_event(self, event_type: str, data: Dict = None):
        """Add an event to the stream"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "data": data or {},
            "phase": self.phase
        }
        
        # Ensure self.events is a list
        if not isinstance(self.events, list):
            print("⚠ Events was not a list, resetting")
            self.events = []
        
        self.events.append(event)
        
        # Keep only last 1000 events
        if len(self.events) > 1000:
            self.events = self.events[-1000:]
    
    def save_events(self):
        """Save events to file"""
        try:
            # Always save as a list
            with open(self.event_file, 'w') as f:
                json.dump(self.events, f, indent=2)
        except Exception as e:
            print(f"⚠ Failed to save events: {e}")
    
    def analyze_patterns(self, window_size: int = 10) -> List[str]:
        """Analyze patterns in recent events"""
        if not isinstance(self.events, list) or len(self.events) < window_size:
            return []
        
        recent_events = self.events[-window_size:]
        
        patterns = []
        
        # Check for debugging session
        debug_events = [e for e in recent_events if e.get("type") == "error"]
        if len(debug_events) > 3:
            patterns.append("debugging_session")
        
        # Check for coding session
        coding_events = [e for e in recent_events if "vscode" in str(e.get("data", {}))]
        if len(coding_events) > 5:
            patterns.append("coding_session")
        
        # Check for working session
        if len(recent_events) > 8:
            patterns.append("working_session")
        
        return patterns
    
    def get_recent_activity(self, limit: int = 10) -> List[Dict]:
        """Get recent activity"""
        if not isinstance(self.events, list):
            return []
        return self.events[-limit:] if self.events else []