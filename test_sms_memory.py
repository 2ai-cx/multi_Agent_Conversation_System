#!/usr/bin/env python3
"""
SMS Memory Testing Script
Simulates SMS messages to test the Mem0 memory system
"""

import requests
import time
from datetime import datetime

BASE_URL = "https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io"
WEBHOOK_URL = f"{BASE_URL}/webhook/sms"

# Replace with your test phone number (must be registered in Supabase users table)
TEST_PHONE = "+61412345678"  # CHANGE THIS TO YOUR PHONE NUMBER

def send_sms(message, test_num):
    """Simulate an SMS webhook from Twilio"""
    message_sid = f"TEST{int(time.time())}{test_num:03d}"
    
    print(f"\n📤 Sending SMS: {message}")
    print(f"   MessageSid: {message_sid}")
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            data={
                "From": TEST_PHONE,
                "Body": message,
                "MessageSid": message_sid
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            },
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ SMS processed successfully")
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False


def main():
    print("=" * 60)
    print("📱 SMS MEMORY TESTING")
    print("=" * 60)
    print(f"Phone: {TEST_PHONE}")
    print(f"Endpoint: {WEBHOOK_URL}")
    print("")
    print("⚠️  IMPORTANT: Make sure this phone number is registered")
    print("   in your Supabase 'users' table!")
    print("=" * 60)
    
    input("\nPress ENTER to start testing...")
    
    # Test 1: Store job information
    print("\n" + "=" * 60)
    print("TEST 1: Store Job Information")
    print("=" * 60)
    send_sms("I work as a software engineer at Google.", 1)
    print("\n⏳ Waiting 10 seconds for processing and memory indexing...")
    time.sleep(10)
    
    # Test 2: Retrieve job information
    print("\n" + "=" * 60)
    print("TEST 2: Retrieve Job Information")
    print("=" * 60)
    send_sms("What is my job?", 2)
    print("\n⏳ Waiting 10 seconds...")
    time.sleep(10)
    
    # Test 3: Store numeric data
    print("\n" + "=" * 60)
    print("TEST 3: Store Numeric Data")
    print("=" * 60)
    send_sms("I worked 847 hours last month.", 3)
    print("\n⏳ Waiting 10 seconds...")
    time.sleep(10)
    
    # Test 4: Retrieve numeric data
    print("\n" + "=" * 60)
    print("TEST 4: Retrieve Numeric Data")
    print("=" * 60)
    send_sms("How many hours did I work?", 4)
    print("\n⏳ Waiting 10 seconds...")
    time.sleep(10)
    
    # Test 5: Store multiple facts
    print("\n" + "=" * 60)
    print("TEST 5: Store Multiple Facts")
    print("=" * 60)
    send_sms("I am a senior developer at Microsoft specializing in AI.", 5)
    print("\n⏳ Waiting 10 seconds...")
    time.sleep(10)
    
    # Test 6: Retrieve multiple facts
    print("\n" + "=" * 60)
    print("TEST 6: Retrieve Multiple Facts")
    print("=" * 60)
    send_sms("Tell me about my professional background.", 6)
    print("\n⏳ Waiting 10 seconds...")
    time.sleep(10)
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 60)
    print("\n📱 Check your phone for SMS responses!")
    print("\n📊 To view detailed logs:")
    print("   az containerapp logs show --name unified-temporal-worker \\")
    print("     --resource-group rg-secure-timesheet-agent \\")
    print("     --tail 100 | grep -E 'memory|Memory|Mem0'")
    print("\n💡 Expected Results:")
    print("   - Test 2: Should mention 'software engineer' and 'Google'")
    print("   - Test 4: Should mention '847 hours'")
    print("   - Test 6: Should mention 'Microsoft' and/or 'AI'")
    print("")


if __name__ == "__main__":
    main()
