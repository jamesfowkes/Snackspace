class User:
	
	
	def __init__(self, member_id, username, balance, limit, limitBehaviour):
		
		self.__name = username
		self.__balance = int(balance)
		self.__limit = int(limit)
		self.__memberID = member_id
		self.__limitBehaviour = limitBehaviour
	
	## Transaction allowed return values
	ALLOWED = 0
	OVERLIMIT = 1
	DENIED = 2
		
	def TransactionAllowed(self, priceinpence):
	
		overLimit = (self.__balance - priceinpence < self.__limit) 	
		transactionState = self.ALLOWED
		
		if overLimit:
			if self.__limitBehaviour == 'warn':
				transactionState = self.OVERLIMIT
			elif self.__limitBehaviour == 'deny':
				transactionState = self.DENIED
		
		return transactionState
	
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