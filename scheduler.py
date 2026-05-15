import asyncio
from datetime import datetime
from gemini_writer import write_blog
from blogger_api import create_draft

scheduled_jobs = []

async def schedule_post(topic: str, time_str: str) -> str:
    try:
        scheduled_time = datetime.strptime(time_str.strip(), "%Y-%m-%d %H:%M")
        now = datetime.now()

        if scheduled_time <= now:
            return "❌ সময়টা আগে চলে গেছে! ভবিষ্যতের সময় দাও।"

        delay = (scheduled_time - now).total_seconds()

        async def delayed_post():
            await asyncio.sleep(delay)
            blog_content = await write_blog(topic)
            url = await create_draft(topic, blog_content)
            return url

        asyncio.create_task(delayed_post())

        formatted = scheduled_time.strftime("%d %B %Y, %I:%M %p")
        return f"✅ Schedule হয়েছে!\n\n📝 Topic: {topic}\n⏰ সময়: {formatted}\n\nএই সময়ে Blogger-এ draft হয়ে যাবে।"

    except ValueError:
        return "❌ সময়ের format ঠিক নেই!\n\nসঠিক format: `2024-12-25 10:00`"
