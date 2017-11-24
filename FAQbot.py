# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram import utils
from FAQbotData import questions
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def start(bot, update):
	return greeting(bot,update,update.message.chat_id)

def greeting(bot,update,chat_id):
	message = "Добро пожаловать! О чем вы хотите узнать?"
	button_list = []
	for i, key in enumerate([x[0] for x in questions]):
		button = [InlineKeyboardButton(key, callback_data="1_{}".format(i))]
		button_list.append(button)
	reply_markup = InlineKeyboardMarkup(button_list)
	bot.send_message(chat_id,message,reply_markup=reply_markup)

def callback_query(bot, update):
	query = update.callback_query.data
	if query == "start":
		return greeting(bot,update,update.callback_query.message.chat_id)
	if query.startswith("1_"):
		return user_picked_topic(bot,update,query)
	elif query.startswith("2_"):
		return user_picked_question(bot,update,query)
	bot.send_message(update.callback_query.message.chat_id, "Invalid request")

def user_picked_topic(bot,update,query):
	message = "Выберите вопрос"
	queryparts = query.split("_")
	topic_index= queryparts[1]
	topic_questions = questions[int(topic_index)][1]
	button_list = []
	for i, question in enumerate([x[0] for x in topic_questions]):
		button = [InlineKeyboardButton(question, callback_data="2_{}_{}".format(topic_index,i))]
		button_list.append(button)
	button_list.append([InlineKeyboardButton("< Назад", callback_data="start")])
	reply_markup = InlineKeyboardMarkup(button_list)
	bot.send_message(update.callback_query.message.chat_id,message,reply_markup=reply_markup)

def user_picked_question(bot,update,query):
	queryparts = query.split("_")
	topic_index= queryparts[1]
	question_index= queryparts[2]
	question =  questions[int(topic_index)][1][int(question_index)][0]
	answer = questions[int(topic_index)][1][int(question_index)][1]
	message = "*{}*\n{}".format(question,answer)
	button_list = [[InlineKeyboardButton("< На главную", callback_data="start")]]
	reply_markup = InlineKeyboardMarkup(button_list)
	bot.send_message(update.callback_query.message.chat_id,message,parse_mode=ParseMode.MARKDOWN,reply_markup=reply_markup)

def main():
	"""Start the bot."""
	updater = Updater("472637556:AAG3w0Un2-_w4MUd0TXyNe4_WQVRPlycSOY")
	dp = updater.dispatcher
	dp.add_handler(CommandHandler("start", start))
	dp.add_handler(CallbackQueryHandler(callback_query))
	updater.start_polling()

	# Run the bot until you press Ctrl-C or the process receives SIGINT,
	# SIGTERM or SIGABRT. This should be used most of the time, since
	# start_polling() is non-blocking and will stop the bot gracefully.
	updater.idle()


if __name__ == '__main__':
	main()
