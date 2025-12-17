"""
config.py
=========
MVP Configuration
"""

import json
import os
from dataclasses import dataclass, field
from typing import List

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

@dataclass
class MVPConfig:
    """MVP Configuration"""
    mode: str = "MVP"
    version: str = "0.1.1"
    capture_interval: int = 10
    screenshot_dir: str = "screenshots"
    memory_file: str = "memory/mvp_memory.json"
    event_stream_file: str = "memory/event_stream.json"
    plugins: List[str] = field(default_factory=lambda: ["flutterflow"])
    gemini_model: str = "models/gemini-2.5-flash"
    config_path: str = "config/mvp_config.json"
    
    def __post_init__(self):
        """Load from config file if it exists"""
        # First check .env file for settings
        env_mode = os.environ.get("MVP_MODE")
        if env_mode:
            self.mode = env_mode
        
        env_interval = os.environ.get("CAPTURE_INTERVAL")
        if env_interval:
            try:
                self.capture_interval = int(env_interval)
            except ValueError:
                pass
        
        if os.path.exists(self.config_path):
            self._load_from_file()
        else:
            self._create_default_config()
    
    def _load_from_file(self):
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)
                self.mode = data.get("mode", self.mode)
                self.version = data.get("version", self.version)
                self.capture_interval = data.get("capture_interval", self.capture_interval)
                self.screenshot_dir = data.get("screenshot_dir", self.screenshot_dir)
                self.memory_file = data.get("memory_file", self.memory_file)
                self.event_stream_file = data.get("event_stream_file", self.event_stream_file)
                self.plugins = data.get("plugins", self.plugins)
                self.gemini_model = data.get("gemini_model", self.gemini_model)
        except Exception as e:
            print(f"⚠ Config load error: {e}, using defaults")
    
    def _create_default_config(self):
        """Create default configuration file"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        default_config = {
            "mode": self.mode,
            "version": self.version,
            "capture_interval": self.capture_interval,
            "screenshot_dir": self.screenshot_dir,
            "memory_file": self.memory_file,
            "event_stream_file": self.event_stream_file,
            "plugins": self.plugins,
            "gemini_model": self.gemini_model
        }
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        print(f"✓ Created default config at {self.config_path}")