#!/usr/bin/env python3
"""
Test the new Chart.js-based web analytics system
"""

import json
import requests
import sys
import time

def test_web_analytics():
    """Test the new web analytics endpoints"""
    base_url = "http://localhost:5000/api"
    test_user_id = "test_user_123"
    
    print("🧪 Testing Modern Web Analytics System")
    print("=" * 50)
    
    # Test endpoints
    endpoints = [
        ("/analytics/all", "All Analytics Data"),
        ("/analytics/pie", "Pie Chart Data"),
        ("/analytics/progress", "Progress Over Time"),
        ("/analytics/performance", "Topic Performance"),
        ("/analytics/activity", "Weekly Activity")
    ]
    
    results = {}
    
    for endpoint, description in endpoints:
        url = f"{base_url}{endpoint}/{test_user_id}"
        print(f"\n📊 Testing: {description}")
        print(f"URL: {url}")
        
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                results[endpoint] = {
                    'status': 'SUCCESS',
                    'response_time': f"{response_time:.2f}s",
                    'data_keys': list(data.keys()) if isinstance(data, dict) else 'non-dict',
                    'data_size': len(str(data))
                }
                print(f"✅ SUCCESS - Response time: {response_time:.2f}s")
                print(f"   Data keys: {list(data.keys()) if isinstance(data, dict) else 'non-dict'}")
                print(f"   Data size: {len(str(data))} characters")
                
                # Validate Chart.js structure
                if 'datasets' in str(data):
                    print("   ✅ Chart.js compatible structure detected")
                else:
                    print("   ⚠️  Warning: No 'datasets' found in response")
                
            else:
                results[endpoint] = {
                    'status': 'FAILED',
                    'error': f"HTTP {response.status_code}",
                    'response': response.text[:200]
                }
                print(f"❌ FAILED - HTTP {response.status_code}")
                print(f"   Error: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            results[endpoint] = {
                'status': 'ERROR',
                'error': str(e)
            }
            print(f"❌ ERROR - {str(e)}")
    
    # Print summary
    print("\n" + "=" * 50)
    print("📈 TEST SUMMARY")
    print("=" * 50)
    
    success_count = sum(1 for r in results.values() if r['status'] == 'SUCCESS')
    total_count = len(results)
    
    print(f"Successful tests: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 ALL TESTS PASSED! Modern analytics system is working!")
        print("\n💡 Next steps:")
        print("   1. Start the backend server: python api_server.py")
        print("   2. Start the frontend: npm run dev")
        print("   3. Navigate to the Analytics tab in the dashboard")
        print("   4. Enjoy modern, interactive Chart.js analytics!")
        return True
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return False

def test_chart_data_structure():
    """Test that the data structure matches Chart.js requirements"""
    print("\n🔍 Testing Chart.js Data Structure Compatibility")
    print("-" * 50)
    
    from web_analytics_service import WebAnalyticsService
    analytics_service = WebAnalyticsService()
    
    # Test pie chart structure
    pie_data = analytics_service.get_pie_chart_data("test_user")
    expected_pie_keys = ['labels', 'datasets']
    
    print("📊 Pie Chart Data Structure:")
    for key in expected_pie_keys:
        if key in pie_data:
            print(f"   ✅ {key}: Present")
        else:
            print(f"   ❌ {key}: Missing")
    
    # Test line chart structure
    line_data = analytics_service.get_progress_over_time_data("test_user")
    expected_line_keys = ['labels', 'datasets']
    
    print("\n📈 Line Chart Data Structure:")
    for key in expected_line_keys:
        if key in line_data:
            print(f"   ✅ {key}: Present")
        else:
            print(f"   ❌ {key}: Missing")
    
    # Test dataset structure
    if 'datasets' in pie_data and pie_data['datasets']:
        dataset = pie_data['datasets'][0]
        expected_dataset_keys = ['data', 'backgroundColor']
        print(f"\n🎨 Dataset Structure (Pie Chart):")
        for key in expected_dataset_keys:
            if key in dataset:
                print(f"   ✅ {key}: Present")
            else:
                print(f"   ❌ {key}: Missing")
    
    print("\n✅ Chart.js compatibility check complete!")

if __name__ == "__main__":
    print("🚀 Modern Analytics Testing Suite")
    print("=" * 50)
    
    # Test data structure first
    try:
        test_chart_data_structure()
    except Exception as e:
        print(f"❌ Data structure test failed: {e}")
    
    # Test API endpoints (requires server to be running)
    print("\n⚠️  Make sure the backend server is running (python api_server.py)")
    input("Press Enter to continue with API tests...")
    
    try:
        success = test_web_analytics()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Testing cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
