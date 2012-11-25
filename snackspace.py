import sys
import pygame

import time

from mydebug import debugPrint

from ssconstants import SSRequests, SSScreens

from ssuser import SSUser

from screens.ssintroscreen import SSIntroScreen
from screens.ssnumericentry import SSNumericEntry
from screens.ssmainscreen import SSMainScreen

class Snackspace:
	def __init__(self, window, size):
		
		self.inittime = int(time.time())
		
		self.window = window
		self.width = size[0]
		self.height = size[1]
	
		self.user = SSUser(self.userCallback)
		
		self.setConstants()
		
		self.setVariables()
		
		# Instantiate all the screens now
		self.screens = {
			SSScreens.INTROSCREEN.value		: SSIntroScreen(self.width, self.height, self.user, self.screenCallback),
			SSScreens.NUMERICENTRY.value	: SSNumericEntry(self.width, self.height, self.user, self.screenCallback),
			SSScreens.MAINSCREEN.value		: SSMainScreen(self.width, self.height, self.user, self.screenCallback)
			}

		self.currentscreen = SSScreens.BLANKSCREEN
		self.setScreen(SSScreens.INTROSCREEN, False)
	
	def startEventLoop(self):
		while (1):
			for event in pygame.event.get():
				if event.type == pygame.QUIT: sys.exit()
				if event.type == pygame.MOUSEBUTTONUP:
					try:
						self.screens[self.currentscreen.value].onGuiEvent(event.pos)
					except AttributeError:  # Screen does not handle Gui events
						if "onGuiEvent" in dir(self.screens[self.currentscreen.value]):
							raise  # # Only raise error if the onScanEvent method exists
				if event.type == pygame.KEYDOWN:
					self.inputHandler(event)

	def userCallback(self):
		for screen in self.screens.values():
			try:
				screen.onUserEvent(self.user)
			except AttributeError:
				if "onUserEvent" in dir(screen):
					raise  # # Only raise error if the onScanEvent method exists

	def inputHandler(self, event):
		if (event.key in self.validKeys):
			self.scannedinput += event.dict['unicode']
		elif (event.key == pygame.K_RETURN):
			if (self.scannedinput == "123"):
				self.onSwipeEvent(0)
			else:
				self.onScanEvent(self.scannedinput)
			
			self.scannedinput = ''
					
	def onSwipeEvent(self, cardnumber):
		if (self.user.isValid() == False):
			self.user.getUser(cardnumber)
				
	def onScanEvent(self, barcode):
		for screen in self.screens.values():
			try:
				screen.onScanEvent(barcode)
			except AttributeError:
				if "onScanEvent" in dir(screen):
					raise  # # Only raise error if the onScanEvent method exists
				
	def setScreen(self, newscreen, force):	
		if (newscreen.value != self.currentscreen.value or force):
			debugPrint("Changing screen from %s to %s" % (self.currentscreen.str, newscreen.str))
			self.currentscreen = newscreen
			self.screens[newscreen.value].draw(self.window)
				
	def setConstants(self):
		self.validKeys = [
			pygame.K_0, pygame.K_1,	pygame.K_2,	pygame.K_3, pygame.K_4,
			pygame.K_5,	pygame.K_6,	pygame.K_7,	pygame.K_8,	pygame.K_9
		]
	
	def setVariables(self):
		self.scannedinput = ''
		
	def screenCallback(self, currentscreenid, request, force):
		if request == SSRequests.MAIN:
			self.setScreen(SSScreens.MAINSCREEN, force)
		elif request == SSRequests.PAYMENT:
			self.setScreen(SSScreens.NUMERICENTRY, force)
		elif request == SSRequests.INTRO:
			self.setScreen(SSScreens.INTROSCREEN, force)
			
def main(argv=None):

	if argv is None:
		argv = sys.argv
		
	pygame.init()
	
	size = [800, 600]
	
	window = pygame.display.set_mode(size)
	
	s = Snackspace(window, size)
	s.startEventLoop()

if __name__ == "__main__":
	main();
