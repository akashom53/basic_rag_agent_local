import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_langchain_memory():
    print("🧪 Testing LangChain Buffer Memory Integration")
    
    # Test 1: First question
    print("\n1️⃣ First question about integration process...")
    try:
        response1 = requests.post(f"{BASE_URL}/chat", json={
            "message": "What is the integration process?",
            "session_id": "langchain_test_session"
        })
        
        print(f"Status Code: {response1.status_code}")
        print(f"Response Headers: {dict(response1.headers)}")
        
        response_data = response1.json()
        print(f"Full Response: {json.dumps(response_data, indent=2)}")
        
        if response1.status_code != 200:
            print(f"❌ API Error: {response_data}")
            return
            
        if 'reply' not in response_data:
            print(f"❌ Missing 'reply' key in response. Available keys: {list(response_data.keys())}")
            return
            
        print(f"✅ Response: {response_data['reply'][:100]}...")
        session_id = response_data.get("session_id", "unknown")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure your FastAPI server is running on localhost:8000")
        return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Test 2: Follow-up question (should use LangChain memory context)
    print("\n2️⃣ Follow-up question using 'this' reference...")
    try:
        response2 = requests.post(f"{BASE_URL}/chat", json={
            "message": "Can you raise a ticket for this?",
            "session_id": session_id
        })
        
        if response2.status_code == 200:
            response2_data = response2.json()
            if 'reply' in response2_data:
                print(f"✅ Response: {response2_data['reply'][:100]}...")
            else:
                print(f"❌ Missing 'reply' key in response2")
        else:
            print(f"❌ API Error: {response2.status_code} - {response2.text}")
            
    except Exception as e:
        print(f"❌ Error in follow-up: {e}")
    
    # Test 3: Check LangChain memory history
    print("\n3️⃣ Checking LangChain memory history...")
    try:
        history = requests.get(f"{BASE_URL}/chat/session/{session_id}/history")
        if history.status_code == 200:
            history_data = history.json()
            print(f"✅ Messages in memory: {history_data.get('stats', {}).get('message_count', 'unknown')}")
            print(f"✅ History: {[msg.get('role', 'unknown') for msg in history_data.get('history', [])]}")
        else:
            print(f"❌ History API Error: {history.status_code} - {history.text}")
    except Exception as e:
        print(f"❌ Error getting history: {e}")
    
    print(f"\n🎉 LangChain Buffer Memory test completed! Session ID: {session_id}")

def test_api_health():
    """Test if the API is running and healthy"""
    print("🏥 Testing API Health...")
    try:
        health = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health")
        if health.status_code == 200:
            print("✅ API is healthy and running")
            return True
        else:
            print(f"❌ API health check failed: {health.status_code}")
            return False
    except Exception as e:
        print(f"❌ API health check error: {e}")
        return False

if __name__ == "__main__":
    # First check if API is running
    if not test_api_health():
        print("\n❌ Please start your FastAPI server first:")
        print("   docker-compose up -d")
        print("   or")
        print("   python -m app.main")
        exit(1)
    
    # Then run the memory test
    test_langchain_memory()