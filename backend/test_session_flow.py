#!/usr/bin/env python3
"""
Test script to verify the end session functionality works correctly
"""

import requests
import json
import time

def test_session_flow():
    """Test the complete session flow including end session"""
    base_url = "http://localhost:5000/api"
    
    try:
        # 1. Create a test user
        print("1. Creating test user...")
        user_response = requests.post(f"{base_url}/users", 
                                     json={"name": "Test Session User"})
        if user_response.status_code != 200:
            print(f"❌ Failed to create user: {user_response.status_code}")
            return
        
        user_data = user_response.json()
        user_id = user_data['user_id']
        print(f"✅ Created user: {user_id}")
        
        # 2. Start a learning session
        print("\n2. Starting learning session...")
        session_response = requests.post(f"{base_url}/session/start",
                                       json={"user_id": user_id, "topic_id": "test_topic"})
        if session_response.status_code != 200:
            print(f"❌ Failed to start session: {session_response.status_code}")
            return
        
        session_data = session_response.json()
        session_id = session_data['sessionId']
        print(f"✅ Started session: {session_id}")
        
        # 3. Wait a moment to simulate learning time
        print("\n3. Simulating learning time (3 seconds)...")
        time.sleep(3)
        
        # 4. End the learning session
        print("\n4. Ending learning session...")
        end_response = requests.post(f"{base_url}/session/end",
                                   json={"session_id": session_id})
        if end_response.status_code != 200:
            print(f"❌ Failed to end session: {end_response.status_code}")
            print(f"Response: {end_response.text}")
            return
        
        end_data = end_response.json()
        duration = end_data['duration']
        print(f"✅ Session ended successfully!")
        print(f"   Duration: {duration} minutes")
        print(f"   Expected: Around 0 minutes (3 seconds)")
        
        # 5. Verify session is marked as inactive
        print("\n5. Testing session status...")
        active_response = requests.get(f"{base_url}/session/active/{user_id}")
        if active_response.status_code == 200:
            active_sessions = active_response.json()
            if len(active_sessions.get('sessions', [])) == 0:
                print("✅ No active sessions found (correct)")
            else:
                print(f"❌ Still has active sessions: {active_sessions}")
        else:
            print(f"❌ Failed to check active sessions: {active_response.status_code}")
        
        print("\n🎉 Session flow test completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure the backend server is running on localhost:5000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    print("🧪 Testing End Session Functionality")
    print("=" * 50)
    test_session_flow()
