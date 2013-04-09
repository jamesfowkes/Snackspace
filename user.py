class User:
	
	
	def __init__(self, member_id, username, balance, limit, limitAction, allowCredit):
		
		self.__name = username
		self.__balance = int(balance)
		self.__limit = int(limit)
		self.__memberID = member_id
		self.__limitAction = limitAction
		self.__allowCredit = allowCredit
		
		## Keep credit added recorded separately from balance.
		## This way, balance will not be updated until payments have been processed,
		## but the user can be prevented from adding too much credit (configuration dependent)   
		self.__creditAdded = 0
		
	## Transaction allowed return values
	XACTION_ALLOWED = 0
	XACTION_OVERLIMIT = 1
	XACTION_DENIED = 2
		
	def TransactionAllowed(self, priceinpence):
	
		overLimit = (self.__balance - priceinpence < self.__limit) 	
		transactionState = self.XACTION_ALLOWED
		
		if overLimit:
			if self.__limitAction == 'warn':
				transactionState = self.XACTION_OVERLIMIT
			elif self.__limitAction == 'deny':
				transactionState = self.XACTION_DENIED
		
		return transactionState
	
	def creditAllowed(self):
		
		if self.__allowCredit == 'always':
			creditAllowed = True
		elif self.__allowCredit == 'whenindebt':
			if (self.__balance + self.__creditAdded) < 0:
				creditAllowed = True
			else:
				creditAllowed = False
		elif self.__allowCredit == 'disallow':
			creditAllowed = False
			
		return creditAllowed
	
	def addCredit(self, amount):
		self.__creditAdded += amount
		
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
	def MemberID(self):
		return self.__memberID