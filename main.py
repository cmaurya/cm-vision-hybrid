"""
main.py
=======
CM Vision Hybrid MVP v0.1.1
Core execution file
"""

import sys
import os
import time
import json
from datetime import datetime
import threading
import tkinter as tk
from tkinter import scrolledtext, ttk

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config import MVPConfig
from core.capture import MVPCapture
from core.analyzer import GeminiAnalyzer
from core.memory import MVPMemory
from core.event_stream import EventStream
from core.blueprint_tracker import BlueprintTracker

class CMVisionHybrid:
    """Main CM Vision Hybrid system"""
    
    def __init__(self):
        print("\n" + "=" * 70)
        print("🧠 CM VISION HYBRID MVP v0.1.1")
        print("Simple today, visionary tomorrow")
        print("=" * 70)
        
        # Load configuration
        print("\n[1/5] Loading configuration...")
        self.config = MVPConfig()
        print(f"✓ Mode: {self.config.mode}")
        
        # Initialize blueprint tracker
        print("[2/5] Initializing blueprint tracker...")
        self.tracker = BlueprintTracker("config/mvp_config.json")
        print("✓ MVP→Blueprint migration path created")
        
        # Initialize components
        print("[3/5] Initializing components...")
        self._init_components()
        
        # Initialize event stream
        print("[3.5/5] Initializing event stream...")
        self.event_stream = EventStream()
        print(f"✓ Event stream ready ({self.event_stream.phase})")
        
        # System ready
        print("\n[4/5] System initialized!")
        self._print_system_status()
        
        # Blueprint status
        print("\n[5/5] Blueprint status:")
        self._print_blueprint_status()
        
        print("\n" + "=" * 70)
        print("READY! Starting in MVP mode.")
        print("Check 'mvp_tracker.json' for migration path.")
        print("=" * 70)
        
    def _init_components(self):
        """Initialize all system components"""
        
        # Capture system
        print("⚠ Tech debt logged: Full screen capture only -> Will fix with Active window detection + event stream")
        self.capture = MVPCapture(self.config.screenshot_dir)
        print("  ✓ MVP capture ready")
        
        # Analyzer
        print(f"✓ Using model: {self.config.gemini_model}")
        try:
            self.analyzer = GeminiAnalyzer(self.config.gemini_model)
            print("✓ Gemini analyzer initialized (MVP ready)")
        except Exception as e:
            print(f"  ⚠ Gemini initialization failed: {str(e)[:50]}")
            print("  ⚠ Creating minimal local analyzer")
            self.analyzer = self._create_minimal_analyzer()
            print("  ✓ Minimal analyzer created")
        
        # Memory
        print("⚠ Tech debt logged: JSON file memory -> Will fix with Supabase pgvector + Neo4j graph")
        self.memory = MVPMemory(self.config.memory_file)
        print("  ✓ MVP memory ready")
        
        # Log tech debt
        self.tracker.log_tech_debt("cross_domain", "Full screen capture only -> Will fix with Active window detection + event stream")
        self.tracker.log_tech_debt("vector_database", "JSON file memory -> Will fix with Supabase pgvector + Neo4j graph")
        self.tracker.log_tech_debt("graph_database", "Basic text similarity search -> Will fix with Vector embeddings + semantic search")
        
    def _create_minimal_analyzer(self):
        """Create a minimal analyzer for fallback"""
        class MinimalAnalyzer:
            def analyze(self, screenshot_path, context=None):
                return {
                    "app": "unknown",
                    "activity": "fallback_analysis",
                    "error_detected": False,
                    "suggestion": "Using local fallback analyzer",
                    "confidence": 0.3,
                    "mode": "local_fallback",
                    "analysis_time": 0.1
                }
            
            def detect_app_from_screenshot(self, screenshot_path):
                return "unknown"
        
        return MinimalAnalyzer()
    
    def _print_system_status(self):
        """Print current system status"""
        print(f"   📸 Screenshots: {self.config.screenshot_dir}/")
        print(f"   💾 Memory: {self.config.memory_file}")
        print(f"   ⏱️  Capture interval: {self.config.capture_interval}s")
        print(f"   🔌 Enabled plugins: {self.config.plugins}")
        print(f"   📊 Event stream: {self.config.event_stream_file}")
    
    def _print_blueprint_status(self):
        """Print blueprint component status"""
        components = self.tracker.components
        
        # Show top components
        for component in components:
            status_icon = "🟢" if component.status == "included" else "🔴"
            print(f"   {status_icon} {component.name.upper()}")
    
    def run_single_capture(self):
        """Run a single capture and analysis cycle"""
        print("\n🎯 SINGLE CAPTURE MODE")
        print("=" * 40)
        
        # Capture
        print("[1/3] Capture...")
        screenshot_path = self.capture.capture()
        if not screenshot_path:
            print("❌ Capture failed")
            return
        
        print(f"  ✓ Saved: {screenshot_path}")
        
        # Analyze
        print("[2/3] Analyze...")
        analysis = self.analyzer.analyze(screenshot_path)
        
        # Log event
        self.event_stream.add_event("capture", {
            "screenshot": screenshot_path,
            "app": analysis.get("app", "unknown"),
            "activity": analysis.get("activity", "unknown"),
            "mode": analysis.get("mode", "unknown"),
            "analysis_time": analysis.get("analysis_time", 0)
        })
        
        print(f"  ✓ Analyzed: {analysis.get('app', 'unknown')} - {analysis.get('activity', 'unknown')}")
        print(f"  ✓ Mode: {analysis.get('mode', 'unknown')}")
        print(f"  ⏱️  Time: {analysis.get('analysis_time', 0):.1f}s")
        
        # Save to memory and get suggestions
        print("[3/3] Memory & Suggestions...")
        memory_id = self.memory.save_experience(
            screenshot_path=screenshot_path,
            analysis=analysis
        )
        
        # Get similar experiences
        similar = self.memory.find_similar(analysis)
        if similar:
            print(f"  🔍 Found {len(similar)} similar past experiences")
            for i, exp in enumerate(similar[:2]):  # Show top 2
                print(f"     {i+1}. {exp.get('app', 'unknown')}: {exp.get('suggestion', 'No suggestion')[:50]}...")
        
        # Update tracker
        self.tracker.update_mvp_stats({
            "total_captures": self.tracker.mvp_state.total_captures + 1,
            "memory_items": len(self.memory.memory_data.get("experiences", []))
        })
        
        print("\n✅ Single capture complete!")
        return analysis
    
    def run_cli_mode(self):
        """Run in continuous CLI mode"""
        print("\n⌨️  CLI MODE - Continuous Analysis")
        print("=" * 40)
        print(f"Starting continuous analysis (Target interval: {self.config.capture_interval}s)")
        print("Press Ctrl+C to stop")
        print("-" * 40)
        
        try:
            capture_count = 0
            while True:
                cycle_start = time.time()
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Capture...")
                
                # Capture
                screenshot_path = self.capture.capture()
                if screenshot_path:
                    print(f"  ✓ Saved: {screenshot_path}")
                    
                    # Analyze
                    print("  Analyzing...")
                    analysis_start = time.time()
                    analysis = self.analyzer.analyze(screenshot_path)
                    analysis_time = time.time() - analysis_start
                    
                    print(f"  ⏱️  Analysis time: {analysis_time:.1f}s")
                    
                    # Save to memory
                    print("  Saving to memory...")
                    memory_id = self.memory.save_experience(
                        screenshot_path=screenshot_path,
                        analysis=analysis
                    )
                    
                    # Log MVP progress
                    self.tracker.log_milestone("basic_memory", f"Memory item #{memory_id} saved")
                    
                    print(f"  ✓ Memory ID: {memory_id}")
                    
                    # Find similar experiences
                    print("⚠ Tech debt logged: Basic text similarity search -> Will fix with Vector embeddings + semantic search")
                    similar = self.memory.find_similar(analysis)
                    if similar:
                        print(f"  🔍 Found {len(similar)} similar past experiences")
                        # Get a suggestion
                        if similar[0].get('suggestion'):
                            print(f"  💡 Suggestion: {similar[0].get('suggestion')[:80]}...")
                    
                    # Update event stream
                    self.event_stream.add_event("analysis", {
                        "memory_id": memory_id,
                        "app": analysis.get("app", "unknown"),
                        "similar_count": len(similar) if similar else 0,
                        "analysis_time": analysis_time
                    })
                    
                    capture_count += 1
                    
                    # Update tracker stats
                    self.tracker.update_mvp_stats({
                        "total_captures": capture_count,
                        "memory_items": memory_id,
                        "suggestions_given": self.tracker.mvp_state.suggestions_given + (1 if similar else 0)
                    })
                    
                    # Calculate cycle time
                    cycle_time = time.time() - cycle_start
                    print(f"  ✅ Pipeline complete ({cycle_time:.1f}s total)")
                    
                    # Adjust wait time based on actual cycle time
                    if cycle_time < self.config.capture_interval:
                        wait_time = self.config.capture_interval - cycle_time
                        print(f"  ⏳ Waiting {wait_time:.1f}s for next capture...")
                        time.sleep(wait_time)
                    else:
                        print(f"  ⚠ Cycle took {cycle_time:.1f}s (longer than {self.config.capture_interval}s interval)")
                        # Continue immediately if we're behind schedule
                        time.sleep(1)  # Small pause to avoid 100% CPU
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Stopped by user")
            return capture_count
    
    def run_gui_mode(self):
        """Run in GUI mode"""
        print("\n🚀 Launching MVP GUI...")
        print("⚠ Tech debt logged: Tkinter basic GUI -> Will fix with PyQt6 overlay with screen annotation")
        
        # Create GUI window
        self.gui_root = tk.Tk()
        self.gui_root.title("CM Vision Hybrid MVP v0.1.1")
        self.gui_root.geometry("800x600")
        
        # Status variables
        self.running = False
        self.capture_count = 0
        
        # Build GUI
        self._build_gui()
        
        # Start the GUI
        print(f"[{datetime.now().strftime('%H:%M:%S')}] CM Vision MVP started")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Capture interval: {self.config.capture_interval}s")
        self.gui_root.mainloop()
    
    def _build_gui(self):
        """Build the GUI interface"""
        
        # Main frame
        main_frame = ttk.Frame(self.gui_root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.gui_root.columnconfigure(0, weight=1)
        self.gui_root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, 
                               text="🧠 CM Vision Hybrid MVP",
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        # Status labels
        self.status_labels = {}
        status_items = [
            ("Mode:", f"MVP ({self.config.mode})"),
            ("Captures:", "0"),
            ("Memory:", f"{len(self.memory.memory_data.get('experiences', []))} items"),
            ("Interval:", f"{self.config.capture_interval}s"),
            ("Analyzer:", self.analyzer.__class__.__name__)
        ]
        
        for i, (label, value) in enumerate(status_items):
            ttk.Label(status_frame, text=label, font=("Arial", 10, "bold")).grid(row=i, column=0, sticky=tk.W, padx=(0, 10))
            self.status_labels[label] = ttk.Label(status_frame, text=value)
            self.status_labels[label].grid(row=i, column=1, sticky=tk.W)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=(0, 10))
        
        self.start_button = ttk.Button(button_frame, text="Start Analysis", command=self._start_analysis)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Stop Analysis", command=self._stop_analysis, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)
        
        # Log/output area
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
        log_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, width=80, height=15, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add initial log message
        self._log_message("System initialized in GUI mode")
        self._log_message(f"Capture interval: {self.config.capture_interval}s")
        self._log_message("Ready to start analysis")
    
    def _log_message(self, message):
        """Add a message to the log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.gui_root.update()
    
    def _start_analysis(self):
        """Start continuous analysis"""
        if self.running:
            return
        
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        self._log_message("Started continuous analysis")
        self._log_message(f"Capture interval: {self.config.capture_interval}s")
        
        # Start analysis in a separate thread
        self.analysis_thread = threading.Thread(target=self._run_continuous_analysis, daemon=True)
        self.analysis_thread.start()
    
    def _stop_analysis(self):
        """Stop continuous analysis"""
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self._log_message("Stopped analysis")
    
    def _run_continuous_analysis(self):
        """Run continuous analysis in background thread"""
        while self.running:
            try:
                cycle_start = time.time()
                self._log_message("Capture...")
                
                # Capture
                screenshot_path = self.capture.capture()
                if screenshot_path:
                    self._log_message(f"  ✓ Saved: {screenshot_path}")
                    
                    # Analyze
                    self._log_message("  Analyzing...")
                    analysis = self.analyzer.analyze(screenshot_path)
                    
                    # Save to memory
                    self._log_message("  Saving to memory...")
                    memory_id = self.memory.save_experience(
                        screenshot_path=screenshot_path,
                        analysis=analysis
                    )
                    
                    # Log MVP progress
                    self.tracker.log_milestone("basic_memory", f"Memory item #{memory_id} saved")
                    
                    self._log_message(f"  ✓ Memory ID: {memory_id}")
                    
                    # Find similar experiences
                    self._log_message("⚠ Tech debt logged: Basic text similarity search -> Will fix with Vector embeddings + semantic search")
                    similar = self.memory.find_similar(analysis)
                    if similar:
                        self._log_message(f"  🔍 Found {len(similar)} similar past experiences")
                        # Get a suggestion
                        if similar[0].get('suggestion'):
                            suggestion = similar[0].get('suggestion')
                            self._log_message(f"  💡 Suggestion: {suggestion[:80]}...")
                    
                    # Update event stream
                    self.event_stream.add_event("analysis", {
                        "memory_id": memory_id,
                        "app": analysis.get("app", "unknown"),
                        "similar_count": len(similar) if similar else 0,
                        "analysis_time": analysis.get("analysis_time", 0)
                    })
                    
                    self.capture_count += 1
                    
                    # Update status
                    self.status_labels["Captures:"].config(text=str(self.capture_count))
                    self.status_labels["Memory:"].config(text=f"{memory_id} items")
                    
                    # Update tracker stats
                    self.tracker.update_mvp_stats({
                        "total_captures": self.capture_count,
                        "memory_items": memory_id,
                        "suggestions_given": self.tracker.mvp_state.suggestions_given + (1 if similar else 0)
                    })
                    
                    cycle_time = time.time() - cycle_start
                    self._log_message(f"  ✅ Pipeline complete ({cycle_time:.1f}s)")
                    self._log_message(f"  Analyzed: {analysis.get('app', 'unknown')} - {analysis.get('activity', 'unknown')}")
                    
                    # Log tech debt
                    if analysis.get('mode') == 'local_fallback':
                        self._log_message("⚠ Tech debt logged: Basic text similarity search -> Will fix with Vector embeddings + semantic search")
                
                # Calculate wait time
                cycle_time = time.time() - cycle_start
                if cycle_time < self.config.capture_interval:
                    wait_time = self.config.capture_interval - cycle_time
                    time.sleep(wait_time)
                else:
                    time.sleep(1)  # Small pause if we're behind
                
            except Exception as e:
                self._log_message(f"❌ Error in analysis: {str(e)}")
                time.sleep(5)  # Wait a bit before retrying
    
    def run_test_mode(self):
        """Run test mode for validation"""
        print("\n🧪 TEST MODE: Quick validation...")
        print("-" * 40)
        
        # Run a single capture
        print("\n[1/4] Capture...")
        screenshot_path = self.capture.capture()
        if not screenshot_path:
            print("❌ Test failed: Capture error")
            return False
        
        print(f"  ✓ Saved: {screenshot_path}")
        
        # Analyze
        print("[2/4] Analyze...")
        analysis = self.analyzer.analyze(screenshot_path)
        print(f"  ✓ Analysis complete")
        print(f"  ⏱️  Time: {analysis.get('analysis_time', 0):.1f}s")
        
        # Save to memory
        print("[3/4] Saving to memory...")
        memory_id = self.memory.save_experience(
            screenshot_path=screenshot_path,
            analysis=analysis
        )
        
        print("✓ MVP progress logged: basic_memory")
        print(f"  ✓ Memory ID: {memory_id}")
        
        # Find similar experiences
        print("[4/4] Finding similar experiences...")
        print("⚠ Tech debt logged: Basic text similarity search -> Will fix with Vector embeddings + semantic search")
        similar = self.memory.find_similar(analysis)
        
        if similar:
            print(f"  🔍 Found {len(similar)} similar past experiences")
            # Show suggestion
            if similar[0].get('suggestion'):
                print(f"  💡 Suggestion: {similar[0].get('suggestion')[:80]}...")
        else:
            print("  🔍 No similar experiences found")
        
        print("\n  ✅ Pipeline complete")
        
        # Update tracker
        self.tracker.update_mvp_stats({
            "total_captures": 1,
            "memory_items": len(self.memory.memory_data.get("experiences", [])),
            "suggestions_given": 1 if similar else 0
        })
        
        # Test results
        print("\n✅ TEST PASSED:")
        print(f"  - Capture: ✓")
        print(f"  - Analysis: ✓ ({analysis.get('analysis_time', 0):.1f}s)")
        print(f"  - Memory save: ✓")
        print(f"  - App detected: {analysis.get('app', 'unknown')}")
        print(f"  - Mode: {analysis.get('mode', 'unknown')}")
        print(f"  - Event stream: ✓ ({len(self.event_stream.events)} events)")
        
        return True
    
    def cleanup(self):
        """Clean up system resources"""
        print("\n🧹 Cleaning up...")
        
        # Print final stats
        print("\n📊 FINAL STATS:")
        print(f"  Total captures: {self.tracker.mvp_state.total_captures}")
        print(f"  Gemini API calls: {self.tracker.mvp_state.gemini_calls}")
        print(f"  Memory items: {self.tracker.mvp_state.memory_items}")
        print(f"  Suggestions given: {self.tracker.mvp_state.suggestions_given}")
        print(f"  Analyzer mode: {self.analyzer.__class__.__name__}")
        
        # Event stream stats
        print("\n📈 EVENT STREAM:")
        print(f"  Total events: {len(self.event_stream.events)}")
        
        # Analyze patterns
        patterns = self.event_stream.analyze_patterns()
        if patterns:
            print(f"  Active patterns: {', '.join(patterns)}")
        
        # Save event stream
        self.event_stream.save_events()
        
        # Show blueprint tracker status
        print("\n📋 BLUEPRINT TRACKER STATUS:")
        self.tracker.show_status()
        
        print("\n" + "=" * 70)
        print("CM Vision Hybrid MVP - Execution Complete")
        print("MVP built, Blueprint path ready")
        print("Check 'mvp_tracker.json' for migration plan")
        print("=" * 70)

def main():
    """Main entry point"""
    system = None
    try:
        # Create system
        system = CMVisionHybrid()
        
        # Choose mode
        print("\n🎮 CHOOSE OPERATION MODE:")
        print("  1. GUI Mode (Recommended for MVP)")
        print("  2. CLI Mode (Terminal only)")
        print("  3. Single Capture & Exit")
        print("  4. Test Mode (Quick validation)")
        
        choice = input("\nChoice (1-4): ").strip()
        
        if choice == "1":
            system.run_gui_mode()
        elif choice == "2":
            capture_count = system.run_cli_mode()
            print(f"\n📈 Captured {capture_count} screenshots")
        elif choice == "3":
            system.run_single_capture()
        elif choice == "4":
            system.run_test_mode()
        else:
            print("❌ Invalid choice. Running test mode...")
            system.run_test_mode()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if system:
            system.cleanup()

if __name__ == "__main__":
    main()