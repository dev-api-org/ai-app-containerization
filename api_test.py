#!/usr/bin/env python3
"""
Simple API test script to verify Gemini API connection.
This tests the API independently before integrating into the main app.
"""

import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

# Fix Windows console encoding issues
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

def test_api_connection():
    """Test basic Gemini API connectivity and model response."""
    
    print("=" * 60)
    print("GEMINI API CONNECTION TEST")
    print("=" * 60)
    
    # Step 1: Check API key
    print("\n[1/4] Checking API key...")
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY not found in .env file")
        return False
    
    print(f"✅ API key found (length: {len(api_key)} characters)")
    
    # Step 2: Configure API
    print("\n[2/4] Configuring Gemini API...")
    try:
        genai.configure(api_key=api_key)
        print("✅ API configured successfully")
    except Exception as e:
        print(f"❌ ERROR configuring API: {e}")
        return False
    
    # Step 3: List available models (optional but helpful)
    print("\n[3/4] Listing available models...")
    try:
        models = genai.list_models()
        print("✅ Available models:")
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                print(f"   - {model.name}")
    except Exception as e:
        print(f"⚠️  Could not list models: {e}")
    
    # Step 4: Test different models
    print("\n[4/4] Testing model responses...")
    
    # Try multiple models in order of preference
    models_to_test = [
        "gemini-2.5-flash",          # Latest stable flash model
        "gemini-2.0-flash",          # Stable 2.0 version
        "gemini-flash-latest",       # Auto-updates to latest
        "gemini-2.5-flash-lite",     # Lighter, faster alternative
    ]
    
    test_prompt = "Say 'Hello! API connection successful.' in one sentence."
    
    for model_name in models_to_test:
        print(f"\n   Testing: {model_name}")
        print("   " + "-" * 55)
        
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config={
                    "temperature": 0.4,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 100,
                }
            )
            
            response = model.generate_content(test_prompt)
            response_text = response.text.strip()
            
            print(f"   ✅ SUCCESS!")
            print(f"   📝 Response: {response_text}")
            print(f"\n   ⭐ RECOMMENDED MODEL: {model_name}")
            
            return True
            
        except Exception as e:
            error_msg = str(e)
            
            # Check for specific error types
            if "429" in error_msg or "quota" in error_msg.lower():
                print(f"   ⚠️  QUOTA EXCEEDED: This model has hit rate limits")
                print(f"      Error: {error_msg[:150]}...")
            elif "404" in error_msg or "not found" in error_msg.lower():
                print(f"   ⚠️  MODEL NOT AVAILABLE: {model_name}")
            else:
                print(f"   ❌ ERROR: {error_msg[:150]}...")
            
            continue
    
    # If we get here, all models failed
    print("\n" + "=" * 60)
    print("❌ ALL MODELS FAILED")
    print("=" * 60)
    print("\n📋 Troubleshooting steps:")
    print("   1. Check if you've exceeded your API quota")
    print("   2. Visit: https://aistudio.google.com/app/apikey")
    print("   3. Check your usage: https://ai.dev/usage?tab=rate-limit")
    print("   4. Wait for quota reset (usually 24 hours)")
    print("   5. Consider upgrading your API plan if needed")
    
    return False


def main():
    """Main entry point."""
    success = test_api_connection()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ API TEST PASSED")
        print("=" * 60)
        print("\n💡 You can now use the recommended model in app.py")
    else:
        print("❌ API TEST FAILED")
        print("=" * 60)
        print("\n⚠️  Fix the errors above before running app.py")
    print()


if __name__ == "__main__":
    main()
