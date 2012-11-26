import pygame

## Safe wild import: all constants, all start with SS_
from ssdisplayconstants import * #@UnusedWildImport

class SSScreenGUI:

	def __init__(self, w, h, owner):
		self.owner = owner
		self.w = w
		self.h = h
		self.lastPressId = -1
		try:
			self.sound = pygame.mixer.Sound(SS_SOUNDFILE)
		except:
			raise
	def getObjectId(self, pos):
	
		# # Return the ID of the object clicked
	
		objectId = -1
		for key, guiObject in self.objects.items():
			if guiObject.collidePoint(pos):
				objectId = key
				break
			
		if objectId > -1:
			self.lastPressId = objectId
		return objectId
	
	def playSound(self):
		self.sound.play()
