import os
import google.generativeai as genai
import asyncio

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

async def write_blog(topic: str) -> str:
    prompt = f"""
তুমি একজন বাংলা SEO ব্লগ লেখক। নিচের topic-এ একটি সম্পূর্ণ SEO-friendly বাংলা ব্লগ পোস্ট লেখো।

Topic: {topic}

নিয়ম:
1. Title: আকর্ষণীয় SEO title (H1)
2. Meta Description: ১৫০-১৬০ অক্ষরের মধ্যে
3. Introduction: ২-৩ প্যারা
4. মূল বিষয়বস্তু: H2, H3 heading ব্যবহার করে ভাগ করো
5. কমপক্ষে ৮০০ শব্দ লেখো
6. Keywords স্বাভাবিকভাবে ব্যবহার করো
7. Conclusion: summary + call to action
8. FAQ section: ৩টি প্রশ্ন-উত্তর

Format:
---TITLE---
[title এখানে]

---META---
[meta description এখানে]

---CONTENT---
[সম্পূর্ণ ব্লগ এখানে HTML format-এ]
---
"""
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, lambda: model.generate_content(prompt))
    return response.text

async def write_facebook_post(topic: str) -> str:
    prompt = f"""
তুমি একজন বাংলা Facebook content writer। নিচের topic-এ একটি আকর্ষণীয় Facebook post লেখো।

Topic: {topic}

নিয়ম:
1. শুরুতে attention-grabbing line
2. ২-৩ প্যারা সহজ বাংলায়
3. Emoji ব্যবহার করো (বেশি না)
4. শেষে relevant hashtag (৫-৮টি)
5. Call to action রাখো
6. মোট ১৫০-৩০০ শব্দ

শুধু post content লেখো, অন্য কিছু না।
"""
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, lambda: model.generate_content(prompt))
    return response.text
