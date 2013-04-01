class Transaction:
	
	def __init__(self, user, description, amount):
		
		self.user = user
		self.description = description
		self.amount = amount
		
	@property
	def user(self):
		return self.user
		
	@property
	def description(self):
		return self.description
		
	@property
	def amount(self):
		return self.amount
