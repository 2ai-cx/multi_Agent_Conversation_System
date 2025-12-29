#!/usr/bin/env python3
"""
Script to delete and recreate the daily timesheet reminder schedule with correct timezone
"""
import asyncio
import os
from datetime import datetime
from temporalio.client import Client as TemporalClient, Schedule, ScheduleActionStartWorkflow, ScheduleSpec

async def fix_schedule():
    """Delete old schedule and create new one with correct timezone"""
    
    # Connect to Temporal
    temporal_host = "temporal-dev-server.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io:443"
    print(f"🔗 Connecting to Temporal: {temporal_host}")
    
    client = await TemporalClient.connect(
        temporal_host,
        tls=True
    )
    print("✅ Connected to Temporal")
    
    schedule_id = "daily-timesheet-reminders"
    
    # Delete existing schedule
    try:
        print(f"🗑️ Deleting old schedule: {schedule_id}")
        schedule_handle = client.get_schedule_handle(schedule_id)
        await schedule_handle.delete()
        print(f"✅ Deleted old schedule")
    except Exception as e:
        if "not found" in str(e).lower():
            print(f"⚠️ Schedule not found, will create new one")
        else:
            print(f"❌ Error deleting schedule: {e}")
            raise
    
    # Create new schedule with correct timezone
    print(f"📅 Creating new schedule with correct timezone...")
    
    # Import the workflow (we need to reference it)
    # For schedule creation, we just need the workflow name
    from unified_workflows import DailyReminderScheduleWorkflow
    
    # Prepare user configurations (same as in unified_server.py)
    users_config = [
        {
            'user_id': 'user1',
            'name': 'User1',
            'phone_number': os.getenv('USER_PHONE_NUMBER', ''),
            'harvest_access_token': os.getenv('HARVEST_ACCESS_TOKEN', ''),
            'harvest_account': os.getenv('HARVEST_ACCOUNT_ID', ''),
            'endpoint': 'https://secure-timesheet-agent.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io'
        }
    ]
    
    schedule = await client.create_schedule(
        schedule_id,
        Schedule(
            spec=ScheduleSpec(
                # 8 AM Sydney time, Monday-Friday
                cron_expressions=["0 8 * * MON-FRI"],
                timezone="Australia/Sydney"
            ),
            action=ScheduleActionStartWorkflow(
                DailyReminderScheduleWorkflow.run,
                args=[users_config],
                id=f"daily_reminders_{datetime.utcnow().strftime('%Y%m%d')}",
                task_queue="timesheet-reminders"
            )
        )
    )
    
    print(f"✅ Created new schedule: {schedule_id}")
    print(f"   Cron: 0 8 * * MON-FRI")
    print(f"   Timezone: Australia/Sydney")
    print(f"   Next run: Tomorrow at 8 AM Sydney time")
    
    return True

if __name__ == "__main__":
    asyncio.run(fix_schedule())
