# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import utils

from database import Database
###
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
###
connect_db = lambda: Database ("db.sqlite")

def start(bot, update):
	db = connect_db()
	chat_id = update.message.chat_id
	user = db.get_user(chat_id)
	print(user)
	message = ""
	if user is None:
		db.add_user(chat_id)
		message = "New user registered"
	else:
		message = "Hello, old user!"

	button_list = [
	    [InlineKeyboardButton("Получить прогноз по инструменту", callback_data="request_forecast")],
	    [InlineKeyboardButton("Получить стратегию по инструменту", callback_data="request_strategy")],
	    [InlineKeyboardButton("Помощь", callback_data="/help")],
	]
	reply_markup = InlineKeyboardMarkup(button_list)
	update.message.reply_text(message,reply_markup=reply_markup)


def reply(bot, update):
	update.message.reply_text('repl!')

def callback_query(bot, update):
	bot.send_message(update.callback_query.message.chat_id, "reply")


def main():
    """Start the bot."""
    updater = Updater("471404918:AAFQ1-pS0KF0u5gWnq3VpFAnfGwwePhiTk0")
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("reply", reply))
    dp.add_handler(CallbackQueryHandler(callback_query))

    # on noncommand i.e message - echo the message on Telegram
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
	main()
