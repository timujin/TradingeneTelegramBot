import threading
import time
from database import Database
connect_db = lambda: Database ("db.sqlite")

from flask import Flask
from flask import request
app = Flask(__name__)

@app.route('/postjson', methods = ['POST'])
def postJsonHandler():
	content = request.get_json()
	try:
		instrument = content["instrument"]
		message = content["message"]
		connect_db().addSignal(instrument,message)
		return 'JSON posted'
	except:
		return 'Incorrect request'

if __name__=="__main__":
    	app.run(host='127.0.0.1',port=8000,debug=True)
