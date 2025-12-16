#!/usr/bin/env python3
"""
CM VISION HYBRID MVP
Day 1: Foundation with Blueprint Migration Path
"""
import sys
import os
import time
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config import MVPConfig
from core.blueprint_tracker import BlueprintTracker
from capture.mvp_screenshot import MVP_Screenshot
from analysis.gemini_analyzer import MVP_GeminiAnalyzer
from memory.mvp_memory import MVP_Memory
from ui.mvp_gui import MVP_GUI

class CMVisionHybrid:
    """Hybrid MVP System - Simple but blueprint-ready"""
    def __init__(self):
        print("\n" + "="*70)
        print("🧠 CM VISION HYBRID MVP v0.1.1")
        print("Simple today, visionary tomorrow")
        print("="*70)
        
        # Load configuration
        print("\n[1/5] Loading configuration...")
        self.config = MVPConfig()
        print(f"✓ Mode: {'MVP' if self.config.is_mvp else 'Blueprint'}")
        
        # Initialize blueprint tracker
        print("\n[2/5] Initializing blueprint tracker...")
        self.tracker = BlueprintTracker(self.config)
        print("✓ MVP→Blueprint migration path created")
        
        # Initialize components
        print("\n[3/5] Initializing components...")
        
        # Capture
        self.capture = MVP_Screenshot(self.config, self.tracker)
        print("  ✓ MVP capture ready")
        
        # Analysis
        self.analyzer = MVP_GeminiAnalyzer(self.config, self.tracker)
        print("  ✓ Gemini analyzer ready")
        
        # Memory
        self.memory = MVP_Memory(self.config, self.tracker)
        print("  ✓ MVP memory ready")
        
        # GUI (will be initialized when needed)
        self.gui = None
        
        # Suggestion engine (simple)
        self.last_suggestions = []
        
        # Stats
        self.stats = {
            "start_time": time.time(),
            "captures": 0,
            "gemini_calls": 0,
            "memory_saves": 0,
            "mvp_mode": self.config.is_mvp,
            "suggestions_given": 0
        }
        
        print("\n[4/5] System initialized!")
        print(f"   📸 Screenshots: {self.config.screenshots_dir}/")
        print(f"   💾 Memory: {self.config.memory_file}")
        print(f"   ⏱️ Capture interval: {self.config.capture_interval}s")
        print(f"   🔌 Enabled plugins: {self.config.enabled_plugins}")
        
        # Show blueprint status
        print("\n[5/5] Blueprint status:")
        blueprint_features = self.config.blueprint_features()
        for feature, disabled in blueprint_features.items():
            status = "🔴 POSTPONED" if disabled else "🟢 INCLUDED"
            print(f"   {status} {feature}")
        
        print("\n" + "="*70)
        print("READY! Starting in MVP mode.")
        print("Check 'mvp_tracker.json' for migration path.")
        print("="*70)
    
    def capture_and_analyze(self):
        """Main capture→analyze→memory→suggest pipeline"""
        try:
            # Step 1: Capture
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"\n[{timestamp}] Capture...")
            screenshot_data = self.capture.capture()
            
            if not screenshot_data:
                print("  ✗ Capture failed")
                return None
            
            self.stats["captures"] += 1
            print(f"  ✓ Saved: {screenshot_data['window_info']['filename']}")
            
            # Step 2: Analyze with Gemini
            print("  Analyzing with Gemini...")
            analysis = self.analyzer.analyze_screen(
                screenshot_data["image"],
                screenshot_data["window_info"]
            )
            
            self.stats["gemini_calls"] += 1
            
            # Step 3: Save to memory
            print("  Saving to memory...")
            memory_id = self.memory.save_experience(screenshot_data, analysis)
            
            self.stats["memory_saves"] += 1
            print(f"  ✓ Memory ID: {memory_id}")
            
            # Step 4: Find similar past experiences
            similar = self.memory.find_similar(analysis, limit=3)
            if similar:
                print(f"  🔍 Found {len(similar)} similar past experiences")
                analysis["similar_past"] = similar
            
            # Step 5: Check for proactive suggestions
            suggestion = self._check_for_suggestion(analysis, similar)
            if suggestion:
                print(f"  💡 Suggestion: {suggestion[:100]}...")
                self.stats["suggestions_given"] += 1
                analysis["suggestion"] = suggestion
            
            # Prepare result
            result = {
                "screenshot": screenshot_data,
                "analysis": analysis,
                "memory_id": memory_id,
                "timestamp": datetime.now().isoformat(),
                "has_suggestion": bool(suggestion)
            }
            
            print(f"  ✅ Pipeline complete")
            
            return result
            
        except Exception as e:
            print(f"  ✗ Pipeline error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _check_for_suggestion(self, analysis, similar_experiences):
        """MVP: Simple suggestion engine"""
        # Check if we should give a suggestion
        errors = analysis.get("potential_errors", [])
        
        # If there are errors
        if errors and len(errors) > 0:
            error_text = " ".join(errors).lower()
            
            # Check for Firebase errors
            if any(word in error_text for word in ["firebase", "permission", "security", "unauthorized"]):
                return "Check Firebase security rules. Common fix: allow read/write only for authenticated users."
            
            # Check for database errors
            if any(word in error_text for word in ["database", "query", "sql", "select"]):
                return "Verify your database query syntax. Check table names and permissions."
            
            # Check for similar past solutions
            if similar_experiences:
                for exp in similar_experiences:
                    exp_errors = exp["experience"].get("errors", [])
                    if exp_errors and len(exp_errors) > 0:
                        return f"Similar error solved before. Check past experience #{exp['experience'].get('id', 'N/A')}"
        
        # Check for stuck state (same app/activity multiple times)
        recent_exps = self.memory.memory.get("experiences", [])[-5:]
        if len(recent_exps) >= 3:
            recent_apps = [exp.get("app") for exp in recent_exps[-3:]]
            if all(app == analysis.get("app_detected") for app in recent_apps if app != "unknown"):
                return f"You've been working in {analysis.get('app_detected')} for a while. Need help?"
        
        return None
    
    def get_stats(self):
        """Get system statistics"""
        memory_stats = self.memory.get_stats()
        
        return {
            **self.stats,
            "memory_items": memory_stats.get("total_experiences", 0),
            "uptime": time.time() - self.stats["start_time"],
            "mode": "MVP Hybrid",
            "suggestions": self.stats["suggestions_given"]
        }
    
    def run_gui(self):
        """Run with GUI"""
        print("\n🚀 Launching MVP GUI...")
        self.gui = MVP_GUI(self)
        self.gui.run()
    
    def run_cli(self):
        """Run in CLI mode"""
        print("\n📟 Running in CLI mode (Ctrl+C to stop)")
        print(f"Capturing every {self.config.capture_interval} seconds\n")
        
        try:
            while True:
                result = self.capture_and_analyze()
                
                if result:
                    # Show simple output
                    analysis = result["analysis"]
                    print(f"  App: {analysis.get('app_detected')}")
                    print(f"  Activity: {analysis.get('primary_activity')}")
                    
                    if analysis.get("similar_past"):
                        print(f"  Similar past: {len(analysis['similar_past'])} found")
                    
                    if analysis.get("suggestion"):
                        print(f"  💡 Suggestion: {analysis['suggestion']}")
                
                # Wait for next capture
                time.sleep(self.config.capture_interval)
                
        except KeyboardInterrupt:
            print("\n\n👋 Stopped by user")
    
    def run_single(self):
        """Run single capture and exit"""
        print("\n📸 Single capture mode...")
        result = self.capture_and_analyze()
        if result:
            print(f"\n✅ SUCCESS: Captured and analyzed")
            print(f"   App: {result['analysis'].get('app_detected')}")
            print(f"   Activity: {result['analysis'].get('primary_activity')}")
            print(f"   Confidence: {result['analysis'].get('confidence_score', 0)*100:.1f}%")
            
            if result['analysis'].get('suggestion'):
                print(f"   💡 Suggestion: {result['analysis'].get('suggestion')}")
        else:
            print("\n❌ Capture failed")
    
    def cleanup(self):
        """Cleanup resources"""
        print("\n🧹 Cleaning up...")
        
        # Show final stats
        print(f"\n📊 FINAL STATS:")
        print(f"  Total captures: {self.stats['captures']}")
        print(f"  Gemini API calls: {self.stats['gemini_calls']}")
        print(f"  Memory items: {self.memory.memory['stats']['total_experiences']}")
        print(f"  Suggestions given: {self.stats['suggestions_given']}")
        
        # Show blueprint tracker status
        print("\n📋 BLUEPRINT TRACKER STATUS:")
        self.tracker.show_status()

def main():
    """Main entry point"""
    try:
        # Initialize system
        system = CMVisionHybrid()
        
        # Ask for mode
        print("\n🎮 CHOOSE OPERATION MODE:")
        print("  1. GUI Mode (Recommended for MVP)")
        print("  2. CLI Mode (Terminal only)")
        print("  3. Single Capture & Exit")
        print("  4. Test Mode (Quick validation)")
        
        choice = input("\nChoice (1-4): ").strip()
        
        if choice == "1":
            system.run_gui()
        elif choice == "2":
            system.run_cli()
        elif choice == "3":
            system.run_single()
        elif choice == "4":
            print("\n🧪 TEST MODE: Quick validation...")
            # Quick test
            result = system.capture_and_analyze()
            if result:
                print("\n✅ TEST PASSED:")
                print(f"  - Capture: ✓")
                print(f"  - Analysis: ✓")
                print(f"  - Memory save: ✓")
                print(f"  - App detected: {result['analysis'].get('app_detected')}")
            else:
                print("\n❌ TEST FAILED")
        else:
            print("Invalid choice. Running GUI mode.")
            system.run_gui()
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Stopped by user")
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'system' in locals():
            system.cleanup()
        
        print("\n" + "="*70)
        print("CM Vision Hybrid MVP - Execution Complete")
        print("MVP built, Blueprint path ready")
        print("Check 'mvp_tracker.json' for migration plan")
        print("="*70)

if __name__ == "__main__":
    main()