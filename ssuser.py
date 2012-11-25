from ssdbaccess import SSDbAccess

class SSUser:
	
	def __init__(self, callback):
		self.__valid = False
		self.__callback = callback
		
		self.__dbHandle = SSDbAccess()
	
		self.__name = ''
		self.__balance = 0
		
	def getUser(self, swipeid):
		self.__swipeid = swipeid
		
		if (self.__dbHandle.isConnected()):
			self.__dbHandle.getUser(swipeid, self.dbCallback)
			
	def charge(self, amountinpence):
		
		if self.__valid:
			self.__dbHandle.chargeUser(amountinpence)
			self.__dbHandle.getUser(self.__swipeid, self.dbCallback)

	def forget(self):
		self.__valid = False
		self.__name = ''
		self.__balance = 0
		
	def dbCallback(self, success, usedId, name, balance):
		self.__valid = success
		
		if self.__valid:
			self.__id = usedId
			self.__name = name
			self.__balance = balance
		
		self.__callback()

	##
	## Property getters
	##
	def isValid(self): return self.__valid
	def getName(self): return self.__name
	def getBalance(self): return self.__balance