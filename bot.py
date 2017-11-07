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
	    [InlineKeyboardButton("Получить прогноз по инструменту", callback_data="1_forecast")],
	    [InlineKeyboardButton("Получить стратегию по инструменту", callback_data="1_strategy")],
	    [InlineKeyboardButton("Помощь", callback_data="help")],
	]
	reply_markup = InlineKeyboardMarkup(button_list)
	update.message.reply_text(message,reply_markup=reply_markup)

def callback_query(bot, update):
	query = update.callback_query.data
	if query == "help":
		return bot.send_message(update.callback_query.message.chat_id, "Help text")


	parts = query.split("_")
	if parts[0] == "1":
		return request(parts[1],bot,update)
	elif parts[0] == "2":
		return picked_instrument(parts[1],parts[2],bot,update)
	elif parts[0] == "3":
		return picked_term(parts[1],parts[2],parts[3],bot,update)
	else:
		bot.send_message(update.callback_query.message.chat_id, "Invalid request")
		return start(bot, update)


def request(req,bot,update):
	message = "Выберите инструмент"
	button_list = [
	    [InlineKeyboardButton("Bitcoin", callback_data="2_{}_btc".format(req))],
	    [InlineKeyboardButton("Ethereum", callback_data="2_{}_eth".format(req))],
	    [InlineKeyboardButton("Litecoin", callback_data="2_{}_ltc".format(req))],
	]
	reply_markup = InlineKeyboardMarkup(button_list)
	bot.send_message(update.callback_query.message.chat_id,message,reply_markup=reply_markup)


def picked_instrument(req,instr,bot,update):
	message = "Выберите срок прогноза"
	button_list = [
	    [InlineKeyboardButton("Долгосрочный", callback_data="3_{}_{}_long".format(req,instr))],
	    [InlineKeyboardButton("Среднесрочный", callback_data="3_{}_{}_mid".format(req,instr))],
	    [InlineKeyboardButton("Краткосрочный", callback_data="3_{}_{}_short".format(req,instr))],
	]
	reply_markup = InlineKeyboardMarkup(button_list)
	bot.send_message(update.callback_query.message.chat_id,message,reply_markup=reply_markup)

def picked_term(req,instr,term,bot,update):
	


def main():
	"""Start the bot."""
	updater = Updater("471404918:AAFQ1-pS0KF0u5gWnq3VpFAnfGwwePhiTk0")
	dp = updater.dispatcher

	# on different commands - answer in Telegram
	dp.add_handler(CommandHandler("start", start))
	dp.add_handler(CallbackQueryHandler(callback_query))

	# on noncommand i.e message - echo the message on Telegram
	updater.start_polling()

	# Run the bot until you press Ctrl-C or the process receives SIGINT,
	# SIGTERM or SIGABRT. This should be used most of the time, since
	# start_polling() is non-blocking and will stop the bot gracefully.
	updater.idle()


if __name__ == '__main__':
	main()
