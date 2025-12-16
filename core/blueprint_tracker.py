"""
TRACKS: What MVP features exist vs Blueprint postponed features
This file ensures we don't forget the grand vision while building MVP
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any

class BlueprintTracker:
    def __init__(self, config):
        self.config = config
        self.tracker_file = "mvp_tracker.json"
        self.blueprint = self._load_blueprint_structure()
        
        # Initialize tracker
        if not os.path.exists(self.tracker_file):
            self._init_tracker()
    
    def _load_blueprint_structure(self):
        """Load the 6-phase blueprint structure"""
        return {
            "phase_1": {
                "name": "Active Perception Engine",
                "mvp_status": "partial",
                "components": {
                    "enriched_capture": {"mvp": True, "blueprint": True, "notes": "MVP has basic capture"},
                    "visual_understanding": {"mvp": True, "blueprint": True, "notes": "Gemini from Day 1 ✓"},
                    "intent_inference": {"mvp": "basic", "blueprint": "advanced", "notes": "MVP: simple rules"},
                    "event_stream": {"mvp": False, "blueprint": True, "notes": "POSTPONED: For Phase 1.4"},
                }
            },
            "phase_2": {
                "name": "Lifelong Memory System",
                "mvp_status": "minimal",
                "components": {
                    "vector_embedding": {"mvp": False, "blueprint": True, "notes": "POSTPONED: JSON file for now"},
                    "hybrid_search": {"mvp": False, "blueprint": True, "notes": "POSTPONED: Simple text search"},
                    "memory_graph": {"mvp": False, "blueprint": True, "notes": "POSTPONED: Linear history only"},
                    "recall_engine": {"mvp": "basic", "blueprint": "advanced", "notes": "MVP: Last 10 similar"},
                }
            },
            "phase_3": {
                "name": "Cognitive Reasoning Core",
                "mvp_status": "none",
                "components": {
                    "orchestrator_agent": {"mvp": False, "blueprint": True, "notes": "POSTPONED: Simple direct calls"},
                    "specialist_agents": {"mvp": False, "blueprint": True, "notes": "POSTPONED: One-size-fits-all"},
                    "knowledge_graph": {"mvp": False, "blueprint": True, "notes": "POSTPONED: Hardcoded FlutterFlow"},
                    "proactive_engine": {"mvp": False, "blueprint": True, "notes": "POSTPONED: Reactive only in MVP"},
                }
            },
            "phase_4": {
                "name": "Seamless Interface",
                "mvp_status": "minimal",
                "components": {
                    "overlay_gui": {"mvp": False, "blueprint": True, "notes": "POSTPONED: Separate window"},
                    "highlighting": {"mvp": False, "blueprint": True, "notes": "POSTPONED: Text only"},
                    "multimodal_output": {"mvp": False, "blueprint": True, "notes": "POSTPONED: Text only"},
                    "privacy_sandbox": {"mvp": False, "blueprint": True, "notes": "POSTPONED: Basic opt-out"},
                }
            },
            "phase_5": {
                "name": "Universal Adapter Layer",
                "mvp_status": "none",
                "components": {
                    "plugin_architecture": {"mvp": False, "blueprint": True, "notes": "POSTPONED: Hardcoded"},
                    "tool_parsers": {"mvp": "flutterflow_only", "blueprint": "universal", "notes": "MVP: One domain"},
                    "action_api": {"mvp": False, "blueprint": True, "notes": "POSTPONED: Manual actions"},
                }
            },
            "phase_6": {
                "name": "Deployment & Growth",
                "mvp_status": "none",
                "components": {
                    "beta_packaging": {"mvp": False, "blueprint": True, "notes": "POSTPONED: Run from source"},
                    "telemetry": {"mvp": False, "blueprint": True, "notes": "POSTPONED: Local logs only"},
                    "community_platform": {"mvp": False, "blueprint": True, "notes": "POSTPONED: Manual sharing"},
                }
            }
        }
    
    def _init_tracker(self):
        """Initialize the tracker file"""
        tracker = {
            "project": "CM Vision Hybrid MVP",
            "version": "0.1.0",
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "current_focus": "MVP Day 1: Foundation & Basic Capture",
            "blueprint_status": self.blueprint,
            "postponed_features": [],
            "tech_debt": [],
            "mvp_milestones": [
                {"id": 1, "name": "Day 1: Basic Capture & Analysis", "status": "in_progress"},
                {"id": 2, "name": "Day 3: Simple Memory System", "status": "pending"},
                {"id": 3, "name": "Day 7: Basic GUI", "status": "pending"},
                {"id": 4, "name": "Day 14: FlutterFlow Help", "status": "pending"},
                {"id": 5, "name": "Day 30: MVP Complete", "status": "pending"},
            ],
            "blueprint_migration_path": [
                {"phase": 1, "feature": "Event Stream", "prerequisite": "MVP stable", "effort": "2 days"},
                {"phase": 2, "feature": "Vector Database", "prerequisite": "Supabase setup", "effort": "5 days"},
                {"phase": 2, "feature": "Memory Graph", "prerequisite": "Vector DB done", "effort": "3 days"},
                {"phase": 3, "feature": "Orchestrator Agent", "prerequisite": "Memory working", "effort": "7 days"},
                {"phase": 4, "feature": "Overlay GUI", "prerequisite": "PyQt6 learned", "effort": "10 days"},
                {"phase": 5, "feature": "Plugin System", "prerequisite": "Overlay stable", "effort": "14 days"},
            ]
        }
        
        with open(self.tracker_file, 'w') as f:
            json.dump(tracker, f, indent=2)
        
        print("✓ Blueprint tracker initialized")
        print("  MVP → Blueprint migration path documented")
    
    def log_mvp_completion(self, component: str, notes: str = ""):
        """Log when an MVP component is completed"""
        with open(self.tracker_file, 'r') as f:
            tracker = json.load(f)
        
        # Update blueprint status if this completes a component
        for phase_name, phase in tracker['blueprint_status'].items():
            for comp_name, comp_data in phase['components'].items():
                if comp_name in component.lower():
                    if comp_data['mvp'] == False:
                        comp_data['mvp'] = "partial"
                        comp_data['notes'] = f"MVP basic version: {notes}"
        
        tracker['last_updated'] = datetime.now().isoformat()
        
        with open(self.tracker_file, 'w') as f:
            json.dump(tracker, f, indent=2)
        
        print(f"✓ MVP progress logged: {component}")
    
    def add_tech_debt(self, item: str, reason: str, blueprint_feature: str):
        """Add technical debt (MVP shortcuts that need blueprint fixing)"""
        with open(self.tracker_file, 'r') as f:
            tracker = json.load(f)
        
        tracker['tech_debt'].append({
            "item": item,
            "reason": reason,
            "blueprint_feature": blueprint_feature,
            "added": datetime.now().isoformat(),
            "status": "pending"
        })
        
        with open(self.tracker_file, 'w') as f:
            json.dump(tracker, f, indent=2)
        
        print(f"⚠ Tech debt logged: {item} -> Will fix with {blueprint_feature}")
    
    def get_next_blueprint_upgrade(self):
        """Get the next blueprint feature to implement after MVP"""
        with open(self.tracker_file, 'r') as f:
            tracker = json.load(f)
        
        for item in tracker['blueprint_migration_path']:
            if item.get('status', 'pending') == 'pending':
                return item
        
        return None
    
    def show_status(self):
        """Display current MVP vs Blueprint status"""
        with open(self.tracker_file, 'r') as f:
            tracker = json.load(f)
        
        print("\n" + "="*60)
        print("MVP vs BLUEPRINT TRACKER")
        print("="*60)
        
        mvp_count = 0
        blueprint_count = 0
        
        for phase_name, phase in tracker['blueprint_status'].items():
            print(f"\n{phase['name'].upper()}: {phase['mvp_status']}")
            
            for comp_name, comp_data in phase['components'].items():
                status = "✓" if comp_data['mvp'] else "✗"
                if comp_data['mvp'] == "partial" or comp_data['mvp'] == "basic":
                    status = "~"
                
                if comp_data['mvp']:
                    mvp_count += 1
                if comp_data['blueprint']:
                    blueprint_count += 1
                
                print(f"  {status} {comp_name}: {comp_data['notes']}")
        
        print(f"\n📊 SUMMARY: {mvp_count} MVP features, {blueprint_count} Blueprint targets")
        
        # Show next upgrade
        next_upgrade = self.get_next_blueprint_upgrade()
        if next_upgrade:
            print(f"\n➡ NEXT BLUEPRINT UPGRADE: {next_upgrade['feature']} ({next_upgrade['effort']})")
        
        return tracker