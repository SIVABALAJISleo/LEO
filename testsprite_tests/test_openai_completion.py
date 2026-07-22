# test_openai_completion.py
# TestSprite backend test for LEO OpenAI-compatible Chat Completion API.
# It makes a real HTTP request against the target environment.

import os
import requests

def test_chat_completion():
    # TARGET_URL is dynamically injected by the TestSprite execution sandbox.
    # Fallback to local dev endpoint if running directly.
    target_url = globals().get("TARGET_URL", "http://localhost:8005")
    url = f"{target_url}/v1/chat/completions"
    
    # Read automatically injected authentication headers if configured
    headers = globals().get("__AUTH_HEADERS__", {})
    if not headers:
        headers = {"Content-Type": "application/json"}
        
    payload = {
        "model": "leo-zni-turbo",
        "messages": [
            {"role": "user", "content": "Explain machine learning in one sentence."}
        ],
        "temperature": 0.7,
        "max_tokens": 128
    }
    
    print(f"Sending request to {url}...")
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    
    # Assert status code
    assert response.status_code == 200, f"Expected HTTP 200, got {response.status_code}. Body: {response.text}"
    
    data = response.json()
    assert "choices" in data, f"Missing 'choices' in response: {data}"
    assert len(data["choices"]) > 0, "Choices list is empty"
    
    message = data["choices"][0]["message"]
    assert "content" in message, f"Missing 'content' in choices[0].message: {message}"
    assert len(message["content"]) > 0, "Returned content is empty"
    
    print("Chat Completion API check PASSED ✓")
    print(f"Response: {message['content'][:100]}...")

# Execute the test function
test_chat_completion()
