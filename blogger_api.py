import os
import asyncio
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import re

BLOG_ID = os.getenv("BLOGGER_BLOG_ID", "")
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS", "")

def get_blogger_service():
    creds_data = json.loads(GOOGLE_CREDENTIALS)
    creds = Credentials(
        token=creds_data.get("token"),
        refresh_token=creds_data.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=creds_data.get("client_id"),
        client_secret=creds_data.get("client_secret"),
        scopes=["https://www.googleapis.com/auth/blogger"]
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    service = build("blogger", "v3", credentials=creds)
    return service

def parse_blog_content(raw_content: str):
    title = ""
    meta = ""
    content = ""

    title_match = re.search(r'---TITLE---\n(.*?)\n', raw_content)
    meta_match = re.search(r'---META---\n(.*?)\n', raw_content)
    content_match = re.search(r'---CONTENT---\n(.*?)---', raw_content, re.DOTALL)

    if title_match:
        title = title_match.group(1).strip()
    if meta_match:
        meta = meta_match.group(1).strip()
    if content_match:
        content = content_match.group(1).strip()

    if not title:
        lines = raw_content.split('\n')
        title = lines[0].replace('#', '').strip()
        content = raw_content

    return title, meta, content

async def create_draft(topic: str, blog_content: str) -> str:
    try:
        loop = asyncio.get_event_loop()

        title, meta, content = parse_blog_content(blog_content)

        if not title:
            title = topic

        full_content = f"""
<meta name="description" content="{meta}">
{content}
"""

        def _create():
            service = get_blogger_service()
            post = {
                "title": title,
                "content": full_content,
                "labels": [topic.split()[0] if topic else "সাধারণ"]
            }
            result = service.posts().insert(
                blogId=BLOG_ID,
                body=post,
                isDraft=True
            ).execute()
            return result.get("url", "Draft তৈরি হয়েছে")

        url = await loop.run_in_executor(None, _create)
        return url

    except Exception as e:
        return f"Draft তৈরিতে সমস্যা: {str(e)}\n\nBlogger credentials ঠিক আছে কিনা দেখো।"
