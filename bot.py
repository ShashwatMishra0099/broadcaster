import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config import TOKEN

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Dictionary to store selected groups for SBroadcast
group_selection = {}

# Start command
async def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("SBroadcast", callback_data='sbroadcast')],
        [InlineKeyboardButton("GBroadcast", callback_data='gbroadcast')],
        [InlineKeyboardButton("Close Bot", callback_data='close_bot')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome! Choose an action:", reply_markup=reply_markup)

# Handle button clicks
async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "sbroadcast":
        # Get list of groups the bot is in and allow user to select
        groups = await context.bot.get_chat_administrators(update.effective_chat.id)
        group_selection[update.effective_user.id] = []
        for group in groups:
            group_selection[update.effective_user.id].append(group.chat.id)

        await query.message.reply_text("Groups selected. Now send the message to broadcast.")
    elif query.data == "gbroadcast":
        # Get all groups the bot is in and broadcast message to all
        await query.message.reply_text("Please send the message to broadcast to all groups.")
        context.user_data['gbroadcast'] = True
    elif query.data == "close_bot":
        await query.message.reply_text("Bot reset. Type /start to begin again.")
        context.user_data.clear()

# Handle incoming messages after group selection
async def message_handler(update: Update, context):
    if context.user_data.get('gbroadcast'):
        await broadcast_to_all(update.message.text, context)
        context.user_data.pop('gbroadcast', None)
    elif update.effective_user.id in group_selection:
        selected_groups = group_selection[update.effective_user.id]
        await broadcast_to_selected_groups(update.message.text, context, selected_groups)
        del group_selection[update.effective_user.id]

# Broadcast message to selected groups
async def broadcast_to_selected_groups(message, context, group_ids):
    for group_id in group_ids:
        try:
            await context.bot.send_message(chat_id=group_id, text=message)
        except Exception as e:
            logging.error(f"Failed to send message to group {group_id}: {e}")

# Broadcast message to all groups bot is added to
async def broadcast_to_all(message, context):
    updates = await context.bot.get_updates()
    group_ids = set()
    for update in updates:
        if update.message and update.message.chat.type in ["group", "supergroup"]:
            group_ids.add(update.message.chat.id)

    for group_id in group_ids:
        try:
            await context.bot.send_message(chat_id=group_id, text=message)
        except Exception as e:
            logging.error(f"Failed to send message to group {group_id}: {e}")

# Main function to start the bot
if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    application.run_polling()
