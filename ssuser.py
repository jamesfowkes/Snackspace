class SSUser:
	
	def __init__(self, username, balance, limit):
		
		self.__name = username
		self.__balance = int(balance)
		self.__limit = int(limit)
				
	def Charge(self, amountinpence, dbaccess):
		dbaccess.chargeUser(amountinpence)
		
	##
	## Property getters
	##
	def getName(self): return self.__name
	def getBalance(self): return self.__balance
	def getLimit(self): return self.__limit