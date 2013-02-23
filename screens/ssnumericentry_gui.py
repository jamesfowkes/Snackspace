from __future__ import division

import pygame

## Safe wild import: all constants, all start with SS_
from ssdisplayconstants import * #@UnusedWildImport

from lcarscappedbar import LCARSCappedBar, CapLocation

from ssborder import SSBorder
from ssscreen_gui import SSScreenGUI

class SSNumericEntryGUI(SSScreenGUI):

	def __init__(self, width, height, owner):
		
		SSScreenGUI.__init__(self, width, height, owner)
		
		ssBorder = SSBorder(width, height)
		
		self.setConstants()
		
		##
		## Fixed position objects
		##
		
		buttonw = 100
		largebuttonw = buttonw * 2
		amountentryw = (buttonw * 4) + (SS_BORDER * 4)
		
		c1x = 200
		c2x = c1x + buttonw + SS_BORDER
		c3x = c2x + buttonw + SS_BORDER		
		c4x = c3x + buttonw + SS_BORDER + SS_BORDER
		buttonh = 50
		amountentryh = buttonh * 1.5
		
		r1y = 125
		r2y = r1y + amountentryh + SS_BORDER
		r3y = r2y + buttonh + SS_BORDER
		r4y = r3y + buttonh + SS_BORDER
		r5y = r4y + buttonh + SS_BORDER
		r6y = r5y + buttonh + SS_BORDER
		
		cancelbuttonx = c4x + buttonw - largebuttonw #Right align the "cancel" button
		
		self.objects = {
			self.AMOUNT : LCARSCappedBar(pygame.Rect(c1x, r1y, amountentryw, amountentryh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "\xA30.00", SS_FG, SS_BG, True),
		
			self.KEY0 : LCARSCappedBar(pygame.Rect(c1x, r5y, buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "0", SS_FG, SS_BG, True),
			self.KEY1 : LCARSCappedBar(pygame.Rect(c1x, r4y, buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "1", SS_FG, SS_BG, True),
			self.KEY2 : LCARSCappedBar(pygame.Rect(c2x, r4y, buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "2", SS_FG, SS_BG, True),
			self.KEY3 : LCARSCappedBar(pygame.Rect(c3x, r4y, buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "3", SS_FG, SS_BG, True),
			self.KEY4 : LCARSCappedBar(pygame.Rect(c1x, r3y, buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "4", SS_FG, SS_BG, True),
			self.KEY5 : LCARSCappedBar(pygame.Rect(c2x, r3y, buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "5", SS_FG, SS_BG, True),
			self.KEY6 : LCARSCappedBar(pygame.Rect(c3x, r3y, buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "6", SS_FG, SS_BG, True),
			self.KEY7 : LCARSCappedBar(pygame.Rect(c1x, r2y, buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "7", SS_FG, SS_BG, True),
			self.KEY8 : LCARSCappedBar(pygame.Rect(c2x, r2y, buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "8", SS_FG, SS_BG, True),
			self.KEY9 : LCARSCappedBar(pygame.Rect(c3x, r2y, buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "9", SS_FG, SS_BG, True),
			
			self.FIVEPOUNDS :	LCARSCappedBar(pygame.Rect(c4x, r2y, buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, u"\xA35", SS_FG, SS_BG, True),
			self.TENPOUNDS :	LCARSCappedBar(pygame.Rect(c4x, r3y, buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, u"\xA310", SS_FG, SS_BG, True),
			self.TWENTYPOUNDS :	LCARSCappedBar(pygame.Rect(c4x, r4y, buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, u"\xA320", SS_FG, SS_BG, True),
			
			self.DONE : LCARSCappedBar(pygame.Rect(c1x, r6y, largebuttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "Done", SS_FG, SS_BG, True),
			self.CANCEL : LCARSCappedBar(pygame.Rect(cancelbuttonx, r6y, largebuttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "Cancel", SS_FG, SS_BG, True),
			}
		
		##
		## Import standard objects
		
		self.objects.update(ssBorder.getBorder());

		##
		## Position-dependant objects
		##
	
	def setConstants(self):
		# Object constant definitions
		self.KEY0 = 0
		self.KEY1 = 1
		self.KEY2 = 2
		self.KEY3 = 3
		self.KEY4 = 4
		self.KEY5 = 5
		self.KEY6 = 6
		self.KEY7 = 7
		self.KEY8 = 8
		self.KEY9 = 9
		self.FIVEPOUNDS = 10
		self.TENPOUNDS = 11
		self.TWENTYPOUNDS = 12
		self.DONE = 13
		self.CANCEL = 14
		self.AMOUNT = 15
			
	def updateAmount(self, amount):
		self.objects[self.AMOUNT].setText("\xA3%.2f" % (amount / 100))
			
	def draw(self, window):
		window.fill(SS_BG)
	
		for guiObject in self.objects.values():
			guiObject.draw(window)
				
		pygame.display.flip()
