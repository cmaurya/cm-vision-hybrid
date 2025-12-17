"""
blueprint_tracker.py
====================
Tracks migration from MVP to full Blueprint system.
Phase 1.4: Enhanced tracking with progress calculation
"""

import os
import json
import time
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
import hashlib

@dataclass
class BlueprintComponent:
    """Represents a component from the blueprint"""
    name: str
    description: str
    phase: int  # 1-5
    status: str  # postponed, included, planned, completed
    priority: int  # 1-5, 1 = highest
    tech_debt: str = ""
    dependencies: List[str] = None
    estimated_effort: int = 0  # hours
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

@dataclass 
class MVPTracker:
    """Tracks MVP implementation progress"""
    version: str = "0.1.1"
    start_date: str = ""
    last_updated: str = ""
    total_captures: int = 0
    gemini_calls: int = 0
    memory_items: int = 0
    suggestions_given: int = 0
    events_logged: int = 0
    active_patterns: List[str] = None
    tech_debt_items: List[str] = None
    
    def __post_init__(self):
        if self.active_patterns is None:
            self.active_patterns = []
        if self.tech_debt_items is None:
            self.tech_debt_items = []
        if not self.start_date:
            self.start_date = datetime.now().strftime("%Y-%m-%d")

class BlueprintTracker:
    """Main tracker class"""
    
    def __init__(self, config_path: str = "config/mvp_config.json"):
        self.config_path = config_path
        self.tracker_file = "mvp_tracker.json"
        self.blueprint_file = "config/blueprint_components.json"
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize tracker data
        self.tracker_data = self._load_or_create_tracker()
        
        # Blueprint components
        self.components = self._load_blueprint_components()
        
        # Current MVP state
        self.mvp_state = MVPTracker()
        
        # Ensure overall_progress key exists
        if 'overall_progress' not in self.tracker_data:
            self.tracker_data['overall_progress'] = 0
        
    def _load_config(self) -> Dict:
        """Load MVP configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"mode": "MVP", "version": "0.1.1"}
    
    def _load_or_create_tracker(self) -> Dict:
        """Load existing tracker or create new one"""
        if os.path.exists(self.tracker_file):
            try:
                with open(self.tracker_file, 'r') as f:
                    data = json.load(f)
                    # Ensure all required keys exist
                    required_keys = ['overall_progress', 'current_phase', 'components', 'milestones']
                    for key in required_keys:
                        if key not in data:
                            data[key] = 0 if key == 'overall_progress' else [] if key in ['components', 'milestones'] else 'Phase 1'
                    return data
            except json.JSONDecodeError:
                print("⚠ Tracker file corrupted, creating new one")
        
        # Create new tracker
        return {
            "version": "0.1.1",
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "overall_progress": 0,
            "current_phase": "Phase 1",
            "components": [],
            "milestones": [],
            "tech_debt": []
        }
    
    def _load_blueprint_components(self) -> List[BlueprintComponent]:
        """Load blueprint components from file or create defaults"""
        if os.path.exists(self.blueprint_file):
            try:
                with open(self.blueprint_file, 'r') as f:
                    components_data = json.load(f)
                    return [BlueprintComponent(**comp) for comp in components_data]
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Default blueprint components (from the blueprint doc)
        return [
            BlueprintComponent(
                name="vector_database",
                description="Supabase pgvector for embeddings",
                phase=2,
                status="postponed",
                priority=1,
                tech_debt="JSON file memory",
                dependencies=["supabase_setup"],
                estimated_effort=8
            ),
            BlueprintComponent(
                name="graph_database",
                description="Neo4j for knowledge graph",
                phase=2,
                status="postponed", 
                priority=2,
                tech_debt="Basic text similarity",
                dependencies=["vector_database"],
                estimated_effort=12
            ),
            BlueprintComponent(
                name="advanced_overlay",
                description="PyQt6 overlay system",
                phase=4,
                status="postponed",
                priority=3,
                tech_debt="Tkinter basic GUI",
                dependencies=["prevention_system"],
                estimated_effort=16
            ),
            BlueprintComponent(
                name="plugin_system",
                description="Extensible plugin architecture",
                phase=5,
                status="postponed",
                priority=4,
                tech_debt="Hardcoded plugins",
                dependencies=["advanced_overlay"],
                estimated_effort=20
            ),
            BlueprintComponent(
                name="telemetry",
                description="Event stream analytics",
                phase=1,
                status="included",
                priority=1,
                tech_debt="Basic event stream",
                dependencies=[],
                estimated_effort=4
            ),
            BlueprintComponent(
                name="proactive_engine",
                description="4-level intervention system",
                phase=3,
                status="included",
                priority=2,
                tech_debt="Reactive suggestions only",
                dependencies=["pattern_detection"],
                estimated_effort=24
            ),
            BlueprintComponent(
                name="cross_domain",
                description="Multi-channel monitoring",
                phase=2,
                status="included",
                priority=1,
                tech_debt="Full screen capture only",
                dependencies=["event_stream"],
                estimated_effort=12
            )
        ]
    
    def update_progress(self, component_name: str, status: str, notes: str = ""):
        """Update progress for a specific component"""
        # Find the component
        component = next((c for c in self.components if c.name == component_name), None)
        if not component:
            print(f"⚠ Component {component_name} not found in blueprint")
            return
        
        # Update component status
        old_status = component.status
        component.status = status
        
        # Add to tracker
        update = {
            "timestamp": datetime.now().isoformat(),
            "component": component_name,
            "old_status": old_status,
            "new_status": status,
            "notes": notes
        }
        
        self.tracker_data["components"].append(update)
        
        # Recalculate overall progress
        self._calculate_overall_progress()
        
        # Save
        self._save_tracker()
        
        print(f"✓ Progress updated: {component_name} -> {status}")
    
    def _calculate_overall_progress(self):
        """Calculate overall progress percentage"""
        total_components = len(self.components)
        if total_components == 0:
            self.tracker_data['overall_progress'] = 0
            return
        
        # Weight components by priority
        completed_score = 0
        total_score = 0
        
        status_weights = {
            "completed": 1.0,
            "included": 0.75,
            "in_progress": 0.5,
            "planned": 0.25,
            "postponed": 0.0
        }
        
        for component in self.components:
            weight = 6 - component.priority  # Higher priority = higher weight
            status_weight = status_weights.get(component.status, 0)
            completed_score += weight * status_weight
            total_score += weight
        
        if total_score > 0:
            progress = int((completed_score / total_score) * 100)
            self.tracker_data['overall_progress'] = progress
    
    def log_tech_debt(self, component: str, debt: str):
        """Log technical debt for a component"""
        debt_entry = {
            "timestamp": datetime.now().isoformat(),
            "component": component,
            "debt": debt,
            "status": "pending"
        }
        
        self.tracker_data.setdefault("tech_debt", []).append(debt_entry)
        
        # Also update component
        comp = next((c for c in self.components if c.name == component), None)
        if comp:
            comp.tech_debt = debt
        
        self._save_tracker()
        
        print(f"⚠ Tech debt logged: {debt}")
    
    def log_milestone(self, milestone: str, details: str = ""):
        """Log a development milestone"""
        milestone_entry = {
            "timestamp": datetime.now().isoformat(),
            "milestone": milestone,
            "details": details
        }
        
        self.tracker_data.setdefault("milestones", []).append(milestone_entry)
        self._save_tracker()
        
        print(f"🎯 Milestone: {milestone}")
    
    def update_mvp_stats(self, stats: Dict):
        """Update MVP statistics"""
        for key, value in stats.items():
            if hasattr(self.mvp_state, key):
                setattr(self.mvp_state, key, value)
        
        # Update tracker
        self.tracker_data["last_updated"] = datetime.now().isoformat()
        self.tracker_data["mvp_stats"] = asdict(self.mvp_state)
        self._save_tracker()
    
    def show_status(self):
        """Display current MVP vs Blueprint status"""
        print("\n" + "=" * 60)
        print("MVP vs BLUEPRINT TRACKER")
        print("=" * 60)
        
        # Get tracker data safely with defaults
        tracker = self.tracker_data
        progress = tracker.get('overall_progress', 0)
        phase = tracker.get('current_phase', 'Phase 1')
        
        print(f"Phase: {phase}")
        print(f"Overall Progress: {progress}%")
        print(f"Last Updated: {tracker.get('last_updated', 'N/A')}")
        
        # MVP Stats
        print("\n📊 MVP STATISTICS:")
        if 'mvp_stats' in tracker:
            stats = tracker['mvp_stats']
            print(f"  • Version: {stats.get('version', 'N/A')}")
            print(f"  • Captures: {stats.get('total_captures', 0)}")
            print(f"  • Memory Items: {stats.get('memory_items', 0)}")
            print(f"  • Suggestions: {stats.get('suggestions_given', 0)}")
        
        # Component Status
        print("\n🔧 COMPONENT STATUS:")
        for component in self.components:
            status_icon = "🟢" if component.status in ["included", "completed"] else "🟡" if component.status == "in_progress" else "🔴"
            print(f"  {status_icon} {component.name:20} {component.status:12} (Phase {component.phase})")
        
        # Recent Tech Debt
        tech_debt = tracker.get('tech_debt', [])
        if tech_debt and len(tech_debt) > 0:
            print("\n⚠ RECENT TECH DEBT:")
            for debt in tech_debt[-3:]:  # Show last 3
                print(f"  • {debt.get('component', 'unknown')}: {debt.get('debt', 'N/A')}")
        
        # Migration Path
        print("\n🛣️  MIGRATION PATH (Next 3 items):")
        next_items = sorted(
            [c for c in self.components if c.status in ["postponed", "planned"]],
            key=lambda x: (x.priority, x.phase)
        )[:3]
        
        for i, item in enumerate(next_items, 1):
            print(f"  {i}. {item.name}: {item.description}")
            print(f"     Phase {item.phase}, Priority {item.priority}, Effort: {item.estimated_effort}h")
        
        print("=" * 60)
    
    def get_migration_path(self) -> List[Dict]:
        """Get the migration path from MVP to full blueprint"""
        path = []
        
        # Group by phase
        for phase in range(1, 6):
            phase_components = [c for c in self.components if c.phase == phase]
            if phase_components:
                path.append({
                    "phase": f"Phase {phase}",
                    "components": [
                        {
                            "name": c.name,
                            "priority": c.priority,
                            "status": c.status,
                            "dependencies": c.dependencies,
                            "effort": c.estimated_effort
                        }
                        for c in sorted(phase_components, key=lambda x: x.priority)
                    ]
                })
        
        return path
    
    def generate_report(self) -> str:
        """Generate a comprehensive report"""
        report = []
        report.append("=" * 60)
        report.append("CM VISION - BLUEPRINT MIGRATION REPORT")
        report.append("=" * 60)
        
        # Summary
        report.append(f"\n📅 Report Generated: {datetime.now().isoformat()}")
        report.append(f"📈 Overall Progress: {self.tracker_data.get('overall_progress', 0)}%")
        report.append(f"🎯 Current Phase: {self.tracker_data.get('current_phase', 'Phase 1')}")
        
        # Component Breakdown
        report.append("\n🔧 COMPONENT BREAKDOWN:")
        status_counts = {}
        for component in self.components:
            status_counts[component.status] = status_counts.get(component.status, 0) + 1
        
        for status, count in status_counts.items():
            report.append(f"  {status}: {count}")
        
        # Tech Debt Summary
        tech_debt = self.tracker_data.get('tech_debt', [])
        if tech_debt:
            report.append(f"\n⚠ TECHNICAL DEBT: {len(tech_debt)} items")
            for debt in tech_debt[-5:]:
                report.append(f"  • {debt.get('component')}: {debt.get('debt')}")
        
        # Recommendations
        report.append("\n🎯 RECOMMENDED NEXT STEPS:")
        next_steps = self.get_migration_path()
        for phase in next_steps[:2]:  # Next 2 phases
            report.append(f"\n{phase['phase']}:")
            for comp in phase['components'][:3]:  # Top 3 per phase
                if comp['status'] in ['postponed', 'planned']:
                    report.append(f"  • {comp['name']} (Priority: {comp['priority']})")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)
    
    def _save_tracker(self):
        """Save tracker data to file"""
        self.tracker_data["last_updated"] = datetime.now().isoformat()
        
        # Ensure overall_progress exists before saving
        if 'overall_progress' not in self.tracker_data:
            self.tracker_data['overall_progress'] = 0
        
        try:
            with open(self.tracker_file, 'w') as f:
                json.dump(self.tracker_data, f, indent=2)
        except Exception as e:
            print(f"⚠ Failed to save tracker: {e}")
    
    def get_component(self, name: str) -> Optional[BlueprintComponent]:
        """Get a component by name"""
        return next((c for c in self.components if c.name == name), None)
    
    def mark_completed(self, component_name: str):
        """Mark a component as completed"""
        self.update_progress(component_name, "completed", "Manual completion")

# Singleton instance for easy access
_tracker_instance = None

def get_tracker(config_path: str = "config/mvp_config.json") -> BlueprintTracker:
    """Get or create tracker instance"""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = BlueprintTracker(config_path)
    return _tracker_instance

if __name__ == "__main__":
    # Test the tracker
    tracker = BlueprintTracker()
    tracker.show_status()
    
    # Generate report
    report = tracker.generate_report()
    print("\n" + report)
    
    # Save to file
    with open("blueprint_report.txt", "w") as f:
        f.write(report)
    
    print("✓ Tracker test complete. Report saved to blueprint_report.txt")