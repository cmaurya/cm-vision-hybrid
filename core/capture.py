"""
capture.py
==========
MVP Screen Capture System
Phase 1.4: Enhanced with window context
"""

import os
import json
import time
from datetime import datetime
from PIL import ImageGrab
import pyautogui

class MVPCapture:
    """MVP Screen Capture with window context"""
    
    def __init__(self, screenshot_dir="screenshots"):
        self.screenshot_dir = screenshot_dir
        os.makedirs(screenshot_dir, exist_ok=True)
        
    def capture(self, filename_prefix="mvp"):
        """Capture screenshot - basic method"""
        try:
            # Take screenshot using ImageGrab (faster)
            screenshot = ImageGrab.grab()
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_prefix}_{timestamp}.png"
            filepath = os.path.join(self.screenshot_dir, filename)
            
            # Save screenshot
            screenshot.save(filepath)
            
            return filepath
            
        except Exception as e:
            print(f"⚠ Capture error (ImageGrab): {e}")
            # Fallback to pyautogui
            try:
                screenshot = pyautogui.screenshot()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{filename_prefix}_{timestamp}_fallback.png"
                filepath = os.path.join(self.screenshot_dir, filename)
                screenshot.save(filepath)
                return filepath
            except Exception as e2:
                print(f"❌ Fallback capture also failed: {e2}")
                return None
    
    def capture_with_context(self, filename_prefix="mvp"):
        """Capture screenshot with window context information"""
        screenshot_path = self.capture(filename_prefix)
        
        if not screenshot_path:
            return None, None
        
        # Try to get window context
        context = self._get_window_context()
        
        # Save context if available
        if context:
            context_file = screenshot_path.replace('.png', '_context.json')
            context_data = {
                "timestamp": datetime.now().isoformat(),
                "screenshot": screenshot_path,
                "context": context
            }
            
            try:
                with open(context_file, 'w') as f:
                    json.dump(context_data, f, indent=2)
            except Exception as e:
                print(f"⚠ Failed to save context: {e}")
        
        return screenshot_path, context
    
    def _get_window_context(self):
        """Get active window context if available"""
        context = {}
        
        try:
            # Try to import pygetwindow
            import pygetwindow as gw
            
            # Get active window
            active_window = gw.getActiveWindow()
            
            if active_window:
                context = {
                    "window_title": active_window.title,
                    "window_left": active_window.left,
                    "window_top": active_window.top,
                    "window_width": active_window.width,
                    "window_height": active_window.height,
                    "is_maximized": active_window.isMaximized,
                    "is_minimized": active_window.isMinimized
                }
                
                # Clean up window title
                if context["window_title"]:
                    # Remove common suffixes
                    title = context["window_title"]
                    if " - " in title:
                        context["window_short_title"] = title.split(" - ")[-1]
                    else:
                        context["window_short_title"] = title
                    
                    print(f"  📊 Window: {context['window_short_title'][:30]}...")
                
        except ImportError:
            print("  ⚠ pygetwindow not installed, window context unavailable")
            print("  💡 Run: pip install pygetwindow")
        except Exception as e:
            print(f"  ⚠ Window context error: {e}")
        
        return context if context else None
    
    def capture_active_window(self, filename_prefix="window"):
        """Capture only the active window (more precise)"""
        try:
            # Try to capture specific window
            import pygetwindow as gw
            import pyautogui
            
            active_window = gw.getActiveWindow()
            
            if not active_window:
                print("  ⚠ No active window found, using full screen")
                return self.capture(filename_prefix)
            
            # Get window coordinates
            left = active_window.left
            top = active_window.top
            width = active_window.width
            height = active_window.height
            
            # Capture window region
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            window_name = "".join(c for c in active_window.title[:20] if c.isalnum() or c in (' ', '-', '_'))
            filename = f"{filename_prefix}_{window_name}_{timestamp}.png"
            filepath = os.path.join(self.screenshot_dir, filename)
            
            # Save screenshot
            screenshot.save(filepath)
            
            # Create context
            context = {
                "window_title": active_window.title,
                "window_left": left,
                "window_top": top,
                "window_width": width,
                "window_height": height,
                "capture_type": "active_window"
            }
            
            print(f"  📊 Captured window: {active_window.title[:30]}...")
            
            return filepath, context
            
        except ImportError:
            print("  ⚠ pygetwindow not installed, falling back to full screen")
            return self.capture(filename_prefix), None
        except Exception as e:
            print(f"  ⚠ Active window capture failed: {e}")
            return self.capture(filename_prefix), None
    
    def capture_multiple(self, count=3, interval=2, filename_prefix="multi"):
        """Capture multiple screenshots with interval"""
        screenshots = []
        
        print(f"📸 Capturing {count} screenshots with {interval}s interval...")
        
        for i in range(count):
            print(f"  Capture {i+1}/{count}...")
            
            screenshot_path = self.capture(f"{filename_prefix}_{i+1}")
            
            if screenshot_path:
                screenshots.append(screenshot_path)
                print(f"    ✓ Saved: {os.path.basename(screenshot_path)}")
            
            # Wait for next capture (except after last one)
            if i < count - 1:
                time.sleep(interval)
        
        return screenshots
    
    def get_screenshot_stats(self):
        """Get statistics about saved screenshots"""
        if not os.path.exists(self.screenshot_dir):
            return {"total": 0, "latest": None, "size_mb": 0}
        
        screenshots = []
        total_size = 0
        
        for filename in os.listdir(self.screenshot_dir):
            if filename.endswith('.png'):
                filepath = os.path.join(self.screenshot_dir, filename)
                file_size = os.path.getsize(filepath)
                modified_time = os.path.getmtime(filepath)
                
                screenshots.append({
                    "filename": filename,
                    "path": filepath,
                    "size_bytes": file_size,
                    "modified": datetime.fromtimestamp(modified_time).isoformat()
                })
                
                total_size += file_size
        
        # Sort by modification time (newest first)
        screenshots.sort(key=lambda x: x["modified"], reverse=True)
        
        return {
            "total": len(screenshots),
            "latest": screenshots[0]["filename"] if screenshots else None,
            "size_mb": total_size / (1024 * 1024),
            "screenshots": screenshots[:5]  # Latest 5
        }