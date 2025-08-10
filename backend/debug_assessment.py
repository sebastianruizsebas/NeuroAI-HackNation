#!/usr/bin/env python3

import sys
import os

# Add the backend directory to sys.path if it's not already there
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from profai_engine import ProfAIEngine

def test_initial_assessment():
    print("=== Testing Initial Assessment Generation ===")
    
    try:
        print("1. Creating ProfAI Engine...")
        engine = ProfAIEngine()
        print("✅ Engine created successfully")
        
        print("2. Testing initial assessment for 'Types of AI Models'...")
        questions = engine.generate_initial_assessment("Types of AI Models")
        
        print(f"✅ Success! Generated {len(questions)} questions")
        
        if questions:
            print("📝 First question preview:")
            print(f"   Question: {questions[0].get('question', 'N/A')}")
            print(f"   Options: {len(questions[0].get('options', []))} choices")
            print(f"   Correct: {questions[0].get('correct', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_initial_assessment()
    sys.exit(0 if success else 1)
