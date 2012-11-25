
from ssconstants import SSRequests, SSScreens
from ssintroscreen_gui import SSIntroScreenGUI

class SSIntroScreen:

	def __init__(self, width, height, user, callback):
		
		self.gui = SSIntroScreenGUI(width, height, self)
		self.user = user
		
		self.SSCallback = callback
		
	def draw(self, window):
		self.gui.draw(window)
		
	def onSwipeEvent(self, cardnumber):
		self.SSCallback(SSScreens.INTROSCREEN, SSRequests.MAIN, False)
		
	def onScanEvent(self, barcode):
		self.SSCallback(SSScreens.INTROSCREEN, SSRequests.MAIN, False)