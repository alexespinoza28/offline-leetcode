#!/usr/bin/env python3
"""
Test script to verify request validation and error handling.
"""

import asyncio
from fastapi.testclient import TestClient
from orchestrator.server import app

client = TestClient(app)

def test_validation():
    """Test various validation scenarios."""
    print("Testing request validation and error handling...")
    
    # Test 1: Valid request to /api/run
    print("\n1. Testing valid request to /api/run...")
    valid_request = {
        "action": "run",
        "problem": "test-problem",
        "lang": "python",
        "code": "print('Hello, World!')"
    }
    
    response = client.post("/api/run", json=valid_request)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 2: Invalid language
    print("\n2. Testing invalid language...")
    invalid_language_request = {
        "action": "run",
        "problem": "test-problem",
        "lang": "invalid_lang",
        "code": "print('Hello, World!')"
    }
    
    response = client.post("/api/run", json=invalid_language_request)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 3: Empty code
    print("\n3. Testing empty code...")
    empty_code_request = {
        "action": "run",
        "problem": "test-problem",
        "lang": "python",
        "code": ""
    }
    
    response = client.post("/api/run", json=empty_code_request)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 4: Missing required field
    print("\n4. Testing missing required field...")
    missing_field_request = {
        "action": "run",
        "lang": "python",
        "code": "print('Hello, World!')"
        # Missing problem
    }
    
    response = client.post("/api/run", json=missing_field_request)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 5: Test validation endpoint
    print("\n5. Testing validation endpoint...")
    validate_request = {
        "code": "print('Hello, World!')",
        "language": "python"
    }
    
    response = client.post("/api/validate", json=validate_request)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    print("\nValidation tests completed!")

if __name__ == "__main__":
    test_validation()