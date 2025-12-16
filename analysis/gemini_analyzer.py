import google.generativeai as genai
import json
import time
from io import BytesIO

class MVP_GeminiAnalyzer:
    """
    MVP: Full Gemini integration from Day 1
    This is BLUEPRINT-READY already!
    """
    def __init__(self, config, tracker):
        self.config = config
        self.tracker = tracker
        self.api_calls = 0
        
        # Configure Gemini
        genai.configure(api_key=config.gemini_api_key)
        
        # FIX: Try multiple model names
        self.model = None
        self.model_name = None
        
        # Try different model names
        model_names = ['gemini-1.5-pro', 'gemini-pro', 'gemini-1.5-flash', 'gemini-1.0-pro']
        
        for model_name in model_names:
            try:
                self.model = genai.GenerativeModel(model_name)
                self.model_name = model_name
                print(f"✓ Using model: {model_name}")
                break
            except Exception as e:
                print(f"✗ Model {model_name} failed: {str(e)[:100]}")
                continue
        
        if self.model is None:
            print("⚠ WARNING: No Gemini model available. Using fallback only.")
            print("  Available models:")
            try:
                models = genai.list_models()
                for m in models:
                    if 'generateContent' in m.supported_generation_methods:
                        print(f"    - {m.name}")
            except:
                print("    Could not list models")
        
        print("✓ Gemini analyzer initialized (MVP ready)")
        
        # Log MVP completion
        tracker.log_mvp_completion(
            component="visual_understanding",
            notes=f"Gemini {self.model_name if self.model_name else 'fallback'} with structured JSON output"
        )
    
    def analyze_screen(self, screenshot_image, window_info):
        """Analyze screenshot - MVP and Blueprint ready"""
        # If no model available, return fallback immediately
        if self.model is None:
            return self._fallback_analysis(window_info)
        
        try:
            # MVP prompt - simple but effective
            prompt = """
            Analyze this developer's screen. Return ONLY valid JSON:
            {
                "app_detected": "guess the main application (VS Code, Chrome, Terminal, etc.)",
                "primary_activity": "coding/debugging/reading/browsing/designing/writing",
                "visible_text_summary": "brief summary of text on screen (max 100 characters)",
                "potential_errors": ["list", "of", "possible", "errors", "or", "issues"],
                "confidence_score": 0.95,
                "suggested_context": "web_dev/data_analysis/writing/unknown"
            }
            
            Be concise. Focus on what's actually visible.
            Important: Return ONLY the JSON object, no other text.
            """
            
            # Add window context if available
            if window_info and window_info.get('app') != 'unknown_app':
                prompt = f"Window context: {window_info['app']}\n" + prompt
            
            # Call Gemini
            self.api_calls += 1
            
            # Convert PIL image to bytes for Gemini
            img_byte_arr = BytesIO()
            screenshot_image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            response = self.model.generate_content([
                prompt,
                {"mime_type": "image/png", "data": img_byte_arr}
            ])
            
            # Extract JSON (Gemini sometimes wraps it)
            response_text = response.text.strip()
            
            # Clean up response
            if response_text.startswith("```json"):
                response_text = response_text[7:-3]
            elif response_text.startswith("```"):
                response_text = response_text[3:-3]
            
            # Parse
            analysis = json.loads(response_text)
            
            # Add metadata
            analysis["api_calls"] = self.api_calls
            analysis["mvp_mode"] = True
            analysis["analyzed_at"] = time.time()
            analysis["model_used"] = self.model_name
            
            # MVP: Add simple intent detection
            analysis["mvp_intent"] = self._simple_intent_detection(analysis)
            
            # Add window info for context
            if window_info:
                analysis["window_title"] = window_info.get("title", "Unknown")
            
            print(f"  ✓ Gemini analysis successful")
            print(f"    App: {analysis.get('app_detected')}")
            print(f"    Activity: {analysis.get('primary_activity')}")
            
            return analysis
            
        except json.JSONDecodeError as e:
            print(f"  ⚠ Gemini returned invalid JSON: {str(e)[:100]}")
            print(f"  Raw response: {response_text[:200]}...")
            return self._fallback_analysis(window_info)
        except Exception as e:
            print(f"  ⚠ Gemini error: {str(e)[:100]}")
            return self._fallback_analysis(window_info)
    
    def _fallback_analysis(self, window_info):
        """Better fallback when Gemini fails"""
        # Try to get active window title
        window_title = "Unknown"
        app_name = "Unknown"
        
        if window_info:
            window_title = window_info.get("title", "Unknown")
            app_name = window_info.get("app", "Unknown")
        
        # Try to detect app from window title
        detected_app = self._guess_app_from_window(window_title)
        if detected_app != "Unknown":
            app_name = detected_app
        
        return {
            "app_detected": app_name,
            "primary_activity": "unknown",
            "visible_text_summary": f"Screen analysis failed. Window: {window_title[:50]}...",
            "potential_errors": ["Gemini API unavailable", "Check API key and model name"],
            "confidence_score": 0.1,
            "suggested_context": "unknown",
            "mvp_intent": "unknown",
            "fallback": True,
            "window_context": window_title,
            "model_used": "fallback"
        }
    
    def _guess_app_from_window(self, title):
        """Guess app from window title"""
        if not title or title == "Unknown":
            return "Unknown"
        
        title_lower = title.lower()
        
        app_map = {
            "chrome": "Chrome",
            "firefox": "Firefox",
            "edge": "Edge",
            "vscode": "VS Code",
            "visual studio code": "VS Code",
            "pycharm": "PyCharm",
            "terminal": "Terminal",
            "cmd": "Command Prompt",
            "powershell": "PowerShell",
            "bash": "Terminal",
            "flutterflow": "FlutterFlow",
            "figma": "Figma",
            "notion": "Notion",
            "excel": "Excel",
            "word": "Word",
            "powerpoint": "PowerPoint",
            "slack": "Slack",
            "discord": "Discord",
            "teams": "Teams"
        }
        
        for key, app in app_map.items():
            if key in title_lower:
                return app
        
        # Check for common patterns
        if "google" in title_lower and "chrome" in title_lower:
            return "Chrome"
        elif "microsoft" in title_lower and "edge" in title_lower:
            return "Edge"
        elif "visual studio" in title_lower:
            return "VS Code"
        elif "python" in title_lower:
            return "Python IDE"
        
        return "Unknown"
    
    def _simple_intent_detection(self, analysis):
        """MVP: Simple intent - Blueprint: advanced classifier"""
        activity = analysis.get("primary_activity", "").lower()
        summary = analysis.get("visible_text_summary", "").lower()
        
        if "error" in activity or "debug" in activity or "error" in summary:
            return "debugging"
        elif "code" in activity or "program" in activity or "script" in summary:
            return "coding"
        elif "read" in activity or "article" in summary or "paper" in summary:
            return "reading"
        elif "design" in activity or "ui" in summary or "ux" in summary:
            return "designing"
        elif "write" in activity or "document" in summary:
            return "writing"
        else:
            return "unknown"
    
    def blueprint_upgrade_hooks(self):
        """Future blueprint enhancements"""
        return {
            "upgrades_available": [
                {"name": "Gemini 1.5 Pro", "for": "complex reasoning"},
                {"name": "Vision preprocessing", "for": "better accuracy"},
                {"name": "Multimodal prompts", "for": "richer context"}
            ],
            "current_model": self.model_name or "fallback",
            "cost_per_1k": "~$0.075-$3.50"
        }