class SSScreenGUI:

	def __init__(self, w, h, owner):
		self.owner = owner
		self.w = w
		self.h = h
		self.lastPressId = -1
		
	def getObjectId(self, pos):
	
		## Return the ID of the object clicked
	
		objectId = -1
		for key, guiObject in self.objects.items():
			if guiObject.collidePoint(pos):
				objectId = key
				break
			
		if objectId > -1:
			self.lastPressId = objectId
		return objectId