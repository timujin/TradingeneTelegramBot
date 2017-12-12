# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import utils, Bot

from database import Database
import twitterapi

###
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
###
connect_db = lambda: Database ("db.sqlite")

apikey = "485825079:AAFO6uJteoP8BidLAgHKnOQlfe-epi1zUik"

################
##### bot ######
################

def start(bot, update, chat_id=None,message=None):
	db = connect_db()
	chat_id = chat_id or update.message.chat_id
	user = db.get_user(chat_id)
	print(user)
	if message is None:
		if user is None:
			db.add_user(chat_id)
			message = "Добро пожаловать!"
		else:
			message = "Добро пожаловать!"

	button_list = [
	    [InlineKeyboardButton("Получить прогноз по инструменту", callback_data="1_forecast")],
	    [InlineKeyboardButton("Подписаться на стратегию по инструменту", callback_data="1_strategy")],
	    [InlineKeyboardButton("Сделать репост в Twitter", callback_data="twitter")],
	    [InlineKeyboardButton("Помощь", callback_data="help")],
	]
	reply_markup = InlineKeyboardMarkup(button_list)
	bot.send_message(chat_id,message,reply_markup=reply_markup)

def callback_query(bot, update):
	query = update.callback_query.data
	if query == "start":
		return start(bot, update, chat_id = update.callback_query.message.chat_id)
	if query == "help":
		return bot.send_message(update.callback_query.message.chat_id, "*текст помощи*")
	if query == "twitter":
		return prepare_repost(bot,update)
	if query == "twitter_done_repost":
		return twitter_done_repost(bot,update)
	parts = query.split("_")
	print("query", query)
	if parts[0] == "1" and parts[1] == "strategy":
		return request_strategy(bot,update)
	elif parts[0] == "1" and parts[1] == "forecast":
		return request_forecast(bot,update)
	elif parts[0] == "2" and parts[1] == "forecast":
		return picked_instrument_for_forecast(bot,update,parts[2])
	elif parts[0] == "3":
		return picked_term(bot,update,parts[1],parts[2])
	elif parts[0] == "description" and parts[1] == "sub":
		return description_sub(bot,update,parts[2])
	elif parts[0] == "confirm" and parts[1] == "sub":
		return confirm_sub(bot,update,parts[2])
	elif parts[0] == "cancel" and parts[1] == "sub":
		return cancel_sub(bot,update,parts[2])
	else:
		bot.send_message(update.callback_query.message.chat_id, "Invalid request")
		return start(bot, update, chat_id = update.callback_query.message.chat_id)


############
# forecast #
############
def request_forecast(bot,update):
	message = "Выберите инструмент"
	button_list = [
	    [InlineKeyboardButton("Bitcoin", callback_data="2_forecast_btc")],
	    [InlineKeyboardButton("Ethereum", callback_data="2_forecast_eth")],
	    [InlineKeyboardButton("Litecoin", callback_data="2_forecast_ltc")],
	]
	reply_markup = InlineKeyboardMarkup(button_list)
	bot.send_message(update.callback_query.message.chat_id,message,reply_markup=reply_markup)


def picked_instrument_for_forecast(bot,update,instr):
	message = "Выберите срок прогноза"
	button_list = [
	    [InlineKeyboardButton("Долгосрочный", callback_data="3_{}_long".format(instr))],
	    [InlineKeyboardButton("Среднесрочный", callback_data="3_{}_mid".format(instr))],
	    [InlineKeyboardButton("Краткосрочный", callback_data="3_{}_short".format(instr))],
	]
	reply_markup = InlineKeyboardMarkup(button_list)
	bot.send_message(update.callback_query.message.chat_id,message,reply_markup=reply_markup)


def picked_term(bot,update,instr,term):
	#is_ratelimited = connect_db().is_ratelimited(update.callback_query.message.chat_id)
	#if not is_ratelimited or term=="short":
	filename = "documents/{}_{}_{}.html".format("forecast",instr,term)
	bot.send_document(update.callback_query.message.chat_id,document=open(filename, 'rb'))
	#else:
	#	message = "Увы, вам доступны только краткосрочные прогнозы. Для получения доступа к остальным прогнозам сделайте репост нашего поста в Twitter"
	#	bot.send_message(update.callback_query.message.chat_id,message)
	return start(bot, update,update.callback_query.message.chat_id)


############
# strategy #
############

def request_strategy(bot,update):
	message = "На какую стратегию вы желаете подписаться?"
	button_list = [
	    [InlineKeyboardButton("Пересечение средней и цены на Ethereum", callback_data="2_strategy_0")],
	    [InlineKeyboardButton("Пересечение средней и цены на Bitcoin" , callback_data="2_strategy_1")],
	    [InlineKeyboardButton("Обратный RSI на Bitcoin", callback_data="2_strategy_2")],
	]
	reply_markup = InlineKeyboardMarkup(button_list)
	bot.send_message(update.callback_query.message.chat_id,message,reply_markup=reply_markup)

def picked_instrument_for_strategy(bot,update,instr):
	db = connect_db()
	is_subscribed = db.is_subscribed(update.callback_query.message.chat_id, instr)
	message = None
	button_list = None
	if is_subscribed:
		message = "Вы подписаны на обновления по инструменту"
		button_list = [
		    [InlineKeyboardButton("Описание", callback_data="description_sub_{}".format(instr))],
		    [InlineKeyboardButton("Отписаться", callback_data="cancel_sub_{}".format(instr))],
		    [InlineKeyboardButton("Отмена", callback_data="start")],
		]
	else:
		message = "Подписаться на обновления по инструменту?"
		button_list = [
		    [InlineKeyboardButton("Описание", callback_data="description_sub_{}".format(instr))],
		    [InlineKeyboardButton("Подписаться", callback_data="confirm_sub_{}".format(instr))],
		    [InlineKeyboardButton("Отмена", callback_data="start")],
		]
	reply_markup = InlineKeyboardMarkup(button_list)
	bot.send_message(update.callback_query.message.chat_id,message,reply_markup=reply_markup)
		

def confirm_sub(bot,update,instr):
	connect_db().subscribe_user(update.callback_query.message.chat_id, instr)
	message = "Успешно подписаны"	
	return start(bot, update,update.callback_query.message.chat_id,message=message)

def cancel_sub(bot,update,instr):
	connect_db().usubscribe_user(update.callback_query.message.chat_id, instr)
	message = "Успешно отписаны"	
	return start(bot, update,update.callback_query.message.chat_id,message=message)

def description_sub(bot,update,instr):
	message = {
		"0": "Стратегия открывает длинные позиции на паре ETHUSD, когда цена закрытия пересекает скользящую среднюю снизу-вверх. Короткая позиция открывается, когда цена закрытия пересекает скользящую среднюю сверху-вниз.\nПараметр средней: 10\nВременной интервал: 60 минут",
		"1": "Стратегия открывает только длинные позиции на паре BTCUSD, когда цена закрытия пересекает скользящую среднюю снизу-вверх. Сделка закрывается, когда цена закрытия пересекает скользящую среднюю сверху-вниз.\nПараметр средней: 60\nВременной интервал: 60 минут",
		"2": "Известная стратегия обратный RSI открывает длинные позиции, когда индикатор RSI превышает верхнее пороговое значение. Короткие позиции открываются, когда индикатор RSI меньше нижнего порогового значения.\nПараметр RSI: 14\nВерхнее пороговое значение: 70\nНижнее пороговое значение: 30\nВременной интервал: 30",
	}[instr]
	bot.send_message(update.callback_query.message.chat_id,message)
	
		
###########
# twitter #
###########

def prepare_repost(bot,update):
	message = "Напишите ваше имя пользователя Twitter в формате @username"
	bot.send_message(update.callback_query.message.chat_id,message)

def register_twitter_name(bot,update):
	text = update.message.text
	if text[0] != "@":
		return start(bot,update)
	else:
		user_exists = twitterapi.doesUserExist(text[1:])
		if not user_exists:
			message = "Невозможно зарегистрировать пользователя Twitter: такого пользователя не существует"
			bot.send_message(chat_id=update.message.chat_id, text=message)
		else:
			connect_db().setTwitterUsername(update.message.chat_id,text[1:])
			message = "Зарегистрировано имя Twitter: {}".format(text)
			bot.send_message(chat_id=update.message.chat_id, text=message)
			share_repost(bot,update)


def share_repost(bot,update):
	print("sharing repost")
	tw = connect_db().getTwitterUsername(update.message.chat_id)
	message = "Сделайте репост этой записи на своем аккаунте Twitter:\n {}".format(twitterapi.retweet_link)
	button_list = [
	    [InlineKeyboardButton("Сделано!", callback_data="twitter_done_repost")],
	]
	reply_markup = InlineKeyboardMarkup(button_list)
	bot.send_message(chat_id=update.message.chat_id, text=message,reply_markup=reply_markup)


def twitter_done_repost(bot,update):
	chatId = update.callback_query.message.chat_id
	username = connect_db().getTwitterUsername(chatId)
	status = twitterapi.getLastStatusByUsername(username)
	res = twitterapi.isLastStatusOurRepost(status)
	if res:
		connect_db().unlock_user(chatId)
		bot.send_message(chat_id=chatId, text="Репост зарегистрирован, возможности бота расширены")	
	else:
		bot.send_message(chat_id=chatId, text="Репост не найден")	
	return start(bot, update,update.callback_query.message.chat_id)

################
### signals ####
################

import threading
import time

class SignalThread (threading.Thread):
	exitFlag = 0
	def __init__(self, threadID, name):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name

	def run(self):
		print "Starting " + self.name
		poll_signals()
		print "Exiting " + self.name

def poll_signals():
	while True:
		db = connect_db()
		signals = db.getSignals()
		#print("tick", signals)
		if signals is not []:
			process_signals(signals)
		db.clearSignals()
		time.sleep(1)

def process_signals(signals):
	for signal in signals:
		print("Signal", signal)
		users = connect_db().get_subscribed_users(signal[0])
		for chatId in users:
			print ("sending...", chatId[0])
			Bot(apikey).send_message(chat_id=chatId[0], text=signal[1])

###########################

def main():
	"""Start the bot."""
	updater = Updater(apikey)
	dp = updater.dispatcher
	dp.add_handler(CommandHandler("start", start))
	dp.add_handler(CallbackQueryHandler(callback_query))

	twitter_handler = MessageHandler(Filters.text, register_twitter_name)
	dp.add_handler(twitter_handler)
	updater.start_polling()

	thread1 = SignalThread(1, "Thread-1")
	thread1.start()
	# Run the bot until you press Ctrl-C or the process receives SIGINT,
	# SIGTERM or SIGABRT. This should be used most of the time, since
	# start_polling() is non-blocking and will stop the bot gracefully.
	updater.idle()
	SignalThread.exit_flag = 1

if __name__ == '__main__':
	main()
