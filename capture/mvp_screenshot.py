import time
from datetime import datetime
import os
from PIL import ImageGrab
import mss
import mss.tools

class MVP_Screenshot:
    """
    MVP: Simple screen capture
    BLUEPRINT UPGRADE PATH: 
    - Add window-specific capture
    - Add event stream integration
    - Add mouse/keyboard tracking
    """
    def __init__(self, config, tracker):
        self.config = config
        self.tracker = tracker
        self.sct = mss.mss()
        self.screenshot_count = 0
        
        # Try to get window info if pygetwindow is available
        self.has_window_info = False
        try:
            import pygetwindow
            self.has_window_info = True
            self.pygetwindow = pygetwindow
        except ImportError:
            print("  ⚠ pygetwindow not installed. Window titles will be limited.")
        
        # Tech debt: Simple capture only
        tracker.add_tech_debt(
            item="Full screen capture only",
            reason="MVP simplicity",
            blueprint_feature="Active window detection + event stream"
        )
    
    def capture(self):
        """Simple MVP capture - full screen only"""
        try:
            # MVP: Simple full screen capture
            screenshot = ImageGrab.grab()
            
            # Save with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.config.screenshots_dir}/mvp_{timestamp}.png"
            
            screenshot.save(filename)
            self.screenshot_count += 1
            
            # Get better window info if possible
            window_info = self._get_window_info()
            window_info.update({
                "timestamp": timestamp,
                "filename": filename,
                "type": "full_screen",  # Blueprint: specific window
                "dimensions": screenshot.size
            })
            
            return {
                "image": screenshot,
                "window_info": window_info,
                "filename": filename
            }
            
        except Exception as e:
            print(f"  ✗ Capture error: {e}")
            return None
    
    def _get_window_info(self):
        """Get window information - improved"""
        window_info = {
            "app": "unknown_app",
            "title": "Unknown",
            "has_pygetwindow": self.has_window_info
        }
        
        if self.has_window_info:
            try:
                active = self.pygetwindow.getActiveWindow()
                if active:
                    window_info["title"] = active.title
                    window_info["app"] = self._extract_app_name(active.title)
                    window_info["position"] = {
                        "left": active.left,
                        "top": active.top,
                        "width": active.width,
                        "height": active.height
                    }
            except Exception as e:
                window_info["error"] = str(e)
        
        return window_info
    
    def _extract_app_name(self, title):
        """Extract app name from window title"""
        if not title:
            return "unknown_app"
        
        title_lower = title.lower()
        
        # Common app detection
        app_patterns = {
            "chrome": ["chrome", "google chrome"],
            "vscode": ["visual studio code", "vscode", "vs code"],
            "pycharm": ["pycharm"],
            "terminal": ["terminal", "cmd", "powershell", "bash", "shell"],
            "flutterflow": ["flutterflow"],
            "figma": ["figma"],
            "notion": ["notion"],
            "slack": ["slack"],
            "discord": ["discord"]
        }
        
        for app_name, patterns in app_patterns.items():
            if any(pattern in title_lower for pattern in patterns):
                return app_name
        
        # Try to extract from title
        words = title.split()
        if words:
            # Take first word, remove special chars
            first_word = words[0].replace("[", "").replace("]", "").replace("-", "")
            return first_word[:20].lower()
        
        return "unknown_app"
    
    def blueprint_upgrade_hook(self):
        """This method will be replaced in blueprint"""
        # Placeholder for blueprint features
        return {
            "needs_upgrade": True,
            "upgrade_to": "Advanced capture with window detection",
            "effort_estimate": "2 days",
            "prerequisites": ["pygetwindow", "psutil"]
        }