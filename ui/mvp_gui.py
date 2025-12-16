import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
from datetime import datetime
from PIL import Image, ImageTk
import os

class MVP_GUI:
    """
    MVP: Simple Tkinter GUI
    BLUEPRINT UPGRADE: PyQt6 overlay
    """
    def __init__(self, cm_system):
        self.system = cm_system
        self.is_running = False
        self.thread = None
        self.last_result = None
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("CM Vision MVP v0.1 - Cognitive Extension")
        self.root.geometry("900x650")
        
        # Style
        self.root.configure(bg="#f0f0f0")
        
        self._create_widgets()
        
        # Tech debt: Basic GUI
        self.system.tracker.add_tech_debt(
            item="Tkinter basic GUI",
            reason="MVP quick implementation",
            blueprint_feature="PyQt6 overlay with screen annotation"
        )
    
    def _create_widgets(self):
        # Header
        header = tk.Frame(self.root, bg="#2c3e50", height=70)
        header.pack(fill="x")
        
        tk.Label(header, text="🧠 CM Vision MVP - Cognitive Extension", 
                font=("Arial", 18, "bold"), 
                fg="white", bg="#2c3e50").pack(side="left", padx=20, pady=15)
        
        # Status label
        self.status_var = tk.StringVar(value="🟢 Ready - MVP Mode")
        tk.Label(header, textvariable=self.status_var,
                font=("Arial", 10), 
                fg="white", bg="#2c3e50").pack(side="right", padx=20)
        
        # Main content - using PanedWindow for resizable panels
        main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg="#f0f0f0")
        main_paned.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left panel - Controls & Info
        left_frame = tk.Frame(main_paned, bg="white", relief=tk.RAISED, borderwidth=1)
        main_paned.add(left_frame, width=300)
        
        # Controls section
        control_frame = tk.LabelFrame(left_frame, text="🎮 Controls", 
                                     font=("Arial", 12, "bold"),
                                     bg="white", padx=10, pady=10)
        control_frame.pack(fill="x", padx=5, pady=5)
        
        # Buttons
        self.start_btn = tk.Button(control_frame, text="▶ Start Continuous Analysis", 
                                  command=self.start_analysis,
                                  bg="#27ae60", fg="white",
                                  font=("Arial", 11), width=20, height=2)
        self.start_btn.pack(pady=5)
        
        self.stop_btn = tk.Button(control_frame, text="⏸ Stop Analysis", 
                                 command=self.stop_analysis,
                                 bg="#e74c3c", fg="white",
                                 font=("Arial", 11), width=20, height=2,
                                 state="disabled")
        self.stop_btn.pack(pady=5)
        
        tk.Button(control_frame, text="📸 Single Capture", 
                 command=self.single_capture,
                 bg="#3498db", fg="white",
                 font=("Arial", 11), width=20, height=2).pack(pady=5)
        
        tk.Button(control_frame, text="📊 Blueprint Tracker", 
                 command=self.show_tracker,
                 bg="#9b59b6", fg="white",
                 font=("Arial", 11), width=20, height=2).pack(pady=5)
        
        tk.Button(control_frame, text="🔄 Update Display", 
                 command=self.update_display,
                 bg="#f39c12", fg="white",
                 font=("Arial", 11), width=20, height=2).pack(pady=5)
        
        # Stats display
        stats_frame = tk.LabelFrame(left_frame, text="📈 Live Stats", 
                                   font=("Arial", 12, "bold"),
                                   bg="white", padx=10, pady=10)
        stats_frame.pack(fill="x", padx=5, pady=10)
        
        self.stats_text = tk.Text(stats_frame, height=8, width=30,
                                 font=("Consolas", 9), bg="#f8f9fa")
        self.stats_text.pack(fill="both", expand=True)
        
        # Right panel - Analysis output
        right_frame = tk.Frame(main_paned, bg="#f0f0f0")
        main_paned.add(right_frame)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Tab 1: Current Analysis
        analysis_tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(analysis_tab, text="🔍 Current Analysis")
        
        # Analysis header
        analysis_header = tk.Frame(analysis_tab, bg="#ecf0f1", height=40)
        analysis_header.pack(fill="x")
        
        self.analysis_title = tk.Label(analysis_header, text="No analysis yet", 
                                      font=("Arial", 12, "bold"), bg="#ecf0f1")
        self.analysis_title.pack(side="left", padx=10, pady=5)
        
        # Analysis content
        analysis_content = tk.Frame(analysis_tab, bg="white")
        analysis_content.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Analysis text with scroll
        self.analysis_text = scrolledtext.ScrolledText(analysis_content, height=15,
                                                      font=("Consolas", 10),
                                                      wrap=tk.WORD, bg="#f8f9fa")
        self.analysis_text.pack(fill="both", expand=True)
        
        # Tab 2: Similar Past Experiences
        memory_tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(memory_tab, text="💾 Similar Past Experiences")
        
        self.memory_text = scrolledtext.ScrolledText(memory_tab, height=15,
                                                    font=("Consolas", 9),
                                                    wrap=tk.WORD, bg="#f8f9fa")
        self.memory_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Tab 3: Logs
        log_tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(log_tab, text="📋 System Logs")
        
        self.log_text = scrolledtext.ScrolledText(log_tab, height=15,
                                                 font=("Consolas", 9),
                                                 wrap=tk.WORD, bg="#f8f9fa")
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Footer
        footer = tk.Frame(self.root, bg="#34495e", height=40)
        footer.pack(fill="x", side="bottom")
        
        self.footer_label = tk.Label(footer, 
                                    text="MVP Mode: Basic functionality | Press F1 for help", 
                                    font=("Arial", 9), fg="white", bg="#34495e")
        self.footer_label.pack(pady=10)
        
        # Bind F1 for help
        self.root.bind('<F1>', lambda e: self.show_help())
    
    def start_analysis(self):
        """Start continuous analysis"""
        if not self.is_running:
            self.is_running = True
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.status_var.set("🔴 Analyzing every 10s...")
            
            # Start thread
            self.thread = threading.Thread(target=self._analysis_loop, daemon=True)
            self.thread.start()
            
            self.log("Started continuous analysis")
            self.log(f"Capture interval: {self.system.config.capture_interval}s")
    
    def stop_analysis(self):
        """Stop analysis"""
        self.is_running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_var.set("🟢 Ready - MVP Mode")
        
        self.log("Stopped analysis")
    
    def single_capture(self):
        """Single capture and analysis"""
        self.log("Single capture triggered")
        self.status_var.set("⏳ Analyzing screenshot...")
        
        # Run in thread
        thread = threading.Thread(target=self._perform_capture, daemon=True)
        thread.start()
    
    def _analysis_loop(self):
        """Continuous analysis loop"""
        interval = self.system.config.capture_interval
        
        while self.is_running:
            try:
                self._perform_capture()
                
                # Wait for next capture
                for _ in range(interval * 10):
                    if not self.is_running:
                        break
                    time.sleep(0.1)
                    
            except Exception as e:
                self.log(f"Error in analysis loop: {e}")
                time.sleep(interval)
    
    def _perform_capture(self):
        """Perform a single capture cycle"""
        try:
            # Use the system to capture and analyze
            result = self.system.capture_and_analyze()
            
            if result:
                self.last_result = result
                # Update UI in main thread
                self.root.after(0, self._update_display, result)
                app = result['analysis'].get('app_detected', 'Unknown')
                self.root.after(0, lambda: self.status_var.set(f"✅ {app}"))
            else:
                self.root.after(0, lambda: self.status_var.set("❌ Capture failed"))
                
        except Exception as e:
            self.root.after(0, lambda: self.log(f"Capture error: {e}"))
            self.root.after(0, lambda: self.status_var.set("⚠ Error occurred"))
    
    def _update_display(self, result):
        """Update all displays with new result"""
        analysis = result.get("analysis", {})
        
        # Update analysis title
        app = analysis.get('app_detected', 'Unknown')
        activity = analysis.get('primary_activity', 'unknown')
        confidence = analysis.get('confidence_score', 0) * 100
        
        self.analysis_title.config(
            text=f"{app} - {activity} ({confidence:.1f}% confidence)"
        )
        
        # Color code based on confidence
        if confidence > 70:
            self.analysis_title.config(fg="#27ae60")  # Green
        elif confidence > 30:
            self.analysis_title.config(fg="#f39c12")  # Orange
        else:
            self.analysis_title.config(fg="#e74c3c")  # Red
        
        # Update analysis text
        self.analysis_text.delete(1.0, tk.END)
        
        display = f"""=== SCREEN ANALYSIS ===
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Model: {analysis.get('model_used', 'unknown')}

📱 APPLICATION: {app}
🎯 ACTIVITY: {activity}
📊 CONFIDENCE: {confidence:.1f}%
🏷️ CONTEXT: {analysis.get('suggested_context', 'unknown')}
🎪 INTENT: {analysis.get('mvp_intent', 'unknown')}

📝 TEXT SUMMARY:
{analysis.get('visible_text_summary', 'No text detected')}

{'⚠️ POTENTIAL ISSUES:' if analysis.get('potential_errors') else '✅ NO ISSUES DETECTED:'}
"""
        
        errors = analysis.get('potential_errors', [])
        if errors:
            for i, error in enumerate(errors, 1):
                display += f"  {i}. {error}\n"
        else:
            display += "  None detected\n"
        
        if analysis.get('window_context'):
            display += f"\n🪟 WINDOW: {analysis.get('window_context', 'Unknown')}"
        
        if analysis.get('fallback'):
            display += "\n\n⚠️ FALLBACK MODE: Gemini analysis failed. Using basic detection."
        
        self.analysis_text.insert(1.0, display)
        
        # Update log
        self.log(f"Analyzed: {app} - {activity}")
        
        # Update memory display
        self._update_memory_display(analysis)
        
        # Update stats
        self._update_stats()
    
    def _update_memory_display(self, current_analysis):
        """Update memory tab with similar experiences"""
        similar = self.system.memory.find_similar(current_analysis, limit=5)
        
        self.memory_text.delete(1.0, tk.END)
        
        if not similar:
            self.memory_text.insert(1.0, "No similar past experiences found.")
            return
        
        memory_display = f"""=== SIMILAR PAST EXPERIENCES ===
Found {len(similar)} similar past experiences

"""
        
        for i, item in enumerate(similar, 1):
            exp = item["experience"]
            score = item["score"]
            reason = item.get("reason", "")
            
            memory_display += f"""\n--- Experience #{i} (Score: {score:.2f}) ---
Time: {exp['timestamp'][11:19] if len(exp['timestamp']) > 10 else exp['timestamp']}
App: {exp['app']}
Activity: {exp['activity']}
Confidence: {exp.get('confidence', 0)*100:.1f}%

Summary: {exp.get('analysis_summary', 'No summary')[:100]}...

Issues: {', '.join(exp.get('errors', ['None']))[:80]}

Match reason: {reason}
"""
        
        self.memory_text.insert(1.0, memory_display)
    
    def _update_stats(self):
        """Update statistics display"""
        stats = self.system.get_stats()
        
        stats_text = f"""=== SYSTEM STATISTICS ===

📊 CAPTURE STATS:
  Total Captures: {stats.get('captures', 0)}
  Gemini API Calls: {stats.get('gemini_calls', 0)}
  Memory Items: {stats.get('memory_items', 0)}

⏱️ PERFORMANCE:
  Uptime: {stats.get('uptime', 0):.0f}s
  Mode: {stats.get('mode', 'MVP')}

💾 MEMORY:
  File: memory/mvp_memory.json
  Status: {'Active' if stats.get('memory_items', 0) > 0 else 'Empty'}

🔧 SYSTEM:
  MVP Mode: {'Yes' if stats.get('mvp_mode', True) else 'No'}
  Version: 0.1.0
"""
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)
    
    def log(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        
        # Also print to console for debugging
        print(f"[{timestamp}] {message}")
    
    def show_tracker(self):
        """Show blueprint tracker status"""
        tracker_status = self.system.tracker.show_status()
        
        # Create popup
        popup = tk.Toplevel(self.root)
        popup.title("Blueprint Tracker - MVP → Vision Migration")
        popup.geometry("700x500")
        
        text = scrolledtext.ScrolledText(popup, wrap=tk.WORD, font=("Consolas", 9))
        text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Load tracker data
        try:
            with open("mvp_tracker.json", "r") as f:
                tracker_data = f.read()
                text.insert(1.0, tracker_data)
        except:
            text.insert(1.0, "Could not load tracker file. Check mvp_tracker.json")
    
    def show_help(self):
        """Show help window"""
        help_text = """=== CM VISION MVP HELP ===

QUICK START:
1. Click 'Single Capture' to test analysis
2. Click 'Start Continuous Analysis' for automatic capture every 10s
3. Check tabs for analysis results and similar past experiences

TABS:
🔍 Current Analysis - Latest screen analysis from Gemini
💾 Similar Past Experiences - Past experiences similar to current
📋 System Logs - All system activities

KEY FEATURES:
- Screen capture and analysis
- Simple memory system (JSON file)
- Similarity search in past experiences
- Blueprint tracker for future upgrades

NEXT STEPS:
1. Fix Gemini model in analysis/gemini_analyzer.py
2. Add proactive suggestions
3. Add FlutterFlow-specific help
4. Upgrade to blueprint features

Press F1 to close this help.
"""
        
        help_window = tk.Toplevel(self.root)
        help_window.title("CM Vision MVP Help")
        help_window.geometry("600x400")
        
        text = scrolledtext.ScrolledText(help_window, wrap=tk.WORD)
        text.pack(fill="both", expand=True, padx=10, pady=10)
        text.insert(1.0, help_text)
        
        tk.Button(help_window, text="Close", command=help_window.destroy,
                 bg="#3498db", fg="white").pack(pady=10)
    
    def update_display(self):
        """Manual update of display"""
        if self.last_result:
            self._update_display(self.last_result)
            self.log("Display manually updated")
        else:
            self.log("No analysis to display yet")
    
    def run(self):
        """Start the GUI"""
        # Initial updates
        self._update_stats()
        self.log("CM Vision MVP started")
        self.log(f"Capture interval: {self.system.config.capture_interval}s")
        
        # Start GUI
        self.root.mainloop()