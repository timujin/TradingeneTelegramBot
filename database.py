import sqlite3

class Database:
	def __init__(self, filename):
		self.filename=filename
		self.db = sqlite3.connect(filename)
		cursor = self.db.cursor()
		cursor.execute('''
		    SELECT name FROM sqlite_master WHERE type='table' AND name='users';
		''')
		table = cursor.fetchone()
		if table is None:
			self.initialize_database()

	def initialize_database(self):
		cursor = self.db.cursor()
		cursor.execute('''
			CREATE TABLE users(id INTEGER PRIMARY KEY,
					   chatId TEXT,
					   rate_limited BOOLEAN,
					   twitter_username TEXT);
		''')
		cursor.execute('''
			CREATE TABLE subscriptions(chatId TEXT,
						   instrument TEXT,
						   FOREIGN KEY(chatId) REFERENCES users(chatId));
		''')
		cursor.execute('''
			CREATE TABLE signals(instrument TEXT,
					     data TEXT);
		''')
		self.db.commit()

	def add_user(self, chatId):
		cursor = self.db.cursor()
		cursor.execute('''INSERT INTO users(chatId, rate_limited, twitter_username)
                  VALUES(?,?,?)''', (chatId, True, ""))
		self.db.commit()

	def get_user(self,chatId):
		cursor = self.db.cursor()
		cursor.execute('''
			SELECT chatId, rate_limited, twitter_username FROM users WHERE chatId=?;
		''', (chatId,))
		user = cursor.fetchone()
		return user

	def add_user_if_not_exists(self,chatId):
		user = self.get_user(chatId)
		if user is None: self.add_user(chatId)

	def unlock_user(self,chatId):
		cursor = self.db.cursor()
		cursor.execute('''UPDATE users SET rate_limited = ? WHERE chatId = ? ''', (False, chatId))
		self.db.commit()

	def is_ratelimited(self,chatId):
		user = self.get_user(chatId)
		if user is None: return True
		return True if user[1] is 1 else False

	def is_subscribed(self,chatId,instrument):
		user = self.get_user(chatId)
		if user is None: return False
		cursor = self.db.cursor()
		cursor.execute('''SELECT * FROM subscriptions WHERE chatId = ? and instrument = ? ''', (chatId, instrument))
		subscription = cursor.fetchone()
		print("sub", subscription)
		if subscription is None:
			return False
		else:
			return True
		
	def subscribe_user(self,chatId,instrument):
		self.add_user_if_not_exists(chatId)
		cursor = self.db.cursor()
		cursor.execute('''INSERT INTO subscriptions(chatId, instrument)
                  		  VALUES(?,?)''', (chatId, instrument))
		self.db.commit()

	def usubscribe_user(self,chatId,instrument):
		cursor = self.db.cursor()
		cursor.execute(''' DELETE FROM subscriptions WHERE chatId = ? and instrument = ? ''',  (chatId, instrument))
		self.db.commit()

	def get_subscribed_users(self,instrument):
		cursor = self.db.cursor()
		cursor.execute('''SELECT users.chatId
				  FROM users INNER JOIN subscriptions ON users.chatId = subscriptions.chatId
				  WHERE subscriptions.instrument = ?''', (instrument,))
		subs = cursor.fetchall()
		print("Subscriptions:", subs)
		return subs
		
	def setTwitterUsername(self,chatId,username):
		user = self.get_user(chatId)
		if user is None: return
		cursor = self.db.cursor()
		cursor.execute('''UPDATE users SET twitter_username = ? WHERE chatId = ? ''', (username, chatId))
		self.db.commit()

	def getTwitterUsername(self,chatId):
		user = self.get_user(chatId)
		if user is None: return None
		return user[2]

	def getSignals(self):
		cursor = self.db.cursor()
		cursor.execute('''SELECT * FROM signals ''')
		signals = cursor.fetchall()	
		return signals

	def addSignal(self, instrument, data):
		cursor = self.db.cursor()
		cursor.execute('''INSERT INTO signals(instrument, data)
                  		  VALUES(?,?)''', (instrument, data))
		self.db.commit()

	def clearSignals(self):
		cursor = self.db.cursor()
		cursor.execute(''' DELETE FROM signals ''', ())
		self.db.commit()
