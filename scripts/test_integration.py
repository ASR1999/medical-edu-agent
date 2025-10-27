#!/usr/bin/env python3
"""
Integration test script for the Medical AI Agent
Tests ASR, EHR, Agent, and TTS pipeline
"""

import requests
import json
import time
import os
import sys

API_BASE_URL = os.getenv("API_URL", "http://localhost:8000/api")

def print_test(name, status, details=""):
    """Pretty print test results"""
    symbol = "✅" if status == "PASS" else "❌"
    print(f"{symbol} {name}: {status}")
    if details:
        print(f"   {details}")
    print()


def test_hello():
    """Test basic API connectivity"""
    try:
        response = requests.get(f"{API_BASE_URL}/hello", timeout=5)
        if response.status_code == 200:
            print_test("API Connectivity", "PASS", response.json().get("message"))
            return True
        else:
            print_test("API Connectivity", "FAIL", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("API Connectivity", "FAIL", str(e))
        return False


def test_ehr_provider():
    """Test EHR provider"""
    try:
        response = requests.get(f"{API_BASE_URL}/system/provider", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_test("EHR Provider", "PASS", 
                      f"Type: {data['provider_type']}, Patients: {data['patients_available']}")
            return True
        else:
            print_test("EHR Provider", "FAIL", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("EHR Provider", "FAIL", str(e))
        return False


def test_ehr_retrieval():
    """Test EHR data retrieval"""
    patient_id = "patient_id_12345"
    try:
        response = requests.get(f"{API_BASE_URL}/ehr/{patient_id}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            patient_name = data.get("data", {}).get("personal_info", {}).get("name", "Unknown")
            print_test("EHR Retrieval", "PASS", f"Retrieved data for {patient_name}")
            return True
        else:
            print_test("EHR Retrieval", "FAIL", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("EHR Retrieval", "FAIL", str(e))
        return False


def test_rag_search():
    """Test RAG semantic search"""
    patient_id = "patient_id_12345"
    query = "diabetes medications"
    try:
        response = requests.get(
            f"{API_BASE_URL}/ehr/{patient_id}/search",
            params={"q": query, "k": 3},
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            results_count = data.get("results_count", 0)
            print_test("RAG Search", "PASS", f"Found {results_count} results for '{query}'")
            return True
        else:
            print_test("RAG Search", "FAIL", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("RAG Search", "FAIL", str(e))
        return False


def test_tts_synthesis():
    """Test TTS synthesis"""
    test_text = "Hello, this is a test of the text to speech system."
    try:
        response = requests.post(
            f"{API_BASE_URL}/test/synthesize",
            data={"text": test_text},
            timeout=30
        )
        if response.status_code == 200 and response.headers.get("content-type") == "audio/wav":
            audio_size_kb = len(response.content) / 1024
            print_test("TTS Synthesis", "PASS", f"Generated {audio_size_kb:.1f} KB audio")
            return True
        else:
            print_test("TTS Synthesis", "FAIL", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("TTS Synthesis", "FAIL", str(e))
        return False


def test_chat_text():
    """Test full chat pipeline with text input"""
    patient_id = "patient_id_12345"
    query = "What medications am I currently taking?"
    
    try:
        print(f"   Sending query: '{query}'")
        response = requests.post(
            f"{API_BASE_URL}/chat",
            data={
                "patient_id": patient_id,
                "text_query": query,
                "return_json": "true"
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            agent_response = data.get("agent_response", "")
            audio_url = data.get("audio_url", "")
            
            response_preview = agent_response[:150] + "..." if len(agent_response) > 150 else agent_response
            print_test("Chat Pipeline (Text)", "PASS", 
                      f"Response length: {len(agent_response)} chars\n   Preview: {response_preview}\n   Audio: {audio_url}")
            return True
        else:
            error_detail = response.json().get("detail", "Unknown error") if response.headers.get("content-type") == "application/json" else response.text
            print_test("Chat Pipeline (Text)", "FAIL", f"Status: {response.status_code}\n   {error_detail}")
            return False
    except Exception as e:
        print_test("Chat Pipeline (Text)", "FAIL", str(e))
        return False


def test_patients_list():
    """Test listing all patients"""
    try:
        response = requests.get(f"{API_BASE_URL}/ehr/patients", timeout=5)
        if response.status_code == 200:
            data = response.json()
            patients_count = data.get("patients_count", 0)
            print_test("List Patients", "PASS", f"{patients_count} patients available")
            return True
        else:
            print_test("List Patients", "FAIL", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("List Patients", "FAIL", str(e))
        return False


def main():
    """Run all integration tests"""
    print("=" * 60)
    print("🧪 MEDICAL AI AGENT - INTEGRATION TESTS")
    print("=" * 60)
    print(f"API Base URL: {API_BASE_URL}\n")
    
    tests = [
        ("Basic API", test_hello),
        ("EHR Provider", test_ehr_provider),
        ("Patient List", test_patients_list),
        ("EHR Retrieval", test_ehr_retrieval),
        ("RAG Search", test_rag_search),
        ("TTS Synthesis", test_tts_synthesis),
        ("Full Chat Pipeline", test_chat_text),
    ]
    
    results = []
    start_time = time.time()
    
    for test_name, test_func in tests:
        print(f"Running: {test_name}...")
        result = test_func()
        results.append((test_name, result))
        time.sleep(1)  # Brief pause between tests
    
    elapsed_time = time.time() - start_time
    
    # Summary
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{passed}/{total} tests passed ({(passed/total*100):.0f}%)")
    print(f"Total time: {elapsed_time:.2f}s\n")
    
    if passed == total:
        print("🎉 All tests passed! System is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

