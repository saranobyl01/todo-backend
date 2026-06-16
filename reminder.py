import asyncio
import os
import httpx
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, text
from dateutil.relativedelta import relativedelta

from database import AsyncSessionLocal
from models import Todo, UserTelegram

async def process_reminders():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        # Try to read from db app.settings if not in env
        async with AsyncSessionLocal() as session:
            try:
                result = await session.execute(text("SELECT current_setting('app.settings.telegram_bot_token', true)"))
                bot_token = result.scalar()
            except Exception as e:
                print(f"Error reading bot token from db: {e}")

    if not bot_token:
        print("Telegram bot token is not configured.")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    async with AsyncSessionLocal() as session:
        # Find due reminders
        stmt = (
            select(Todo, UserTelegram)
            .join(UserTelegram, Todo.user_id == UserTelegram.user_id)
            .where(
                Todo.is_completed == False,
                Todo.telegram_enabled == True,
                UserTelegram.is_active == True,
                Todo.due_date <= datetime.utcnow()
            )
        )
        
        result = await session.execute(stmt)
        rows = result.all()
        
        async with httpx.AsyncClient() as client:
            for todo, user_telegram in rows:
                print(f"Sending reminder for: {todo.title} to {user_telegram.telegram_chat_id}")
                payload = {
                    "chat_id": user_telegram.telegram_chat_id,
                    "text": f"⏰ *Todo Reminder*:\n\n*{todo.title}* is due!\n\n📅 Due Date: {todo.due_date.strftime('%Y-%m-%d %H:%M:%S') if todo.due_date else ''}",
                    "parse_mode": "Markdown"
                }
                
                try:
                    response = await client.post(url, json=payload)
                    if response.status_code == 200:
                        print(f"Notification sent for '{todo.title}'")
                        
                        # Update recurrence
                        if todo.frequency == "Once" or not todo.frequency:
                            todo.telegram_enabled = False
                        elif todo.frequency == "Minute":
                            todo.due_date = todo.due_date + relativedelta(minutes=1)
                        elif todo.frequency == "Hour":
                            todo.due_date = todo.due_date + relativedelta(hours=1)
                        elif todo.frequency == "Daily":
                            todo.due_date = todo.due_date + relativedelta(days=1)
                        elif todo.frequency == "Weekly":
                            todo.due_date = todo.due_date + relativedelta(weeks=1)
                        elif todo.frequency == "Monthly":
                            todo.due_date = todo.due_date + relativedelta(months=1)
                        else:
                            todo.telegram_enabled = False
                            
                        await session.commit()
                    else:
                        print(f"Failed to send telegram notification: {response.text}")
                except Exception as e:
                    print(f"Error sending telegram message: {e}")

async def reminder_daemon():
    print("Starting reminder daemon...")
    while True:
        try:
            await process_reminders()
        except Exception as e:
            print(f"Error in reminder daemon loop: {e}")
        await asyncio.sleep(10)
