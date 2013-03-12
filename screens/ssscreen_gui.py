import pygame

from threading import Timer

# # Safe wild import: all constants, all start with SS_
from ssdisplayconstants import *  # @UnusedWildImport

from lcarscappedbar import LCARSCappedBar, CapLocation

class SSScreenGUI:

	def __init__(self, w, h, owner):
		self.owner = owner
		self.w = w
		self.h = h
		self.lastPressId = -1
		self.acceptGUIEvents = True
		self.banner = None
		
		try:
			self.sound = pygame.mixer.Sound(SS_SOUNDFILE)
		except:
			raise
		
	def getObjectId(self, pos):
	
		# # Return the ID of the object clicked
		
		objectId = -1
		
		if self.acceptGUIEvents:
			for key, guiObject in self.objects.items():
				if guiObject.collidePoint(pos):
					objectId = key
					break
				
			if objectId > -1:
				self.lastPressId = objectId

		return objectId
	
	def playSound(self):
		self.sound.play()
		
	def SetBannerWithTimeout(self, text, timeout, colour, callback):
		
		try:
			self.timer.cancel()
		except:
			pass
		
		self.banner = LCARSCappedBar(pygame.Rect(self.w * 0.2, self.h / 2, self.w * 0.6, SS_LARGE_BAR),
			CapLocation.CAP_RIGHT + CapLocation.CAP_LEFT, text, colour, SS_BG , True)
		
		if timeout > 0:
			self.timer = Timer(timeout, callback)
			self.timer.start()

	def HideBanner(self, redrawnow = False):
		try:
			self.timer.cancel()
		except:
			pass
		self.banner = None

