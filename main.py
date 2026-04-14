import os
import google.generativeai as genai
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters

# ---------------- ENV VARIABLES ----------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not BOT_TOKEN:
    raise Exception("BOT_TOKEN missing")

if not GEMINI_API_KEY:
    raise Exception("GEMINI_API_KEY missing")

# ---------------- GEMINI SETUP ----------------
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ---------------- TELEGRAM BOT ----------------
bot = Bot(token=BOT_TOKEN)

app = Flask(__name__)

dispatcher = Dispatcher(bot, None, workers=0)

# ---------------- START COMMAND ----------------
def start(update, context):
    update.message.reply_text("👋 Hello! I am your AI bot.")

# ---------------- CHAT HANDLER ----------------
def chat(update, context):
    user_text = update.message.text

    try:
        response = model.generate_content(user_text)
        reply = response.text
    except Exception as e:
        reply = f"Error: {str(e)}"

    update.message.reply_text(reply)

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

# ---------------- WEBHOOK ----------------
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

# ---------------- SET WEBHOOK ----------------
@app.route("/setwebhook", methods=["GET"])
def set_webhook():
    bot.set_webhook(WEBHOOK_URL + "/webhook")
    return "Webhook set!"

# ---------------- HOME ----------------
@app.route("/")
def home():
    return "Bot is running"

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
