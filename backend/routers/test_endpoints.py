#!/usr/bin/env python3
"""
Endpoint Testing Script for Crooks Command Center
Run this to test all your API endpoints and identify 404 issues
"""

import requests
import json
from datetime import datetime

# Configure your API base URL
API_BASE = "http://localhost:8000"  # Change this to your actual URL

def test_endpoint(method, endpoint, expected_status=200):
    """Test a single endpoint and return results"""
    url = f"{API_BASE}{endpoint}"
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=5)
        elif method.upper() == "POST":
            response = requests.post(url, timeout=5)
        
        status = response.status_code
        success = status == expected_status
        
        return {
            "endpoint": endpoint,
            "method": method,
            "status_code": status,
            "success": success,
            "response_size": len(response.text),
            "error": None if success else f"Expected {expected_status}, got {status}"
        }
    except requests.exceptions.RequestException as e:
        return {
            "endpoint": endpoint,
            "method": method,
            "status_code": None,
            "success": False,
            "response_size": 0,
            "error": str(e)
        }

def main():
    print("🔍 Testing Crooks Command Center API Endpoints")
    print("=" * 50)
    
    # Define all endpoints to test
    endpoints_to_test = [
        # Health checks
        ("GET", "/"),
        ("GET", "/health"),
        ("GET", "/api/__routes"),
        
        # Executive endpoints
        ("GET", "/api/executive/overview"),
        ("GET", "/api/executive/summary"),
        ("GET", "/api/executive/metrics"),
        ("POST", "/api/executive/refresh"),
        
        # Competitive analysis endpoints
        ("GET", "/api/competitive/analysis"),
        ("GET", "/api/competitive-analysis/comparison"),
        
        # Other common endpoints that might exist
        ("GET", "/api/shopify/dashboard"),
        ("GET", "/api/calendar/events"),
        ("GET", "/api/agency/dashboard"),
        ("GET", "/api/content/overview"),
        ("GET", "/api/intelligence/summary"),
        ("GET", "/api/media/list"),
        ("GET", "/api/summary/overview"),
    ]
    
    results = []
    working_endpoints = []
    failing_endpoints = []
    
    for method, endpoint in endpoints_to_test:
        result = test_endpoint(method, endpoint)
        results.append(result)
        
        # Print immediate result
        status_icon = "✅" if result["success"] else "❌"
        print(f"{status_icon} {method} {endpoint} - {result['status_code'] or 'ERROR'}")
        
        if result["success"]:
            working_endpoints.append(endpoint)
        else:
            failing_endpoints.append((endpoint, result["error"]))
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    print(f"✅ Working endpoints: {len(working_endpoints)}")
    print(f"❌ Failing endpoints: {len(failing_endpoints)}")
    print(f"📈 Success rate: {len(working_endpoints)/(len(working_endpoints)+len(failing_endpoints))*100:.1f}%")
    
    if failing_endpoints:
        print("\n🚨 FAILING ENDPOINTS:")
        for endpoint, error in failing_endpoints:
            print(f"   {endpoint} - {error}")
    
    if working_endpoints:
        print("\n✅ WORKING ENDPOINTS:")
        for endpoint in working_endpoints:
            print(f"   {endpoint}")
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"endpoint_test_results_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "api_base": API_BASE,
            "total_tested": len(results),
            "working_count": len(working_endpoints),
            "failing_count": len(failing_endpoints),
            "results": results
        }, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {filename}")
    
    # Provide specific recommendations
    print("\n🔧 RECOMMENDATIONS:")
    if len(failing_endpoints) > len(working_endpoints):
        print("   - Your API server might not be running")
        print("   - Check if main.py is properly configured")
        print("   - Verify router imports and registrations")
    elif any("executive" in ep for ep, _ in failing_endpoints):
        print("   - Executive router not properly registered")
        print("   - Check executive.py import in main.py")
    elif any("competitive" in ep for ep, _ in failing_endpoints):
        print("   - Competitive analysis router issues")
        print("   - Check competitive router imports")

if __name__ == "__main__":
    main()
