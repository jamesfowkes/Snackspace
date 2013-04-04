
from constants import Requests, Screens
from introscreen_gui import IntroScreenGUI

class IntroScreen:

	def __init__(self, width, height, screenFuncs, userFuncs, productFuncs):
		
		self.ScreenFuncs = screenFuncs
		self.ProductFuncs = productFuncs
		self.UserFuncs = userFuncs
		
		self.gui = IntroScreenGUI(width, height, self)
		
	def draw(self, window):
		self.gui.draw(window)
		
	def onSwipeEvent(self, cardnumber):
		if self.acceptGUIEvents:
			self.ScreenFuncs.RequestScreen(Screens.INTROSCREEN, Requests.MAIN, False)
		
	def onScanEvent(self, barcode):
		
		if self.acceptGUIEvents:
			self.ScreenFuncs.RequestScreen(Screens.INTROSCREEN, Requests.MAIN, False)
		
	def setIntroText(self, text, color):
		self.gui.setIntroText(text, color)
