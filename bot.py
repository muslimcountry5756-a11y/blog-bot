import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from gemini_writer import write_blog, write_facebook_post
from blogger_api import create_draft
from scheduler import schedule_post
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✍️ ব্লগ লেখো", callback_data="blog")],
        [InlineKeyboardButton("📘 Facebook Post", callback_data="facebook")],
        [InlineKeyboardButton("⏰ Schedule করো", callback_data="schedule")],
        [InlineKeyboardButton("❓ সাহায্য", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🤖 *সত্যবার্তা Blog Bot-এ স্বাগতম!*\n\n"
        "আমি তোমার জন্য SEO-friendly ব্লগ লিখব এবং Blogger-এ draft করব।\n\n"
        "নিচের অপশন বেছে নাও অথবা সরাসরি topic লেখো 👇",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "blog":
        await query.message.reply_text("✍️ কোন topic-এ ব্লগ লিখব? লেখো 👇")
        context.user_data["mode"] = "blog"

    elif query.data == "facebook":
        await query.message.reply_text("📘 কোন topic-এ Facebook post লিখব? লেখো 👇")
        context.user_data["mode"] = "facebook"

    elif query.data == "schedule":
        await query.message.reply_text(
            "⏰ Schedule format:\n\n"
            "`topic | YYYY-MM-DD HH:MM`\n\n"
            "উদাহরণ:\n`ইসলামিক শিক্ষা | 2024-12-25 10:00`",
            parse_mode="Markdown"
        )
        context.user_data["mode"] = "schedule"

    elif query.data == "help":
        await query.message.reply_text(
            "📖 *কীভাবে ব্যবহার করবে:*\n\n"
            "1️⃣ `/blog টপিক` — ব্লগ লিখে Blogger-এ draft করবে\n"
            "2️⃣ `/fb টপিক` — Facebook post লিখবে\n"
            "3️⃣ `/schedule টপিক | তারিখ সময়` — নির্দিষ্ট সময়ে post করবে\n"
            "4️⃣ যেকোনো কথা লিখলেই বট বুঝবে!\n\n"
            "💡 সরাসরি topic লিখলেও ব্লগ লেখা শুরু হবে।",
            parse_mode="Markdown"
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    mode = context.user_data.get("mode", "blog")

    await update.message.reply_text("⏳ লেখা হচ্ছে, একটু অপেক্ষা করো...")

    try:
        if mode == "facebook":
            result = await write_facebook_post(text)
            await update.message.reply_text(
                f"📘 *Facebook Post তৈরি হয়েছে:*\n\n{result}",
                parse_mode="Markdown"
            )
            context.user_data["mode"] = "blog"

        elif mode == "schedule":
            if "|" in text:
                parts = text.split("|")
                topic = parts[0].strip()
                time_str = parts[1].strip()
                result = await schedule_post(topic, time_str)
                await update.message.reply_text(f"✅ {result}")
            else:
                await update.message.reply_text("❌ Format ঠিক নেই। উদাহরণ:\n`ইসলামিক শিক্ষা | 2024-12-25 10:00`", parse_mode="Markdown")
            context.user_data["mode"] = "blog"

        else:
            blog_content = await write_blog(text)
            draft_url = await create_draft(text, blog_content)
            await update.message.reply_text(
                f"✅ *ব্লগ draft হয়েছে!*\n\n"
                f"📝 Topic: {text}\n"
                f"🔗 Blogger Draft: {draft_url}\n\n"
                f"এখন Blogger-এ গিয়ে review করে publish করো।",
                parse_mode="Markdown"
            )

    except Exception as e:
        await update.message.reply_text(f"❌ সমস্যা হয়েছে: {str(e)}")

async def blog_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = " ".join(context.args)
    if not topic:
        await update.message.reply_text("Topic লেখো! যেমন: `/blog ইসলামিক শিক্ষা`", parse_mode="Markdown")
        return
    await update.message.reply_text("⏳ ব্লগ লেখা হচ্ছে...")
    try:
        blog_content = await write_blog(topic)
        draft_url = await create_draft(topic, blog_content)
        await update.message.reply_text(
            f"✅ *ব্লগ draft হয়েছে!*\n\n🔗 {draft_url}",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ সমস্যা: {str(e)}")

async def fb_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = " ".join(context.args)
    if not topic:
        await update.message.reply_text("Topic লেখো! যেমন: `/fb আজকের খবর`", parse_mode="Markdown")
        return
    await update.message.reply_text("⏳ Facebook post লেখা হচ্ছে...")
    try:
        result = await write_facebook_post(topic)
        await update.message.reply_text(f"📘 *Facebook Post:*\n\n{result}", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ সমস্যা: {str(e)}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("blog", blog_command))
    app.add_handler(CommandHandler("fb", fb_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot চালু হয়েছে!")
    app.run_polling()

if __name__ == "__main__":
    main()
