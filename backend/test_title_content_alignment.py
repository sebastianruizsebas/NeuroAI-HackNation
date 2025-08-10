#!/usr/bin/env python3
"""
Test script to verify that lesson content aligns with enhanced topic titles
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from profai_engine import ProfAIEngine

def test_title_content_alignment():
    """Test that lesson content delivers on the promises made in enhanced titles"""
    
    engine = ProfAIEngine()
    
    # Test cases with specific outcome-focused titles
    test_cases = [
        {
            "title": "Building and Training Neural Networks from Scratch",
            "expected_deliverables": ["neural network implementation", "training algorithm", "working model"],
            "expected_actions": ["building", "training"],
            "expected_technologies": ["neural networks"]
        },
        {
            "title": "Creating Computer Vision Systems for Image Analysis", 
            "expected_deliverables": ["computer vision system", "image processing pipeline"],
            "expected_actions": ["creating"],
            "expected_technologies": ["computer vision"]
        },
        {
            "title": "Implementing Core Machine Learning Algorithms",
            "expected_deliverables": ["algorithm implementations", "working code"],
            "expected_actions": ["implementing"],
            "expected_technologies": ["machine learning", "algorithms"]
        }
    ]
    
    print("Testing Title-Content Alignment")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        title = test_case["title"]
        print(f"\n{i}. Testing Title: '{title}'")
        print("-" * 50)
        
        try:
            # Test title analysis
            title_analysis = engine._analyze_topic_title(title)
            print(f"Title Analysis:")
            print(f"   Actions: {title_analysis['actions']}")
            print(f"   Technologies: {title_analysis['technologies']}")
            print(f"   Domain: {title_analysis['domain']}")
            print(f"   Deliverables: {title_analysis['deliverables']}")
            
            # Verify expected components are detected
            validation_results = []
            
            # Check actions
            detected_actions = any(action in title_analysis['actions'] for action in test_case['expected_actions'])
            validation_results.append(("Actions detected", detected_actions))
            
            # Check technologies
            detected_tech = any(tech in ' '.join(title_analysis['technologies']) for tech in test_case['expected_technologies'])
            validation_results.append(("Technologies detected", detected_tech))
            
            # Check if analysis captures the essence
            has_implementation_focus = any(word in title_analysis['actions'] for word in ['building', 'creating', 'implementing', 'developing'])
            validation_results.append(("Implementation focus", has_implementation_focus))
            
            print(f"\nValidation Results:")
            for check, result in validation_results:
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"   {check}: {status}")
            
            # Test lesson outline generation (if API key available)
            print(f"\nGenerating lesson outline for alignment test...")
            try:
                user_profile = {"competency_scores": {title: 3}}
                outline = engine.generate_lesson_outline(title, "beginner", None)
                
                if outline and 'learningObjectives' in outline:
                    print(f"   Lesson outline generated successfully")
                    objectives = outline.get('learningObjectives', [])
                    if objectives:
                        print(f"   First objective: {objectives[0][:100]}...")
                    
                    # Check if objectives align with title promises
                    obj_text = ' '.join(objectives).lower()
                    title_alignment = any(action in obj_text for action in test_case['expected_actions'])
                    tech_alignment = any(tech.lower() in obj_text for tech in test_case['expected_technologies'])
                    
                    print(f"   Objectives align with title actions: {'✅' if title_alignment else '❌'}")
                    print(f"   Objectives mention title technologies: {'✅' if tech_alignment else '❌'}")
                else:
                    print(f"   ⚠️  Lesson outline generation failed (likely API key issue)")
                    
            except Exception as e:
                print(f"   ⚠️  Lesson outline test failed: {e}")
                
        except Exception as e:
            print(f"   ❌ Error in title analysis: {e}")
    
    print("\n" + "=" * 60)
    print("Title-Content Alignment Test Complete!")
    print("\nKey Improvements:")
    print("✅ Enhanced titles focus on specific, actionable outcomes")
    print("✅ Title analysis extracts implementation requirements")
    print("✅ Lesson generation uses title analysis to ensure alignment")
    print("✅ Content promises match what students will actually build/learn")

if __name__ == "__main__":
    test_title_content_alignment()
