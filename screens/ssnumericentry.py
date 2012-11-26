from __future__ import division

from ssconstants import SSRequests, SSScreens

from ssnumericentry_gui import SSNumericEntryGUI

class SSNumericEntry:

	def __init__(self, width, height, user, callback):
		
		self.gui = SSNumericEntryGUI(width, height, self)
		self.SSCallback = callback
		
		self.user = user
		
		self.amountinpence = 0
		
	def draw(self, window):
		self.gui.draw(window)
	
	def onGuiEvent(self, pos):
	
		button = self.gui.getObjectId(pos)
		
		if button >= self.gui.KEY0 and button <= self.gui.KEY9:
			#Let button press decide whether to play sound or not
			self.newButtonPress(button)
		else:
			#Play sound unconditionally for other buttons
			self.gui.playSound()
			if button == self.gui.FIVEPOUNDS:
				self.setAmount(500)
			elif button == self.gui.TENPOUNDS:
				self.setAmount(1000)
			elif button == self.gui.TWENTYPOUNDS:
				self.setAmount(2000)
			elif button == self.gui.DONE:
				self.chargeAndExit()
			elif button == self.gui.CANCEL:
				self.exit()

	def setAmount(self, amount):
		self.amountinpence = amount
		self.gui.updateAmount(self.amountinpence)
		self.SSCallback(SSScreens.NUMERICENTRY, SSRequests.PAYMENT, True)
		
	def newButtonPress(self, key):
		
		if ((self.amountinpence * 10) + key) <= 5000:
			
			self.gui.playSound()
		
			self.amountinpence *= 10
			self.amountinpence += key
		
			self.gui.updateAmount(self.amountinpence)
			self.SSCallback(SSScreens.NUMERICENTRY, SSRequests.PAYMENT, True)
		
	def chargeAndExit(self):
		self.user.charge(-self.amountinpence)
		self.exit()
		
	def exit(self):
		self.setAmount(0)
		self.SSCallback(SSScreens.NUMERICENTRY, SSRequests.MAIN, False)
		