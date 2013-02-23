
from ssconstants import SSRequests, SSScreens
from ssintroscreen_gui import SSIntroScreenGUI

class SSIntroScreen:

	def __init__(self, width, height, screenFuncs, userFuncs, itemFuncs):
		
		self.ScreenFuncs = screenFuncs
		self.ItemFuncs = itemFuncs
		self.UserFuncs = userFuncs
		
		self.gui = SSIntroScreenGUI(width, height, self)
		
	def draw(self, window):
		self.gui.draw(window)
		
	def onSwipeEvent(self, cardnumber):
		if self.acceptGUIEvents:
			self.ScreenFuncs.RequestScreen(SSScreens.INTROSCREEN, SSRequests.MAIN, False)
		
	def onScanEvent(self, barcode):
		
		if self.acceptGUIEvents:
			self.ScreenFuncs.RequestScreen(SSScreens.INTROSCREEN, SSRequests.MAIN, False)
		
	def setIntroText(self, text, color):
		self.gui.setIntroText(text, color)
