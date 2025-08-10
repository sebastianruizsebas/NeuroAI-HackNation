#!/usr/bin/env python3
"""
Quick test of lesson outline endpoint
"""

import requests
import json

def test_lesson_outline_api():
    """Test the lesson outline API endpoint"""
    url = 'http://localhost:5000/api/lesson/outline'
    
    # Test data
    data = {
        "topic": "Neural Networks",
        "difficulty": "intermediate",
        "assessment_results": {
            "overall_score": 6.5,
            "knowledge_gaps": ["backpropagation", "activation functions"],
            "strong_areas": ["basic concepts"]
        }
    }
    
    try:
        print("Testing lesson outline API...")
        print(f"URL: {url}")
        print(f"Data: {json.dumps(data, indent=2)}")
        
        response = requests.post(url, json=data, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS - Lesson outline generated")
            print(f"Topic: {result.get('topic')}")
            print(f"Modules: {len(result.get('modules', []))}")
            print(f"Duration: {result.get('estimatedDuration')}")
            return True
        else:
            print("❌ FAILED")
            try:
                error = response.json()
                print(f"Error: {error}")
            except:
                print(f"Raw response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR - Is the backend running on localhost:5000?")
        return False
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT - Backend took longer than 30 seconds")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_lesson_outline_api()
    if success:
        print("\n✅ Backend lesson outline API is working!")
        print("The blank screen issue is likely in the frontend.")
    else:
        print("\n❌ Backend lesson outline API has issues!")
        print("This is the cause of the blank screen.")
