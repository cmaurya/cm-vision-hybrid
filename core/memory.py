"""
memory.py
=========
MVP Memory System
Phase 1.4: JSON-based memory with simple similarity
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any
import difflib

class MVPMemory:
    """MVP Memory System"""
    
    def __init__(self, memory_file="memory/mvp_memory.json"):
        self.memory_file = memory_file
        os.makedirs(os.path.dirname(memory_file), exist_ok=True)
        self.memory_data = self._load_memory()
    
    def _load_memory(self) -> Dict[str, Any]:
        """Load memory from file"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    # Ensure experiences have proper structure
                    if "experiences" in data:
                        for exp in data["experiences"]:
                            if "analysis" not in exp:
                                exp["analysis"] = {
                                    "app": exp.get("app", "unknown"),
                                    "activity": exp.get("activity", "unknown"),
                                    "error_detected": exp.get("error_detected", False),
                                    "suggestion": exp.get("suggestion", ""),
                                    "mode": exp.get("mode", "unknown")
                                }
                    return data
            except json.JSONDecodeError:
                print("⚠ Memory file corrupted, creating new one")
        
        # Create new memory structure
        return {
            "version": "0.1.1",
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "experiences": [],
            "patterns": []
        }
    
    def save_experience(self, screenshot_path: str, analysis: Dict) -> int:
        """Save an experience to memory"""
        # Create experience entry with analysis properly embedded
        experience = {
            "id": len(self.memory_data.get("experiences", [])) + 1,
            "timestamp": datetime.now().isoformat(),
            "screenshot": screenshot_path,
            "analysis": analysis,  # Store the full analysis object
            "app": analysis.get("app", "unknown"),
            "activity": analysis.get("activity", "unknown"),
            "error_detected": analysis.get("error_detected", False),
            "suggestion": analysis.get("suggestion", ""),
            "mode": analysis.get("mode", "unknown")
        }
        
        # Add to memory
        if "experiences" not in self.memory_data:
            self.memory_data["experiences"] = []
        
        self.memory_data["experiences"].append(experience)
        self.memory_data["last_updated"] = datetime.now().isoformat()
        
        # Save to file
        self._save_memory()
        
        return experience["id"]
    
    def find_similar(self, current_analysis: Dict, limit: int = 5) -> List[Dict]:
        """Find similar past experiences"""
        experiences = self.memory_data.get("experiences", [])
        if not experiences:
            return []
        
        similarities = []
        
        for exp in experiences[-50:]:  # Check last 50 experiences
            # Get analysis from experience - handle both old and new formats
            exp_analysis = exp.get("analysis", {})
            if not exp_analysis:
                # If no analysis field, create one from the experience data
                exp_analysis = {
                    "app": exp.get("app", "unknown"),
                    "activity": exp.get("activity", "unknown"),
                    "error_detected": exp.get("error_detected", False),
                    "suggestion": exp.get("suggestion", ""),
                    "mode": exp.get("mode", "unknown")
                }
            
            similarity_score = self._calculate_similarity(current_analysis, exp_analysis)
            
            if similarity_score > 0.3:  # Threshold
                similarities.append((similarity_score, exp))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[0], reverse=True)
        
        # Return top matches
        return [exp for score, exp in similarities[:limit]]
    
    def _calculate_similarity(self, analysis1: Dict, analysis2: Dict) -> float:
        """Calculate similarity between two analyses"""
        score = 0.0
        
        # Compare app
        app1 = analysis1.get("app", "unknown")
        app2 = analysis2.get("app", "unknown")
        if app1 == app2 and app1 != "unknown":
            score += 0.4
        
        # Compare activity
        activity1 = analysis1.get("activity", "unknown")
        activity2 = analysis2.get("activity", "unknown")
        if activity1 == activity2 and activity1 != "unknown":
            score += 0.3
        
        # Text similarity for suggestion
        suggestion1 = analysis1.get("suggestion", "")
        suggestion2 = analysis2.get("suggestion", "")
        
        if suggestion1 and suggestion2:
            try:
                seq = difflib.SequenceMatcher(None, suggestion1.lower(), suggestion2.lower())
                score += seq.ratio() * 0.3
            except:
                pass  # Ignore similarity calculation errors
        
        return score
    
    def _save_memory(self):
        """Save memory to file"""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory_data, f, indent=2)
        except Exception as e:
            print(f"⚠ Failed to save memory: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory statistics"""
        experiences = self.memory_data.get("experiences", [])
        
        # Count by app
        app_counts = {}
        for exp in experiences:
            app = exp.get("app", "unknown")
            app_counts[app] = app_counts.get(app, 0) + 1
        
        return {
            "total_experiences": len(experiences),
            "app_distribution": app_counts,
            "last_updated": self.memory_data.get("last_updated", "never")
        }