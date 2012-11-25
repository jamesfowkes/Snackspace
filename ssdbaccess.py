class SSDbAccess:

	def __init__(self):
		
		self.setVariables()
		
	def getUser(self, swipeid, callback):
	
		if (self.__callback is None):
			self.__callback = callback
		
		## Fake user DB access
		self.__callback(True, 4574, "James Fowkes", self.__testamount)
		self.__callback = None
	
	def chargeUser(self, amountinpence):
		self.__testamount -= amountinpence
		
	def setVariables(self):
	
		self.__connected = True
		self.__callback = None
		
		self.__testamount = -1000
		
	##
	## Property getters
	##
	def isConnected(self): return self.__connected

		