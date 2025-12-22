#!/usr/bin/env python3
"""
Test Harvest MCP Server
Tests if the MCP server works with the same credentials
"""

import subprocess
import requests
import json

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

def test_harvest_mcp():
    """Test Harvest MCP server with credentials from Supabase"""
    
    # 1. Get Supabase credentials
    print("🔐 Getting Supabase credentials from Azure Key Vault...")
    from supabase import create_client
    
    supabase_url = get_azure_secret('SUPABASE-URL')
    supabase_key = get_azure_secret('SUPABASE-KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials")
        return
    
    supabase = create_client(supabase_url, supabase_key)
    
    # 2. Get credentials for user1
    print("📚 Fetching credentials for user1...")
    result = supabase.table('users').select(
        'id,harvest_account_id,harvest_access_token,harvest_user_id'
    ).eq('id', 'user1').execute()
    
    if not result.data:
        print("❌ User not found")
        return
    
    user = result.data[0]
    harvest_account = user.get('harvest_account_id')
    harvest_token = user.get('harvest_access_token')
    harvest_user_id = user.get('harvest_user_id')
    
    print(f"\n📋 Using credentials:")
    print(f"  Account ID: {harvest_account}")
    print(f"  Token length: {len(harvest_token)} chars")
    print(f"  User ID: {harvest_user_id}")
    
    # 3. Test Harvest MCP via KrakenD (same as our system)
    print(f"\n🧪 Test 1: Via KrakenD Gateway (production route)")
    print(f"   URL: https://krakend-gateway.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/harvest/api/list_time_entries")
    
    payload = {
        "harvest_account": harvest_account,
        "harvest_token": harvest_token,
        "from_date": "2025-11-25",
        "to_date": "2025-11-26",
        "user_id": harvest_user_id
    }
    
    print(f"\n📦 Payload:")
    print(f"   harvest_account: {payload['harvest_account']}")
    print(f"   harvest_token: {payload['harvest_token'][:20]}...")
    print(f"   from_date: {payload['from_date']}")
    print(f"   to_date: {payload['to_date']}")
    print(f"   user_id: {payload['user_id']}")
    
    try:
        response = requests.post(
            "https://krakend-gateway.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/harvest/api/list_time_entries",
            json=payload,
            timeout=15
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        print(f"📝 Response Body: {response.text[:500]}")
        
        if response.status_code == 200:
            print("\n✅ SUCCESS! MCP works via KrakenD")
            data = response.json()
            print(f"   Response keys: {list(data.keys())}")
        elif response.status_code == 500:
            print("\n❌ FAILED! MCP returned 500 Internal Server Error")
            print("   This means MCP received the request but failed to process it")
        else:
            print(f"\n❌ FAILED! Unexpected status code")
            
    except requests.exceptions.Timeout:
        print("\n❌ Request timed out")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    # 4. Test Harvest MCP directly (internal URL)
    print(f"\n\n🧪 Test 2: Direct to Harvest MCP (internal route)")
    print(f"   URL: http://harvest-mcp.internal.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/api/list_time_entries")
    
    try:
        response2 = requests.post(
            "http://harvest-mcp.internal.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/api/list_time_entries",
            json=payload,
            timeout=15
        )
        
        print(f"\n📊 Response Status: {response2.status_code}")
        print(f"📝 Response Body: {response2.text[:500]}")
        
        if response2.status_code == 200:
            print("\n✅ SUCCESS! MCP works directly")
        else:
            print(f"\n❌ FAILED! Status {response2.status_code}")
            
    except Exception as e:
        print(f"\n⚠️ Direct connection failed (expected if not in Azure network): {e}")

if __name__ == "__main__":
    print("=" * 70)
    print("🧪 Harvest MCP Server Test")
    print("=" * 70)
    test_harvest_mcp()
    print("\n" + "=" * 70)
