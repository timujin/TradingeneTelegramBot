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
			CREATE TABLE users(id INTEGER PRIMARY KEY, chatId TEXT, rate_limited BOOLEAN);
		''')
		self.db.commit()

	def add_user(self, chatId):
		cursor = self.db.cursor()
		cursor.execute('''INSERT INTO users(chatId, rate_limited)
                  VALUES(?,?)''', (chatId, True))
		self.db.commit()

	def get_user(self,chatId):
		cursor = self.db.cursor()
		cursor.execute('''
			SELECT chatId, rate_limited FROM users WHERE chatId=?;
		''', (chatId,))
		user = cursor.fetchone()
		return user

	def add_user_if_not_exists(self,chatId):
		user = get_user(chatId)
		if user is None: self.add_user(chatId)

	def unlock_user(self,chatId):
		cursor = self.db.cursor()
		cursor.execute('''UPDATE users SET rate_limited = ? WHERE chatId = ? ''', (False, chatId))
		self.db.commit()

	def is_ratelimited(self,chatId):
		user = self.get_user(chatId)
		if user is None: return True
		return True if user[1] is 1 else False
