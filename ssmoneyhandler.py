class SSMoneyHandler:
	
	def __init__(self):
	
		self.valueinpence = 0
		
		self.callbacks = {
			'addAmount':self.addAmount,
			'removeAmount':self.removeAmount
		}
	
	def getCallbacks(self):
		return self.callbacks
		
	def setValue(self, valueinpence):
		self.value = value
		
	def getValue(self):
		return self.valueinpence
		
	def addAmount(self, e):
		self.valueinpence += e
		
	def removeAmount(self, e):
		self.valueinpence -= e
		