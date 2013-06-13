import pygame

from threading import Timer

# # Safe wild import: all constants
from displayconstants import *  # @UnusedWildImport

from LCARSGui import LCARSCappedBar, CapLocation

class ScreenGUI:

	def __init__(self, w, h, owner):
		self.owner = owner
		self.w = w
		self.h = h
		self.lastPressId = -1
		self.active = True
		self.banner = None
		
		try:
			pass #self.sound = pygame.mixer.Sound(SOUNDFILE)
		except:
			raise
		
	def getObjectId(self, pos):
	
		# # Return the ID of the object clicked
		
		objectId = -1
		
		if self.active:
			for key, guiObject in self.objects.items():
				if guiObject.collidePoint(pos) and guiObject.visible:
					objectId = key
					break
				
			if objectId > -1:
				self.lastPressId = objectId

		return objectId
	
	def playSound(self):
		pass #self.sound.play()
		
	def SetBannerWithTimeout(self, text, timeout, colour, callback, widthFraction = 0.6):
		
		try:
			self.timer.cancel()
		except:
			pass
		
		x = self.w * (1 - widthFraction) / 2
		width = self.w * widthFraction
		self.banner = LCARSCappedBar(pygame.Rect(x, self.h / 2, width , LARGE_BAR_W),
			CapLocation.CAP_RIGHT + CapLocation.CAP_LEFT, text, colour, RGB_BG , True)
		
		if timeout > 0:
			self.timer = Timer(timeout, callback)
			self.timer.start()

	def HideBanner(self):
		try:
			self.timer.cancel()
		except:
			pass
		self.banner = None

