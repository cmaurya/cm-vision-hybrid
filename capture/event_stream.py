"""
Event Stream - Phase 1.4 Blueprint Upgrade
Tracks window changes and user activity patterns
"""
import time
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import json
import os

@dataclass
class UserEvent:
    """Standardized event for user activity"""
    event_type: str  # 'window_change', 'capture', 'analysis', 'suggestion', 'workflow'
    timestamp: float
    app: str
    window_title: str
    data: Dict[str, Any]
    
    def to_dict(self):
        """Convert event to dictionary safely"""
        # Handle None values gracefully
        safe_window_title = str(self.window_title)[:100] if self.window_title else ""
        safe_app = self.app if self.app else "unknown"
        safe_data = self.data if self.data else {}
        
        # Handle timestamp conversion
        iso_time = ""
        if self.timestamp:
            try:
                iso_time = datetime.fromtimestamp(self.timestamp).isoformat()
            except (ValueError, OSError):
                iso_time = datetime.now().isoformat()
        
        return {
            "type": self.event_type,
            "timestamp": self.timestamp,
            "iso_time": iso_time,
            "app": safe_app,
            "window_title": safe_window_title,
            "data": safe_data
        }


class EventStream:
    def __init__(self, config, tracker):
        self.config = config
        self.tracker = tracker
        self.events: List[UserEvent] = []
        self.last_window: Optional[str] = None
        
        tracker.add_tech_debt(
            item="Basic event stream",
            reason="MVP Phase 1.4 implementation",
            blueprint_feature="Real-time event processing + ML pattern detection"
        )
    
    def log_capture(self, window_info, filename):
        """Log screenshot capture event"""
        # Safely extract values with defaults
        window_title = window_info.get("title") or "Unknown"
        app = window_info.get("app") or "unknown"
        
        event = UserEvent(
            event_type="capture",
            timestamp=time.time(),
            app=app,
            window_title=str(window_title),  # Ensure string
            data={
                "filename": filename or "unknown",
                "type": "screenshot",
                "window_info": {
                    "app": app,
                    "title": window_title
                }
            }
        )
        self.events.append(event)
        
        # Check for window changes
        self._detect_window_change(window_info)
    
    def log_analysis(self, analysis_result):
        """Log analysis event"""
        # Safely extract values with defaults
        window_title = analysis_result.get("window_context") or "Unknown"
        app = analysis_result.get("app_detected") or "unknown"
        activity = analysis_result.get("primary_activity") or "unknown"
        confidence = analysis_result.get("confidence_score", 0.0)
        intent = analysis_result.get("mvp_intent") or "unknown"
        errors = analysis_result.get("potential_errors") or []
        
        event = UserEvent(
            event_type="analysis",
            timestamp=time.time(),
            app=app,
            window_title=str(window_title),  # Ensure string
            data={
                "activity": activity,
                "confidence": float(confidence),
                "intent": intent,
                "errors": list(errors),
                "model_used": analysis_result.get("model_used", "unknown"),
                "local_mode": analysis_result.get("local_mode", False)
            }
        )
        self.events.append(event)
    
    def log_suggestion(self, suggestion, context):
        """Log suggestion event"""
        # Safely extract values with defaults
        window_title = context.get("window_title") or "Unknown"
        app = context.get("app") or "unknown"
        suggestion_text = suggestion or ""
        
        event = UserEvent(
            event_type="suggestion",
            timestamp=time.time(),
            app=app,
            window_title=str(window_title),  # Ensure string
            data={
                "suggestion": str(suggestion_text)[:100],
                "context": context.get("context", "general"),
                "suggestion_length": len(str(suggestion_text))
            }
        )
        self.events.append(event)
    
    def _detect_window_change(self, window_info):
        """Detect when user switches windows"""
        current_window = window_info.get("title") or "Unknown"
        current_app = window_info.get("app") or "unknown"
        
        if self.last_window != current_window:
            event = UserEvent(
                event_type="window_change",
                timestamp=time.time(),
                app=current_app,
                window_title=str(current_window),  # Ensure string
                data={
                    "from": self.last_window or "Unknown",
                    "to": current_window,
                    "change_type": "application_switch",
                    "app_change": True if self.last_window else False
                }
            )
            self.events.append(event)
            self.last_window = current_window
    
    def get_stats(self):
        """Get event stream statistics"""
        # Simple pattern detection
        patterns = {
            "debugging_session": False,
            "design_session": False,
            "research_session": False,
            "working_session": False
        }
        
        # Check last 5 minutes
        cutoff = time.time() - 300
        recent = [e for e in self.events if e.timestamp > cutoff]
        
        if not recent:
            return {
                "total_events": len(self.events),
                "window_changes": sum(1 for e in self.events if e.event_type == "window_change"),
                "captures": sum(1 for e in self.events if e.event_type == "capture"),
                "analyses": sum(1 for e in self.events if e.event_type == "analysis"),
                "suggestions": sum(1 for e in self.events if e.event_type == "suggestion"),
                "active_patterns": patterns,
                "recent_events": len(recent)
            }
        
        # Debugging pattern (errors in analysis)
        error_events = [
            e for e in recent 
            if e.event_type == "analysis" 
            and e.data.get("errors") 
            and len(e.data["errors"]) > 0
        ]
        if len(error_events) >= 2:
            patterns["debugging_session"] = True
        
        # Design pattern (FlutterFlow/Figma)
        design_events = [
            e for e in recent 
            if e.app and e.app.lower() in ["flutterflow", "figma", "design"]
        ]
        if len(design_events) >= 3:
            patterns["design_session"] = True
        
        # Research pattern (window changes)
        window_changes = sum(1 for e in recent if e.event_type == "window_change")
        if window_changes > 5:
            patterns["research_session"] = True
        
        # Working session (multiple captures/analyses)
        if len(recent) >= 5:
            patterns["working_session"] = True
        
        return {
            "total_events": len(self.events),
            "window_changes": sum(1 for e in self.events if e.event_type == "window_change"),
            "captures": sum(1 for e in self.events if e.event_type == "capture"),
            "analyses": sum(1 for e in self.events if e.event_type == "analysis"),
            "suggestions": sum(1 for e in self.events if e.event_type == "suggestion"),
            "active_patterns": patterns,
            "recent_events": len(recent),
            "first_event": self.events[0].timestamp if self.events else None,
            "last_event": self.events[-1].timestamp if self.events else None
        }
    
    def save_events(self):
        """Save events to JSON file"""
        try:
            # Create memory directory if it doesn't exist
            os.makedirs("memory", exist_ok=True)
            
            # Convert events to dictionaries (handle empty list)
            events_data = []
            if self.events:
                # Get last 100 events (or all if less than 100)
                events_to_save = self.events[-100:] if len(self.events) > 100 else self.events
                events_data = [e.to_dict() for e in events_to_save]
            
            # Prepare the data structure
            save_data = {
                "version": "1.0.0",
                "total_events": len(self.events),
                "saved_events": len(events_data),
                "events": events_data,
                "last_updated": datetime.now().isoformat(),
                "stats": self.get_stats()
            }
            
            # Save to file
            with open("memory/event_stream.json", "w") as f:
                json.dump(save_data, f, indent=2, default=str)
            
            # print(f"  ✓ Saved {len(events_data)} events to memory/event_stream.json")
            
        except Exception as e:
            print(f"  ⚠ Could not save events: {e}")
            # Try minimal save
            try:
                with open("memory/event_stream_backup.json", "w") as f:
                    f.write(f"Error in main save: {e}\n")
                    f.write(f"Total events: {len(self.events)}\n")
            except:
                pass
    
    def clear_old_events(self, max_events=1000):
        """Clear old events to prevent memory bloat"""
        if len(self.events) > max_events:
            # Keep only the most recent events
            self.events = self.events[-max_events:]
            print(f"  🧹 Cleared old events, keeping {len(self.events)} most recent")
    
    def get_recent_events(self, event_type=None, limit=10):
        """Get recent events, optionally filtered by type"""
        if event_type:
            filtered = [e for e in self.events if e.event_type == event_type]
            return filtered[-limit:] if filtered else []
        return self.events[-limit:] if self.events else []
    
    def get_user_activity_summary(self, hours=1):
        """Get summary of user activity for last N hours"""
        cutoff = time.time() - (hours * 3600)
        recent = [e for e in self.events if e.timestamp > cutoff]
        
        if not recent:
            return {
                "total_events": 0,
                "apps_used": [],
                "most_active_app": None,
                "suggestions_given": 0
            }
        
        # Count apps used
        app_counter = {}
        for event in recent:
            app = event.app
            app_counter[app] = app_counter.get(app, 0) + 1
        
        # Find most active app
        most_active = max(app_counter.items(), key=lambda x: x[1]) if app_counter else (None, 0)
        
        # Count suggestions
        suggestions = sum(1 for e in recent if e.event_type == "suggestion")
        
        return {
            "total_events": len(recent),
            "apps_used": list(app_counter.keys()),
            "most_active_app": most_active[0],
            "most_active_count": most_active[1],
            "suggestions_given": suggestions,
            "time_period_hours": hours
        }