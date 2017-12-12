# -*- coding: utf-8 -*-
import threading
import time
from database import Database
connect_db = lambda: Database ("db.sqlite")

from flask import Flask
from flask import request
app = Flask(__name__)

def parse_json(content):
	res = {}
	res["direction"] = content["direction"] 	#направление
	if content["algorithmId"] == 0:
		res["instrument"] = u"Пересечение средней и цены на Ethereum"
	if content["algorithmId"] == 1:
		res["instrument"] = u"Пересечение средней и цены на Bitcoin"
	if content["algorithmId"] == 2:
		res["instrument"] = u"Обратный RSI на Bitcoin"

	if res["direction"] in ["buy","sell"]:
		res["previous"]=content["previous"]	# предыдущая сделка
		res["since_launch"]=content["since_launch"] # с момента запуска стратегии
	elif res["direction"] == "close":
		res["result"] = content["result"] # результат сделки
	else:
		raise
	return res

def generate_message(content):
	if content["direction"] in ["buy","sell"]:
		return u"""Инструмент: {}\nНаправление: {}\nПредыдущая сделка: {} usd\nС момента запуска стратегии: {} usd""".format(
			content["instrument"], content["direction"], content["previous"], content["since_launch"]
		)
	elif content["direction"] == "close":
		return u"""Инструмент: {}\nНаправление: close (flat)\nРезультат сделки: {} usd""".format(
			content["instrument"], content["result"]
		)

@app.route('/postjson', methods = ['POST'])
def postJsonHandler():
	content = request.get_json()
	try:
		instrument = content["algorithmId"]
		content = parse_json(content)
		message = generate_message(content)
		connect_db().addSignal(instrument,message)
		return 'JSON posted'
	except Exception as e:
		return 'Incorrect request, ' + str(e)

if __name__=="__main__":
    	app.run(host='127.0.0.1',port=8000,debug=True)
