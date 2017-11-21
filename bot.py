# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import utils

from database import Database
import twitterapi

###
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
###
connect_db = lambda: Database ("db.sqlite")

def start(bot, update, chat_id=None):
	db = connect_db()
	chat_id = chat_id or update.message.chat_id
	user = db.get_user(chat_id)
	print(user)
	message = ""
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

	if query.startswith("cancel_sub"):
		return cancel_sub(bot,update)
	if query.startswith("confirm_sub"):
		return confirm_sub(bot,update)

	parts = query.split("_")
	if parts[0] == "1":
		return request(parts[1],bot,update)
	elif parts[0] == "2":
		return picked_instrument(parts[1],parts[2],bot,update)
	elif parts[0] == "3":
		return picked_term(parts[1],parts[2],parts[3],bot,update)
	else:
		bot.send_message(update.callback_query.message.chat_id, "Invalid request")
		return start(bot, update, chat_id = update.callback_query.message.chat_id)


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
	if req == "forecast":
		return picked_instrument_for_forecast(req,instr,bot,update)
	elif req == "strategy":
		return picked_instrument_for_strategy(req,instr,bot,update)

def picked_instrument_for_forecast(req,instr,bot,update):
	message = "Выберите срок прогноза"
	button_list = [
	    [InlineKeyboardButton("Долгосрочный", callback_data="3_{}_{}_long".format(req,instr))],
	    [InlineKeyboardButton("Среднесрочный", callback_data="3_{}_{}_mid".format(req,instr))],
	    [InlineKeyboardButton("Краткосрочный", callback_data="3_{}_{}_short".format(req,instr))],
	]
	reply_markup = InlineKeyboardMarkup(button_list)
	bot.send_message(update.callback_query.message.chat_id,message,reply_markup=reply_markup)


def picked_instrument_for_strategy(req,instr,bot,update):
	db = connect_db()
	is_subscribed = db.is_subscribed(update.callback_query.message.chat_id, instr)
	message = None
	button_list = None
	if is_subscribed:
		message = "Вы подписаны на обновления по инструменту"
		button_list = [
		    [InlineKeyboardButton("Отписаться", callback_data="cancel_sub_{}".format(instr))],
		    [InlineKeyboardButton("Отмена", callback_data="start".format(req,instr))],
		]
	else:
		message = "Подписаться на обновления по инструменту?"
		button_list = [
		    [InlineKeyboardButton("Подписаться", callback_data="confirm_sub_{}".format(instr))],
		    [InlineKeyboardButton("Отмена", callback_data="start".format(req,instr))],
		]
	reply_markup = InlineKeyboardMarkup(button_list)
	bot.send_message(update.callback_query.message.chat_id,message,reply_markup=reply_markup)
				


def picked_term(req,instr,term,bot,update):
	is_ratelimited = connect_db().is_ratelimited(update.callback_query.message.chat_id)
	if not is_ratelimited or term=="short":
		filename = "documents/{}_{}_{}.html".format(req,instr,term)
		bot.send_document(update.callback_query.message.chat_id,document=open(filename, 'rb'))
	else:
		message = "Увы, вам доступны только краткосрочные прогнозы. Для получения доступа к остальным прогнозам сделайте репост нашего поста в Twitter"
		bot.send_message(update.callback_query.message.chat_id,message)
	return start(bot, update,update.callback_query.message.chat_id)


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
		

def confirm_sub(bot,update):
	instr = update.callback_query.data[-3:]
	connect_db().subscribe_user(update.callback_query.message.chat_id, instr)
	message = "Successfully subscribed!"	
	return start(bot, update,update.callback_query.message.chat_id)

def cancel_sub(bot,update):
	instr = update.callback_query.data[-3:]
	connect_db().usubscribe_user(update.callback_query.message.chat_id, instr)
	message = "Successfully unsubscribed!"	
	return start(bot, update,update.callback_query.message.chat_id)

def main():
	"""Start the bot."""
	updater = Updater("471404918:AAFQ1-pS0KF0u5gWnq3VpFAnfGwwePhiTk0")
	dp = updater.dispatcher
	dp.add_handler(CommandHandler("start", start))
	dp.add_handler(CallbackQueryHandler(callback_query))

	twitter_handler = MessageHandler(Filters.text, register_twitter_name)
	dp.add_handler(twitter_handler)
	updater.start_polling()

	# Run the bot until you press Ctrl-C or the process receives SIGINT,
	# SIGTERM or SIGABRT. This should be used most of the time, since
	# start_polling() is non-blocking and will stop the bot gracefully.
	updater.idle()


if __name__ == '__main__':
	main()
