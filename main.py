import os
import google.generativeai as genai
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters

# ---------------- ENV ----------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# safety check
if not BOT_TOKEN or not GEMINI_API_KEY:
    raise Exception("Missing ENV variables")

# ---------------- GEMINI ----------------
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ---------------- TELEGRAM ----------------
bot = Bot(token=BOT_TOKEN)

app = Flask(__name__)
dispatcher = Dispatcher(bot, None, workers=0)

# ---------------- HANDLERS ----------------
def start(update, context):
    update.message.reply_text("👋 Bot is alive!")

def chat(update, context):
    user_text = update.message.text
    try:
        res = model.generate_content(user_text)
        reply = res.text
    except:
        reply = "Error from AI"
    update.message.reply_text(reply)

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

# ---------------- WEBHOOK ----------------
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

@app.route("/setwebhook", methods=["GET"])
def setwebhook():
    bot.set_webhook(WEBHOOK_URL + "/webhook")
    return "Webhook set!"

@app.route("/")
def home():
    return "Bot running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
