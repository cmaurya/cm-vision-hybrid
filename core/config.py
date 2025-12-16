import os
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Optional

load_dotenv()

@dataclass
class MVPConfig:
    """MVP Configuration - Simple but blueprint-compatible"""
    # Gemini
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    
    # Operation Mode
    is_mvp: bool = os.getenv("MVP_MODE", "true").lower() == "true"
    
    # Capture
    capture_interval: int = int(os.getenv("CAPTURE_INTERVAL", 10))
    screenshots_dir: str = "screenshots"
    max_screenshots: int = 100  # MVP: Keep limited
    
    # Memory (MVP simple, blueprint future)
    memory_file: str = "memory/mvp_memory.json"
    use_vector_db: bool = False  # Blueprint: True
    use_graph_db: bool = False   # Blueprint: True
    
    # UI
    enable_overlay: bool = False  # Blueprint: True
    gui_type: str = "tkinter"     # Blueprint: "pyqt6"
    
    # Plugins
    enabled_plugins: list = None
    
    def __post_init__(self):
        if self.enabled_plugins is None:
            self.enabled_plugins = ["flutterflow"]  # MVP: Only FlutterFlow
        
        # Validate
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required in .env file")
        
        # Create directories
        os.makedirs(self.screenshots_dir, exist_ok=True)
        os.makedirs("memory", exist_ok=True)
        os.makedirs("plugins/flutterflow", exist_ok=True)
    
    def blueprint_features(self):
        """Return list of blueprint features not in MVP"""
        return {
            "vector_database": not self.use_vector_db,
            "graph_database": not self.use_graph_db,
            "advanced_overlay": not self.enable_overlay,
            "plugin_system": True,  # MVP has hardcoded plugins
            "telemetry": False,
            "proactive_engine": False,  # MVP is reactive
            "cross_domain": False,      # MVP is FlutterFlow only
        }