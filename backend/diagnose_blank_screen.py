#!/usr/bin/env python3
"""
Test script to diagnose assessment completion and blank screen issues.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))
import requests
import json

def test_backend_health():
    """Test if backend is responding"""
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            print("✓ Backend is running and healthy")
            return True
        else:
            print(f"✗ Backend responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to backend - is it running on localhost:5000?")
        return False
    except Exception as e:
        print(f"✗ Error testing backend: {e}")
        return False

def test_assessment_flow():
    """Test the assessment completion flow"""
    print("\nTesting assessment completion flow...")
    
    # Test data
    test_data = {
        "user_id": "test_user_123",
        "topic": "Neural Networks",
        "initial_answers": {"0": "A", "1": "B", "2": "C", "3": "A", "4": "B"},
        "adaptive_answers": {"0": "A", "1": "C", "2": "B", "3": "A", "4": "C"},
        "all_questions": [
            {"question": "Test Q1", "correct": "A", "concept": "basics"},
            {"question": "Test Q2", "correct": "B", "concept": "intermediate"},
            {"question": "Test Q3", "correct": "C", "concept": "advanced"},
            {"question": "Test Q4", "correct": "A", "concept": "basics"},
            {"question": "Test Q5", "correct": "B", "concept": "intermediate"},
            {"question": "Test Q6", "correct": "A", "concept": "advanced"},
            {"question": "Test Q7", "correct": "C", "concept": "basics"},
            {"question": "Test Q8", "correct": "B", "concept": "intermediate"},
            {"question": "Test Q9", "correct": "A", "concept": "advanced"},
            {"question": "Test Q10", "correct": "C", "concept": "basics"}
        ]
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/api/assessment/complete', 
            json=test_data,
            timeout=30  # Give it more time in case processing is slow
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Assessment completion successful")
            print(f"  Overall score: {result.get('overall_score', 'N/A')}")
            print(f"  Knowledge gaps: {len(result.get('knowledge_gaps', []))}")
            print(f"  Strong areas: {len(result.get('strong_areas', []))}")
            return True
        else:
            print(f"✗ Assessment completion failed with status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"  Error: {error_data}")
            except:
                print(f"  Raw response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ Assessment completion timed out after 30 seconds")
        print("  This suggests the backend is processing but taking too long")
        return False
    except Exception as e:
        print(f"✗ Error during assessment completion: {e}")
        return False

def test_lesson_outline_generation():
    """Test lesson outline generation that happens after assessment"""
    print("\nTesting lesson outline generation...")
    
    try:
        # Test data that would typically come from assessment
        test_data = {
            "topic": "Neural Networks",
            "difficulty": "intermediate",
            "knowledge_gaps": ["backpropagation", "activation functions"],
            "strong_areas": ["basic concepts"],
            "user_profile": {"competency_scores": {"Neural Networks": 6.5}}
        }
        
        # This endpoint might not exist, but let's test what we have
        response = requests.post(
            'http://localhost:5000/api/curriculum/generate',
            json={
                "user_id": "test_user_123",
                "topic": "Neural Networks", 
                "knowledge_gaps": ["backpropagation", "activation functions"]
            },
            timeout=20
        )
        
        if response.status_code == 200:
            print("✓ Lesson outline generation successful")
            return True
        else:
            print(f"⚠ Lesson outline generation returned status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"⚠ Error testing lesson outline: {e}")
        return False

def diagnose_blank_screen():
    """Main diagnosis function"""
    print("DIAGNOSING BLANK SCREEN AFTER ASSESSMENT")
    print("="*50)
    
    # Step 1: Check backend
    backend_ok = test_backend_health()
    
    if not backend_ok:
        print("\n❌ DIAGNOSIS: Backend is not running or not accessible")
        print("SOLUTION: Start the backend server with:")
        print("  cd backend")
        print("  python api_server.py")
        return
    
    # Step 2: Test assessment completion
    assessment_ok = test_assessment_flow()
    
    if not assessment_ok:
        print("\n❌ DIAGNOSIS: Assessment completion is failing")
        print("SOLUTION: Check backend logs for errors in assessment processing")
        return
    
    # Step 3: Test lesson outline
    lesson_ok = test_lesson_outline_generation()
    
    print(f"\n{'='*50}")
    print("DIAGNOSIS SUMMARY:")
    print(f"Backend Health: {'✓' if backend_ok else '✗'}")
    print(f"Assessment Flow: {'✓' if assessment_ok else '✗'}")
    print(f"Lesson Generation: {'✓' if lesson_ok else '⚠'}")
    
    if backend_ok and assessment_ok:
        print("\n✅ PROBABLE CAUSE: Frontend state management issue")
        print("The backend is working, so the blank screen is likely due to:")
        print("1. Frontend not properly handling the assessment completion response")
        print("2. State transition from 'assessment' to 'lesson-outline' not working")
        print("3. React component rendering issue in lesson outline")
        print("\nSOLUTION: Check browser console for JavaScript errors")
    else:
        print("\n❌ BACKEND ISSUE DETECTED")
        print("The blank screen is caused by backend processing problems")

if __name__ == "__main__":
    diagnose_blank_screen()
