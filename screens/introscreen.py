## Safe wild import: all constants
from displayconstants import * #@UnusedWildImport

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
		
	def setDbState(self, dbConnected):
		if not dbConnected:
			self.gui.setIntroText("ERROR: Cannot access Snackspace remote database", RGB_ERROR_FG)
		else:
			self.gui.setIntroText("Scan an item or swipe your card to start", RGB_FG)