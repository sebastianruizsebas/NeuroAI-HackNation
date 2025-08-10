#!/usr/bin/env python3
"""
Simple test to check lesson outline generation which might be causing the blank screen.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_lesson_outline_locally():
    """Test lesson outline generation locally"""
    try:
        from profai_engine import ProfAIEngine
        
        print("Testing lesson outline generation locally...")
        engine = ProfAIEngine()
        
        # Test data similar to what would come from assessment
        topic = "Neural Networks"
        difficulty = "intermediate"
        user_assessment = {
            'overall_score': 6.5,
            'knowledge_gaps': ['backpropagation', 'activation functions'],
            'strong_areas': ['basic concepts', 'perceptrons'],
            'learning_path': ['fundamentals', 'architecture', 'training']
        }
        
        print(f"Generating outline for: {topic}")
        print(f"Difficulty: {difficulty}")
        print(f"Assessment data: {user_assessment}")
        
        outline = engine.generate_lesson_outline(topic, difficulty, user_assessment)
        
        if outline:
            print("✓ Lesson outline generated successfully!")
            print(f"Topic: {outline.get('topic')}")
            print(f"Modules: {len(outline.get('modules', []))}")
            print(f"Duration: {outline.get('estimatedDuration')}")
            
            # Check if all required fields are present
            required_fields = ['topic', 'difficulty', 'estimatedDuration', 'learningObjectives', 'modules']
            missing_fields = [field for field in required_fields if field not in outline]
            
            if missing_fields:
                print(f"⚠ Missing fields: {missing_fields}")
            else:
                print("✓ All required fields present")
                
            return True
        else:
            print("✗ Lesson outline generation returned None")
            return False
            
    except Exception as e:
        print(f"✗ Error testing lesson outline: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_blank_screen_cause():
    """Analyze potential causes of blank screen"""
    print("ANALYZING BLANK SCREEN AFTER INITIAL ASSESSMENT")
    print("=" * 60)
    
    # Test 1: Can we generate lesson outline?
    outline_ok = test_lesson_outline_locally()
    
    print(f"\n{'=' * 60}")
    print("ANALYSIS RESULTS:")
    print(f"Lesson Outline Generation: {'✓' if outline_ok else '✗'}")
    
    if outline_ok:
        print("\n✅ DIAGNOSIS: Backend lesson outline generation is working")
        print("The blank screen is likely due to:")
        print("1. Frontend timeout waiting for response")
        print("2. JavaScript/React rendering error")
        print("3. Missing error handling in LessonOutline component")
        print("4. Assessment completion not properly setting state")
        
        print("\nRECOMMENDED ACTIONS:")
        print("1. Check browser console for JavaScript errors")
        print("2. Add console.log statements in Assessment.tsx handleAssessmentComplete")
        print("3. Add console.log statements in LessonOutline.tsx useEffect")
        print("4. Verify App.tsx state transitions from 'assessment' to 'lesson-outline'")
        
    else:
        print("\n❌ DIAGNOSIS: Backend lesson outline generation is failing")
        print("The blank screen is caused by backend errors")
        print("Check the lesson outline generation method in profai_engine.py")

if __name__ == "__main__":
    analyze_blank_screen_cause()
