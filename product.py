class Product:
		
	def __init__(self, barcode, description, priceinpence):
		self.__valid = False
		self.__description = ''
		self.__priceinpence = 0
		self.__count = 0
		
		self.__barcode = barcode
		self.__description = description
		self.__priceinpence = int(priceinpence)
		self.__count = 1
		self.__valid = True
						
	def Increment(self):
		if (self.__valid):
			self.__count += 1

	def Decrement(self):
		if (self.__valid):
			if self.__count > 0:
				self.__count -= 1	
		
		return self.__count
	
	@property
	def Valid(self):
		return self.__valid
		
	@property
	def Count(self):
		return self.__count
	
	@property	
	def PriceEach(self):
		return self.__priceinpence
	
	@property	
	def TotalPrice(self):
		return self.__count * self.__priceinpence
	
	@property
	def Barcode(self):
		return self.__barcode
	
	@property	
	def Description(self):
		return self.__description