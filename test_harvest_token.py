#!/usr/bin/env python3
"""
Test Harvest API Token
Tests if the token stored in Supabase works with Harvest API
"""

import os
import subprocess
import requests
from supabase import create_client

def get_azure_secret(secret_name):
    """Get secret from Azure Key Vault"""
    try:
        result = subprocess.run(
            ['az', 'keyvault', 'secret', 'show', 
             '--vault-name', 'kv-secure-agent-2ai',
             '--name', secret_name,
             '--query', 'value',
             '-o', 'tsv'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception as e:
        print(f"⚠️ Failed to get {secret_name}: {e}")
    return None

def test_harvest_token():
    """Test Harvest API token from Supabase"""
    
    # 1. Get Supabase credentials from Azure Key Vault
    print("🔐 Getting Supabase credentials from Azure Key Vault...")
    supabase_url = get_azure_secret('SUPABASE-URL')
    supabase_key = get_azure_secret('SUPABASE-KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials from Key Vault")
        return
    
    print(f"✅ Connecting to Supabase...")
    supabase = create_client(supabase_url, supabase_key)
    
    # 2. Get credentials for user1
    print(f"📚 Fetching credentials for user1...")
    result = supabase.table('users').select(
        'id,harvest_account_id,harvest_access_token,harvest_user_id'
    ).eq('id', 'user1').execute()
    
    if not result.data:
        print("❌ User 'user1' not found in Supabase")
        return
    
    user = result.data[0]
    harvest_account = user.get('harvest_account_id')
    harvest_token = user.get('harvest_access_token')
    harvest_user_id = user.get('harvest_user_id')
    
    print(f"\n📋 Credentials from Supabase:")
    print(f"  Account ID: {harvest_account}")
    print(f"  Token length: {len(harvest_token) if harvest_token else 0} chars")
    print(f"  Token starts with: {harvest_token[:10] if harvest_token else 'None'}...")
    print(f"  User ID: {harvest_user_id}")
    
    if not harvest_account or not harvest_token:
        print("\n❌ Missing Harvest credentials in Supabase")
        return
    
    # 3. Test token with Harvest API - Get current user
    print(f"\n🧪 Testing token with Harvest API...")
    print(f"   Endpoint: GET https://api.harvestapp.com/v2/users/me")
    
    headers = {
        "Harvest-Account-ID": str(harvest_account),
        "Authorization": f"Bearer {harvest_token}",
        "User-Agent": "Harvest Token Test Script"
    }
    
    try:
        response = requests.get(
            "https://api.harvestapp.com/v2/users/me",
            headers=headers,
            timeout=10
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! Token is valid")
            user_data = response.json()
            print(f"\n👤 Harvest User Info:")
            print(f"  Name: {user_data.get('first_name')} {user_data.get('last_name')}")
            print(f"  Email: {user_data.get('email')}")
            print(f"  ID: {user_data.get('id')}")
            print(f"  Is Active: {user_data.get('is_active')}")
            
            # 4. Test time entries endpoint
            print(f"\n🧪 Testing time entries endpoint...")
            print(f"   Endpoint: GET https://api.harvestapp.com/v2/time_entries?from=2025-11-25&to=2025-11-26")
            
            response2 = requests.get(
                "https://api.harvestapp.com/v2/time_entries",
                headers=headers,
                params={"from": "2025-11-25", "to": "2025-11-26"},
                timeout=10
            )
            
            print(f"\n📊 Response Status: {response2.status_code}")
            
            if response2.status_code == 200:
                print("✅ SUCCESS! Time entries endpoint works")
                entries_data = response2.json()
                entries = entries_data.get('time_entries', [])
                print(f"  Found {len(entries)} time entries")
                if entries:
                    for entry in entries[:3]:  # Show first 3
                        print(f"    - {entry.get('spent_date')}: {entry.get('hours')}h on {entry.get('project', {}).get('name', 'Unknown')}")
            elif response2.status_code == 401:
                print("❌ FAILED! 401 Unauthorized on time entries")
                print(f"   Response: {response2.text[:200]}")
            else:
                print(f"❌ FAILED! Status {response2.status_code}")
                print(f"   Response: {response2.text[:200]}")
                
        elif response.status_code == 401:
            print("❌ FAILED! Token is invalid or expired")
            print(f"   Response: {response.text[:200]}")
            print(f"\n💡 Possible issues:")
            print(f"   1. Token has expired")
            print(f"   2. Token format is incorrect")
            print(f"   3. Account ID doesn't match token")
            print(f"   4. Token was revoked in Harvest")
        else:
            print(f"❌ FAILED! Unexpected status code")
            print(f"   Response: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Harvest API Token Test")
    print("=" * 60)
    test_harvest_token()
    print("\n" + "=" * 60)
