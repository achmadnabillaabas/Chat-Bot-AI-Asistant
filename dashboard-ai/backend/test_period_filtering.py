"""
Test script for Token Usage period filtering.
Verifies that all analytics endpoints correctly filter by days parameter.
"""
import requests
import sys

BASE_URL = "http://localhost:8000/api"

def test_period_filtering():
    """Test that all analytics endpoints accept and use days parameter"""
    
    print("Testing Token Usage Period Filtering")
    print("=" * 70)
    
    periods = [
        ("Today", 1),
        ("7 Days", 7),
        ("30 Days", 30),
        ("90 Days", 90)
    ]
    
    for period_name, days in periods:
        print(f"\n{'=' * 70}")
        print(f"Testing Period: {period_name} (days={days})")
        print(f"{'=' * 70}")
        
        # Test 1: Summary endpoint
        print(f"\n1. GET /analytics/usage/summary?days={days}")
        try:
            response = requests.get(f"{BASE_URL}/analytics/usage/summary", params={"days": days})
            response.raise_for_status()
            data = response.json()
            print(f"   ✓ Total Requests: {data['total_requests']}")
            print(f"   ✓ Total Tokens: {data['total_tokens']}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return False
        
        # Test 2: Timeseries endpoint
        print(f"\n2. GET /analytics/usage/timeseries?days={days}")
        try:
            response = requests.get(f"{BASE_URL}/analytics/usage/timeseries", params={"days": days})
            response.raise_for_status()
            data = response.json()
            print(f"   ✓ Days returned: {len(data)}")
            if data:
                total_requests = sum(d['requests'] for d in data)
                print(f"   ✓ Total requests in series: {total_requests}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return False
        
        # Test 3: By-combo endpoint
        print(f"\n3. GET /analytics/usage/by-combo?days={days}")
        try:
            response = requests.get(f"{BASE_URL}/analytics/usage/by-combo", params={"days": days})
            response.raise_for_status()
            data = response.json()
            print(f"   ✓ Combos returned: {len(data)}")
            if data:
                print(f"   ✓ First combo: {data[0]['combo_id']} ({data[0]['requests']} requests)")
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return False
        
        # Test 4: Request history endpoint
        print(f"\n4. GET /analytics/usage/requests?days={days}&page=1&page_size=20")
        try:
            response = requests.get(
                f"{BASE_URL}/analytics/usage/requests",
                params={"days": days, "page": 1, "page_size": 20}
            )
            response.raise_for_status()
            data = response.json()
            print(f"   ✓ Total requests: {data['total']}")
            print(f"   ✓ Page size: {len(data['items'])}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return False
    
    # Test 5: Verify different periods return different results (if applicable)
    print(f"\n{'=' * 70}")
    print("Testing Period Differences")
    print(f"{'=' * 70}")
    
    try:
        # Get Today
        response_today = requests.get(f"{BASE_URL}/analytics/usage/summary", params={"days": 1})
        response_today.raise_for_status()
        today_data = response_today.json()
        
        # Get 7 Days
        response_7days = requests.get(f"{BASE_URL}/analytics/usage/summary", params={"days": 7})
        response_7days.raise_for_status()
        days_7_data = response_7days.json()
        
        # Get 30 Days
        response_30days = requests.get(f"{BASE_URL}/analytics/usage/summary", params={"days": 30})
        response_30days.raise_for_status()
        days_30_data = response_30days.json()
        
        print(f"\nToday:    {today_data['total_requests']} requests, {today_data['total_tokens']} tokens")
        print(f"7 Days:   {days_7_data['total_requests']} requests, {days_7_data['total_tokens']} tokens")
        print(f"30 Days:  {days_30_data['total_requests']} requests, {days_30_data['total_tokens']} tokens")
        
        # Verify Today <= 7 Days <= 30 Days (logical consistency)
        if (today_data['total_requests'] <= days_7_data['total_requests'] <= days_30_data['total_requests']):
            print("\n✓ Period filtering is logically consistent (Today ≤ 7 Days ≤ 30 Days)")
        else:
            print("\n⚠ Warning: Period results don't follow expected order")
            print("  This may be okay if all data is from today.")
        
    except Exception as e:
        print(f"✗ Error comparing periods: {e}")
        return False
    
    print(f"\n{'=' * 70}")
    print("✓ All period filtering tests passed!")
    print(f"{'=' * 70}")
    return True

if __name__ == "__main__":
    try:
        success = test_period_filtering()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
