#!/usr/bin/env python3
"""
Test script to verify enhanced topic title generation
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from profai_engine import ProfAIEngine

def test_enhanced_titles():
    """Test the enhanced title generation for different topics"""
    
    engine = ProfAIEngine()
    
    # Test cases with different user inputs
    test_cases = [
        "I'm interested in learning about Neural Networks",
        "I want to learn machine learning",
        "computer vision for image recognition",
        "natural language processing",
        "reinforcement learning for games",
        "deep learning with PyTorch",
        "data science and analytics",
        "python programming for AI"
    ]
    
    print("Testing Enhanced Title Generation")
    print("=" * 50)
    
    for i, user_input in enumerate(test_cases, 1):
        print(f"\n{i}. User Input: '{user_input}'")
        
        try:
            # Test the fallback title generation first
            fallback_title = engine._generate_fallback_title(user_input)
            print(f"   Fallback Title: {fallback_title}")
            
            # Test full topic generation
            print("   Generating custom topics...")
            topics = engine.generate_custom_topics(f"test_user_{i}", user_input)
            
            if topics:
                for j, topic in enumerate(topics):
                    print(f"   Topic {j+1}: {topic.get('title', 'No title')}")
                    print(f"   Description: {topic.get('description', 'No description')[:100]}...")
            else:
                print("   Using fallback topics...")
                fallback_topics = engine._generate_fallback_topics(user_input, f"test_user_{i}")
                for j, topic in enumerate(fallback_topics):
                    print(f"   Fallback Topic {j+1}: {topic.get('title', 'No title')}")
                    
        except Exception as e:
            print(f"   Error: {e}")
            print("   Testing fallback only...")
            fallback_title = engine._generate_fallback_title(user_input)
            print(f"   Fallback Title: {fallback_title}")
    
    print("\n" + "=" * 50)
    print("Title Enhancement Test Complete!")

if __name__ == "__main__":
    test_enhanced_titles()
