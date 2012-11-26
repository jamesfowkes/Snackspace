class Constant:
	
	def __init__(self, strId, value):
		self.__value__ = value
		self.__str__ = strId

	@property
	def value(self):
		return self.__value__
	
	@property	
	def str(self):
		return self.__str__
		
class SSRequests:
	INTRO = Constant("INTRO", 0)
	MAIN = Constant("MAIN", 1)
	PAYMENT = Constant("PAYMENT", 2)
	
class SSScreens:
	
	BLANKSCREEN = Constant("BLANKSCREEN", -1)
	INTROSCREEN = Constant("INTROSCREEN", 0)
	MAINSCREEN = Constant("MAINSCREEN", 1)
	NUMERICENTRY = Constant("NUMERICENTRY", 2)
	WAITING = Constant("WAITING", 3)
	
class SSData:
	ItemsFile = Constant("Item Filename", "items/items.xml")
	