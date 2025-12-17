"""
analyzer.py
===========
MVP Analyzer System - IMPROVED VERSION
"""

import os
import json
import time
import re
from typing import Dict, Any

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import google.generativeai as genai
from PIL import Image

class GeminiAnalyzer:
    """Improved Gemini Analyzer with better app detection"""
    
    def __init__(self, model_name="models/gemini-1.5-flash"):
        self.model_name = model_name
        self.api_key = os.environ.get("GEMINI_API_KEY", "demo_key")
        
        if self.api_key == "demo_key" or len(self.api_key) < 20:
            self.available = False
            print("⚠ Using local analyzer (no Gemini API key)")
        else:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(model_name)
                self.available = True
                print(f"✓ Gemini ready: {model_name}")
            except Exception as e:
                print(f"⚠ Gemini init failed: {e}")
                self.available = False
    
    def analyze(self, screenshot_path: str, context: Dict = None) -> Dict[str, Any]:
        """Analyze screenshot with improved prompt and parsing"""
        start_time = time.time()
        
        if not self.available:
            return self._fast_fallback_analysis(screenshot_path, context)
        
        try:
            # Open and resize image for faster processing
            img = Image.open(screenshot_path)
            img.thumbnail((800, 600))  # Smaller image = faster processing
            
            # IMPROVED PROMPT - Forces JSON response
            prompt = """
            Analyze this developer screenshot. Return ONLY valid JSON, no other text.
            
            JSON format:
            {
              "app": "app_name",
              "activity": "activity_description",
              "confidence": 0.0-1.0,
              "error_detected": true/false,
              "suggestion": "brief_suggestion"
            }
            
            App options: vscode, visual_studio, pycharm, chrome, firefox, edge, terminal, 
                        command_prompt, powershell, file_explorer, notepad, word, excel,
                        powerpoint, slack, discord, teams, spotify, unknown
            
            Activity options: coding, debugging, browsing, reading, writing, chatting,
                            presenting, file_management, system_admin, gaming, unknown
            
            Look for: IDE windows, browser tabs, terminal text, error messages, code.
            """
            
            # Generate with stricter config
            response = self.model.generate_content(
                [prompt, img],
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=200,
                    temperature=0.1,
                    response_mime_type="application/json"  # Ask for JSON directly
                )
            )
            
            elapsed = time.time() - start_time
            
            # Parse the response
            analysis = self._parse_gemini_response(response.text, elapsed)
            print(f"✓ Gemini: {analysis.get('app', 'unknown')} - {analysis.get('activity', 'unknown')} ({elapsed:.1f}s)")
            
            return analysis
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"⚠ Gemini analysis error: {e}")
            return self._fallback_with_context(screenshot_path, context, elapsed)
    
    def _parse_gemini_response(self, response_text: str, elapsed_time: float) -> Dict[str, Any]:
        """Parse Gemini response with multiple fallback strategies"""
        
        # Default analysis
        default_analysis = {
            "app": "unknown",
            "activity": "unknown",
            "error_detected": False,
            "suggestion": "Analysis completed",
            "confidence": 0.5,
            "mode": "gemini",
            "analysis_time": elapsed_time
        }
        
        # Try to extract JSON
        json_str = None
        
        # Strategy 1: Look for JSON block
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
        # Strategy 2: Look for curly braces
        elif "{" in response_text and "}" in response_text:
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            json_str = response_text[start:end]
        # Strategy 3: Maybe it's just JSON
        else:
            json_str = response_text.strip()
        
        if json_str:
            try:
                data = json.loads(json_str)
                
                # Map to our expected format
                analysis = {
                    "app": data.get("app", "unknown"),
                    "activity": data.get("activity", "unknown"),
                    "error_detected": data.get("error_detected", False),
                    "suggestion": data.get("suggestion", "No suggestion"),
                    "confidence": data.get("confidence", 0.5),
                    "mode": "gemini_json",
                    "analysis_time": elapsed_time
                }
                
                # Clean up app name
                app = analysis["app"].lower().replace(" ", "_")
                if "visual" in app and "studio" in app:
                    analysis["app"] = "visual_studio"
                elif "vs" in app and "code" in app:
                    analysis["app"] = "vscode"
                elif "command" in app or "cmd" in app:
                    analysis["app"] = "command_prompt"
                elif "power" in app and "shell" in app:
                    analysis["app"] = "powershell"
                
                return analysis
                
            except json.JSONDecodeError:
                print(f"⚠ Failed to parse JSON: {json_str[:50]}...")
        
        # If no JSON, try to extract app from text
        app = self._extract_app_from_text(response_text)
        activity = self._extract_activity_from_text(response_text)
        
        default_analysis.update({
            "app": app,
            "activity": activity,
            "suggestion": response_text[:100] if response_text else "No suggestion",
            "mode": "gemini_text"
        })
        
        return default_analysis
    
    def _extract_app_from_text(self, text: str) -> str:
        """Extract app from text response"""
        text_lower = text.lower()
        
        app_patterns = {
            "vscode": ["vscode", "visual studio code", "code editor", "vs code"],
            "visual_studio": ["visual studio", "visualstudio"],
            "pycharm": ["pycharm", "jetbrains"],
            "chrome": ["chrome", "google chrome", "browser"],
            "firefox": ["firefox", "mozilla"],
            "edge": ["edge", "microsoft edge"],
            "terminal": ["terminal", "linux terminal", "mac terminal"],
            "command_prompt": ["command prompt", "cmd.exe", "cmd window"],
            "powershell": ["powershell", "ps1", "ps "],
            "file_explorer": ["file explorer", "windows explorer", "folder"],
            "notepad": ["notepad", "text editor"],
            "word": ["word", "microsoft word"],
            "excel": ["excel", "spreadsheet"],
            "slack": ["slack"],
            "discord": ["discord"],
            "spotify": ["spotify", "music"]
        }
        
        for app, patterns in app_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return app
        
        return "unknown"
    
    def _extract_activity_from_text(self, text: str) -> str:
        """Extract activity from text response"""
        text_lower = text.lower()
        
        activity_patterns = {
            "coding": ["coding", "programming", "writing code", "developing"],
            "debugging": ["debugging", "fixing error", "troubleshooting"],
            "browsing": ["browsing", "reading", "searching", "web"],
            "reading": ["reading", "viewing", "looking at"],
            "writing": ["writing", "typing", "documenting"],
            "chatting": ["chatting", "messaging", "communicating"],
            "presenting": ["presenting", "presentation", "slides"],
            "file_management": ["files", "folders", "organizing", "managing"],
            "system_admin": ["system", "admin", "configuring", "settings"]
        }
        
        for activity, patterns in activity_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return activity
        
        return "unknown"
    
    def _fallback_with_context(self, screenshot_path: str, context: Dict, elapsed: float) -> Dict[str, Any]:
        """Fallback analysis using filename and context"""
        filename = os.path.basename(screenshot_path)
        
        # Try to guess from window title if available
        app = "unknown"
        activity = "unknown"
        
        if context and "window_title" in context:
            title = context["window_title"].lower()
            if any(x in title for x in ["visual studio", "vscode"]):
                app = "vscode"
                activity = "coding"
            elif any(x in title for x in ["chrome", "firefox", "edge", "browser"]):
                app = "chrome"
                activity = "browsing"
            elif any(x in title for x in ["terminal", "cmd", "powershell"]):
                app = "command_prompt"
                activity = "system_admin"
            elif "explorer" in title:
                app = "file_explorer"
                activity = "file_management"
        
        return {
            "app": app,
            "activity": activity,
            "error_detected": False,
            "suggestion": "Context-based analysis",
            "confidence": 0.3,
            "mode": "context_fallback",
            "analysis_time": elapsed
        }
    
    def _fast_fallback_analysis(self, screenshot_path: str, context: Dict = None) -> Dict[str, Any]:
        """Very fast local fallback"""
        return {
            "app": "unknown",
            "activity": "unknown",
            "error_detected": False,
            "suggestion": "Fast local mode - no Gemini",
            "confidence": 0.1,
            "mode": "fast_local",
            "analysis_time": 0.1
        }
    
    def detect_app_from_screenshot(self, screenshot_path: str) -> str:
        """Quick app detection"""
        analysis = self.analyze(screenshot_path)
        return analysis.get("app", "unknown")