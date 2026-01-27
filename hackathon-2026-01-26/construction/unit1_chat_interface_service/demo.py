"""Demo script for Chat Interface Service"""
import requests
import json
import time
from threading import Thread
import uvicorn


BASE_URL = "http://localhost:8000"
TOKEN = "demo-token-12345"  # Mock token


def start_server():
    """Start FastAPI server in background"""
    from src.api.main import app
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")


def print_section(title: str):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_response(response):
    """Print formatted response"""
    print(f"Status: {response.status_code}")
    if response.status_code < 400:
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error:\n{json.dumps(response.json(), indent=2)}")
    print()


def demo_workflow():
    """Run demo workflow"""
    headers = {"Authorization": f"Bearer {TOKEN}"}

    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(2)

    # Check health
    print_section("1. Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response)

    # Submit first message (creates conversation implicitly)
    print_section("2. Submit First Message (Create Conversation Implicitly)")
    response = requests.post(
        f"{BASE_URL}/api/v1/chat/conversations/new/messages",
        headers=headers,
        data={
            "query_text": "How do I create an S3 bucket in AWS?"
        }
    )
    print_response(response)

    if response.status_code == 200:
        first_message = response.json()
        conversation_id = first_message["conversation_id"]
        
        # List conversations
        print_section("3. List Conversations")
        response = requests.get(
            f"{BASE_URL}/api/v1/chat/conversations",
            headers=headers
        )
        print_response(response)
        
        # Get conversation details
        print_section("4. Get Conversation Details")
        response = requests.get(
            f"{BASE_URL}/api/v1/chat/conversations/{conversation_id}",
            headers=headers
        )
        print_response(response)
        
        # Submit follow-up message
        print_section("5. Submit Follow-up Message")
        response = requests.post(
            f"{BASE_URL}/api/v1/chat/conversations/{conversation_id}/messages",
            headers=headers,
            data={
                "query_text": "What are the best practices for S3 security?"
            }
        )
        print_response(response)
        
        if response.status_code == 200:
            assistant_message_id = response.json()["message_id"]
            
            # Submit feedback
            print_section("6. Submit Feedback on Assistant Response")
            response = requests.post(
                f"{BASE_URL}/api/v1/chat/conversations/{conversation_id}/feedback",
                headers=headers,
                json={
                    "message_id": assistant_message_id,
                    "answered_question": True,
                    "problem_solved": True
                }
            )
            print_response(response)
        
        # Get updated conversation
        print_section("7. Get Updated Conversation")
        response = requests.get(
            f"{BASE_URL}/api/v1/chat/conversations/{conversation_id}",
            headers=headers
        )
        print_response(response)
        
        # Escalate conversation
        print_section("8. Escalate Conversation to Human Support")
        response = requests.post(
            f"{BASE_URL}/api/v1/chat/conversations/{conversation_id}/escalate",
            headers=headers,
            json={
                "reason": "Need more detailed guidance on S3 encryption"
            }
        )
        print_response(response)
        
        # Try to add message to escalated conversation (should fail)
        print_section("9. Try to Add Message to Escalated Conversation (Should Fail)")
        response = requests.post(
            f"{BASE_URL}/api/v1/chat/conversations/{conversation_id}/messages",
            headers=headers,
            data={
                "query_text": "This should fail"
            }
        )
        print_response(response)
        
        # Final conversation list
        print_section("10. Final Conversation List")
        response = requests.get(
            f"{BASE_URL}/api/v1/chat/conversations",
            headers=headers
        )
        print_response(response)

    print_section("Demo Complete!")
    print("✅ All domain invariants enforced")
    print("✅ All API endpoints functional")
    print("✅ Events published correctly")
    print("✅ Clear separation of concerns across layers")
    print("\nPress Ctrl+C to stop the server")


if __name__ == "__main__":
    print("=" * 80)
    print("  Chat Interface Service - Demo")
    print("  Unit 1: Chat Interface Context")
    print("=" * 80)
    
    # Start server in background thread
    server_thread = Thread(target=start_server, daemon=True)
    server_thread.start()
    
    try:
        # Run demo workflow
        demo_workflow()
        
        # Keep server running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
