class SSItem:
		
	def __init__(self, dom, barcode):
		self.__valid = False
		self.description = ''
		self.priceinpence = 0
		self.count = 0
		
		self.dom = dom
		
		self.barcode = barcode

		items = self.dom.getElementsByTagName("item")
		
		for node in items:
			barcodeNode = node.getElementsByTagName("barcode").item(0).firstChild
			if barcodeNode.nodeValue == barcode:
				self.description = node.getElementsByTagName("description").item(0).firstChild.nodeValue
				self.priceinpence = int( node.getElementsByTagName("priceinpence").item(0).firstChild.nodeValue )
				self.count = 1
				self.__valid = True
						
	def increment(self):
		if (self.__valid):
			self.count += 1

	def decrement(self):
		if (self.__valid):
			if self.count > 1:
				self.count -= 1	
	
	def isValid(self):
		return self.__valid
	def totalPrice(self):
		return self.count * self.priceinpence