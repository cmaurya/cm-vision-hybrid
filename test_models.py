#!/usr/bin/env python3
"""
Quick test to see available Gemini models
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

try:
    import google.generativeai as genai
    
    # Configure
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env file")
        sys.exit(1)
    
    genai.configure(api_key=api_key)
    
    # List models
    print("🔍 Checking available Gemini models...")
    models = genai.list_models()
    
    generation_models = []
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            generation_models.append(model.name)
    
    if generation_models:
        print(f"\n✅ Found {len(generation_models)} models that support generateContent:")
        for model_name in generation_models:
            print(f"   • {model_name}")
        
        # Try to use each model
        print("\n🧪 Testing each model...")
        for model_name in generation_models:
            try:
                model = genai.GenerativeModel(model_name)
                print(f"   ✓ {model_name} - OK")
            except Exception as e:
                print(f"   ✗ {model_name} - Failed: {str(e)[:80]}")
    else:
        print("❌ No models found with generateContent support")
        
except ImportError:
    print("❌ google-generativeai not installed. Run: pip install google-generativeai")
except Exception as e:
    print(f"❌ Error: {e}")