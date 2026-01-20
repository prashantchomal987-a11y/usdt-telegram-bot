import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = "8034636115:AAENbPXiZPCJviI8iaIWl8y6fDm6YCtf_Ow"
ADMIN_ID = 1603929921  # apni telegram id

MIN_USDT = 100
MAX_USDT = 5000000

bot = telebot.TeleBot(BOT_TOKEN)
user_data = {}

# ---------- START ----------
@bot.message_handler(commands=['start'])
def start(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("💰 Buy USDT", callback_data="buy"),
        InlineKeyboardButton("💸 Sell USDT", callback_data="sell")
    )
    bot.send_message(
        message.chat.id,
        "Welcome to Our Secure & Trusted USDT Buy & Sell Platform\n\nChoose an option 👇",
        reply_markup=keyboard
    )

# ---------- BUTTON HANDLER ----------
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    uid = call.from_user.id

    if call.data == "buy":
        user_data[uid] = {"type": "BUY", "step": "amount"}
        bot.send_message(call.message.chat.id, "💰 Enter USDT amount to BUY:")

    elif call.data == "sell":
        user_data[uid] = {"type": "SELL", "step": "amount"}
        bot.send_message(call.message.chat.id, "💸 Enter USDT amount to SELL:")

    elif call.data == "sell_uid":
        user_data[uid]["method"] = "BINANCE_UID"
        bot.send_message(
            call.message.chat.id,
            "✅ Send USDT via Binance Internal Transfer\n\n"
            "Binance UID: 440898957\n\n"
            "USDT send karne ke baad screenshot bhejo 📸"
        )

    elif call.data == "sell_trc20":
        user_data[uid]["method"] = "TRC20"
        bot.send_message(
            call.message.chat.id,
            "🔗 Send USDT via TRC20\n\n"
            "Network: TRC20\n"
            "Address: TP1UqtyjL96hnouDidATJmfwATfHfMx2HM\n\n"
            "⚠️ Only TRC20 network\n"
            "USDT send karne ke baad screenshot bhejo 📸"
        )

    elif call.data.startswith("approve"):
        u = int(call.data.split("_")[1])
        bot.send_message(u, "✅ Your order has been APPROVED")

    elif call.data.startswith("reject"):
        u = int(call.data.split("_")[1])
        bot.send_message(u, "❌ Your order has been REJECTED")

# ---------- TEXT HANDLER ----------
@bot.message_handler(func=lambda m: True, content_types=['text'])
def text_handler(message):
    uid = message.from_user.id

    if uid not in user_data:
        bot.send_message(message.chat.id, "Please /start se process shuru karo")
        return

    data = user_data[uid]

    # AMOUNT STEP
    if data.get("step") == "amount":
        try:
            amount = float(message.text)
        except:
            bot.send_message(message.chat.id, "❌ Valid number enter karo")
            return

        if amount < MIN_USDT or amount > MAX_USDT:
            bot.send_message(
                message.chat.id,
                f"❌ Amount limit error\n\nMinimum: {MIN_USDT} USDT\nMaximum: {MAX_USDT} USDT"
            )
            return

        data["amount"] = amount
        data["step"] = "payment"

        # BUY FLOW
        if data["type"] == "BUY":
            bot.send_message(
                message.chat.id,
                "🇮🇳 BUY USDT – PAYMENT DETAILS\n\n"
                "UPI ID: prashantlnh-3@okicici\n"
                "Account Name: Prashant Sharma\n\n"
                "Payment ke baad screenshot bhejo 📸"
            )

        # SELL FLOW → BUTTONS
        else:
            kb = InlineKeyboardMarkup()
            kb.add(
                InlineKeyboardButton("🔘 Binance UID", callback_data="sell_uid"),
                InlineKeyboardButton("🔘 USDT TRC20", callback_data="sell_trc20")
            )
            bot.send_message(
                message.chat.id,
                "Sell method choose karo 👇",
                reply_markup=kb
            )
    else:
        bot.send_message(message.chat.id, "❌ Ab sirf payment screenshot bhejo")

# ---------- PHOTO HANDLER (STRICT) ----------
@bot.message_handler(content_types=['photo'])
def photo_handler(message):
    uid = message.from_user.id

    if uid not in user_data:
        bot.send_message(message.chat.id, "❌ Invalid screenshot. Only payment screenshots are allowed.")
        return

    data = user_data[uid]

    # Screenshot already sent
    if data.get("screenshot_sent"):
        bot.send_message(message.chat.id, "❌ Screenshot has already been submitted for this order.")
        return

    # Only allow at payment step
    if data.get("step") != "payment":
        bot.send_message(message.chat.id, "❌ Do not send screenshots without completing the payment.")
        return

    data["screenshot_sent"] = True

    caption = (
        f"🆕 New USDT Order\n\n"
        f"👤 User ID: {uid}\n"
        f"🔁 Type: {data['type']}\n"
        f"💰 Amount: {data['amount']} USDT\n"
        f"📌 Method: {data.get('method','INR PAYMENT')}"
    )

    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("✅ Approve", callback_data=f"approve_{uid}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"reject_{uid}")
    )

    bot.send_photo(
        ADMIN_ID,
        message.photo[-1].file_id,
        caption=caption,
        reply_markup=kb
    )

    bot.send_message(
        message.chat.id,
        "⏳ Screenshot received.\nAdmin verification in process."
    )

# ---------- RUN ----------
bot.polling()
