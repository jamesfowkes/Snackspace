## Safe wild import: all constants
from displayconstants import * #@UnusedWildImport

from constants import Screens
from introscreen_gui import IntroScreenGUI

class IntroScreen:

	def __init__(self, width, height, manager, owner):
		
		self.ScreenManager = manager
		self.Owner = owner
		
		self.active = False
		
		self.gui = IntroScreenGUI(width, height, self)
	
	def SetActive(self, state):
		self.active = state
		
	def draw(self, window):
		self.gui.draw(window)
	
	def OnRFID(self):
		if self.active:
			self.ScreenManager.Req(Screens.MAINSCREEN)
	
	def OnGuiEvent(self, pos):
		pass
	
	def OnKeyEvent(self, key):
		pass
	
	def OnScan(self, product):
		
		if self.active:
			self.ScreenManager.Req(Screens.MAINSCREEN)
	
	def OnBadScan(self, barcode):
		
		if self.active:
			self.ScreenManager.Req(Screens.MAINSCREEN)
			
	def SetDbState(self, dbConnected):
		if not dbConnected:
			self.gui.setIntroText("ERROR: Cannot access Snackspace remote database", RGB_ERROR_FG)
		else:
			self.gui.setIntroText("Scan an item or swipe your card to start", RGB_FG)