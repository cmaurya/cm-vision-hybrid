class MVP_IntentDetector:
    """
    MVP: Simple rule-based intent detection
    BLUEPRINT: Will be replaced with ML classifier
    """
    def __init__(self):
        self.rules = {
            "debugging": ["error", "fail", "bug", "exception", "traceback"],
            "coding": ["code", "function", "class", "def ", "import"],
            "research": ["article", "paper", "read", "study", "research"],
            "design": ["design", "ui", "ux", "figma", "sketch"],
            "communication": ["email", "chat", "message", "slack", "discord"]
        }
    
    def detect(self, analysis_text, window_app):
        """Simple rule-based intent detection"""
        text_lower = analysis_text.lower()
        app_lower = window_app.lower() if window_app else ""
        
        scores = {}
        
        # Check rules
        for intent, keywords in self.rules.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower or keyword in app_lower:
                    score += 1
            
            scores[intent] = score
        
        # Get best match
        best_intent = max(scores.items(), key=lambda x: x[1])
        
        if best_intent[1] > 0:
            return best_intent[0]
        
        return "unknown"