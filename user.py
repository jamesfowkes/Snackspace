class User:
	
	def __init__(self, member_id, username, balance, limit):
		
		self.__name = username
		self.__balance = int(balance)
		self.__limit = int(limit)
		self.__memberID = member_id
		
	def TransactionAllowed(self, priceinpence):
		return ((self.__balance - self.__limit) > priceinpence)
	
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