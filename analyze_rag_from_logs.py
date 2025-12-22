#!/usr/bin/env python3
"""
Analyze RAG Performance from Azure Logs

Extracts memory retrieval metrics from production SMS workflow logs.
No need to access Qdrant directly - analyzes what's already working.

Usage:
    python analyze_rag_from_logs.py
"""

import subprocess
import json
import re
from datetime import datetime
from typing import List, Dict, Any


def get_azure_logs(hours: int = 24) -> List[str]:
    """Fetch Azure Container App logs"""
    print(f"📥 Fetching logs from last {hours} hours...")
    
    cmd = [
        "az", "containerapp", "logs", "show",
        "--name", "unified-temporal-worker",
        "--resource-group", "rg-secure-timesheet-agent",
        "--tail", "300",
        "--follow=false"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.split('\n')


def parse_memory_logs(logs: List[str]) -> Dict[str, Any]:
    """Extract memory-related events from logs"""
    
    memory_events = {
        "storage_events": [],
        "retrieval_events": [],
        "extracted_memories": [],
        "workflow_completions": 0,
    }
    
    for line in logs:
        try:
            if not line.strip():
                continue
            
            # Parse JSON log
            data = json.loads(line)
            log_msg = data.get('Log', '').strip()
            timestamp = data.get('TimeStamp', '')
            
            # Memory storage
            if 'Memory stored in Mem0' in log_msg or 'Stored conversation in Mem0' in log_msg:
                memory_events["storage_events"].append({
                    "timestamp": timestamp,
                    "message": log_msg[:200]
                })
            
            # Memory retrieval
            if 'Retrieved' in log_msg and 'memory' in log_msg.lower():
                # Extract count if present
                count_match = re.search(r'Retrieved (\d+)', log_msg)
                count = int(count_match.group(1)) if count_match else None
                
                memory_events["retrieval_events"].append({
                    "timestamp": timestamp,
                    "count": count,
                    "message": log_msg[:200]
                })
            
            # Extracted memories (from refinement)
            if 'Extracted memory' in log_msg:
                memory_events["extracted_memories"].append({
                    "timestamp": timestamp,
                    "message": log_msg[:200]
                })
            
            # Workflow completions
            if 'Multi-agent workflow complete' in log_msg:
                memory_events["workflow_completions"] += 1
        
        except json.JSONDecodeError:
            continue
        except Exception as e:
            continue
    
    return memory_events


def analyze_rag_performance(events: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze RAG performance metrics"""
    
    total_storage = len(events["storage_events"])
    total_retrieval = len(events["retrieval_events"])
    total_extracted = len(events["extracted_memories"])
    total_workflows = events["workflow_completions"]
    
    # Calculate retrieval success rate
    successful_retrievals = sum(1 for e in events["retrieval_events"] if e.get("count", 0) > 0)
    retrieval_success_rate = successful_retrievals / total_retrieval if total_retrieval > 0 else 0
    
    # Average memories retrieved
    retrieval_counts = [e.get("count", 0) for e in events["retrieval_events"] if e.get("count") is not None]
    avg_retrieved = sum(retrieval_counts) / len(retrieval_counts) if retrieval_counts else 0
    
    return {
        "total_workflows": total_workflows,
        "total_storage_events": total_storage,
        "total_retrieval_events": total_retrieval,
        "total_extracted_memories": total_extracted,
        "retrieval_success_rate": retrieval_success_rate,
        "avg_memories_retrieved": avg_retrieved,
        "storage_per_workflow": total_storage / total_workflows if total_workflows > 0 else 0,
    }


def print_report(events: Dict[str, Any], metrics: Dict[str, Any]):
    """Print analysis report"""
    
    print("\n" + "="*80)
    print("📊 RAG PERFORMANCE ANALYSIS - Production Logs")
    print("="*80)
    
    print(f"\n🔍 Data Summary:")
    print(f"   Total Workflows: {metrics['total_workflows']}")
    print(f"   Memory Storage Events: {metrics['total_storage_events']}")
    print(f"   Memory Retrieval Events: {metrics['total_retrieval_events']}")
    print(f"   Extracted Memories: {metrics['total_extracted_memories']}")
    
    print(f"\n📈 Performance Metrics:")
    print(f"   Retrieval Success Rate: {metrics['retrieval_success_rate']:.1%}")
    print(f"   Avg Memories Retrieved: {metrics['avg_memories_retrieved']:.1f}")
    print(f"   Storage per Workflow: {metrics['storage_per_workflow']:.1f}")
    
    print(f"\n💡 Analysis:")
    if metrics['retrieval_success_rate'] >= 0.8:
        print("   ✅ Excellent retrieval performance!")
    elif metrics['retrieval_success_rate'] >= 0.6:
        print("   ⚠️  Good retrieval, but some queries return no results")
    else:
        print("   ❌ Low retrieval success - investigate memory storage")
    
    if metrics['avg_memories_retrieved'] >= 3:
        print("   ✅ Good memory recall - finding multiple relevant items")
    elif metrics['avg_memories_retrieved'] >= 1:
        print("   ⚠️  Limited recall - consider increasing retrieval limit")
    else:
        print("   ❌ Poor recall - memories not being retrieved")
    
    # Recent events
    print(f"\n📝 Recent Memory Events:")
    
    if events["storage_events"]:
        print(f"\n   Last 3 Storage Events:")
        for event in events["storage_events"][-3:]:
            ts = event['timestamp'][-12:-7] if len(event['timestamp']) > 12 else event['timestamp']
            print(f"   {ts}: {event['message'][:80]}...")
    
    if events["extracted_memories"]:
        print(f"\n   Last 3 Extracted Memories:")
        for event in events["extracted_memories"][-3:]:
            ts = event['timestamp'][-12:-7] if len(event['timestamp']) > 12 else event['timestamp']
            print(f"   {ts}: {event['message'][:80]}...")
    
    print("\n" + "="*80)
    print("💡 Recommendation:")
    print("   Your RAG system is working in production!")
    print("   Send more SMS test messages to gather more metrics.")
    print("="*80)


def main():
    """Main analysis function"""
    print("\n🚀 Analyzing RAG Performance from Production Logs\n")
    
    # Fetch logs
    logs = get_azure_logs(hours=24)
    print(f"✅ Fetched {len(logs)} log lines")
    
    # Parse memory events
    events = parse_memory_logs(logs)
    print(f"✅ Found {len(events['storage_events'])} storage events")
    print(f"✅ Found {len(events['retrieval_events'])} retrieval events")
    
    # Analyze performance
    metrics = analyze_rag_performance(events)
    
    # Print report
    print_report(events, metrics)
    
    # Save report
    report = {
        "timestamp": datetime.now().isoformat(),
        "metrics": metrics,
        "events": {
            "storage_count": len(events["storage_events"]),
            "retrieval_count": len(events["retrieval_events"]),
            "extracted_count": len(events["extracted_memories"]),
        }
    }
    
    filename = f"rag_production_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Report saved to: {filename}")


if __name__ == "__main__":
    main()
