from __future__ import division

from constants import Screens

from numericentry_gui import NumericEntryGUI

class NumericEntry:

	def __init__(self, width, height, manager, owner):
		
		self.gui = NumericEntryGUI(width, height, self)	
		self.amountinpence = 0
		self.presetAmount = False
	
		self.ScreenManager = manager
		self.Owner = owner
		
	def draw(self, window):
		self.gui.draw(window)
	
	def OnGuiEvent(self, pos):
	
		button = self.gui.getObjectId(pos)
		
		if button >= self.gui.KEY0 and button <= self.gui.KEY9:
			#Let button press decide whether to play sound or not
			self.__newButtonPress(button)
		else:
			#Play sound unconditionally for other buttons
			self.gui.playSound()
			if button == self.gui.FIVEPOUNDS:
				self.presetAmount = True
				self.__setAmount(500)
			elif button == self.gui.TENPOUNDS:
				self.presetAmount = True
				self.__setAmount(1000)
			elif button == self.gui.TWENTYPOUNDS:
				self.presetAmount = True
				self.__setAmount(2000)
			elif button == self.gui.DONE:
				self.__creditAndExit()
			elif button == self.gui.CANCEL:
				self.__exit()
				
	def SetActive(self, state):
		self.acceptInput = state
	
	def OnScan(self, product):
		pass
			
	def OnBadScan(self, badcode):
		pass
	
	def OnKeyEvent(self, key):
		pass
	
	def OnRFID(self):
		pass
	
	def OnBadRFID(self):
		pass
	
	def __setAmount(self, amount):
		self.amountinpence = amount
		self.gui.updateAmount(self.amountinpence)
		self.ScreenManager.Req(Screens.NUMERICENTRY)
		
	def __newButtonPress(self, key):
		
		if self.presetAmount:
			## Clear the preset amount and assume starting from scratch
			self.presetAmount = False
			self.amountinpence = 0
			
		if ((self.amountinpence * 10) + key) <= 5000:
			
			self.gui.playSound()
		
			self.amountinpence *= 10
			self.amountinpence += key
		
			self.gui.updateAmount(self.amountinpence)
			self.ScreenManager.Req(Screens.NUMERICENTRY)
		
	def __creditAndExit(self):
		self.Owner.CreditUser(self.amountinpence)
		self.__exit()
		
	def __exit(self):
		self.__setAmount(0)
		self.ScreenManager.Req(Screens.MAINSCREEN)
		