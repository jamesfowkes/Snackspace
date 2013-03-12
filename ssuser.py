class SSUser:
	
	def __init__(self, rfid, username, balance, limit):
		
		self.__name = username
		self.__balance = int(balance)
		self.__limit = int(limit)
		self.__rfid = rfid
	##
	## Property getters
	##
	@property
	def Name(self):
		return self.__name
	
	@property
	def Balance(self):
		return self.__balance
	
	@property
	def Limit(self):
		return self.__limit
	
	@property
	def RFID(self):
		return self.__rfid