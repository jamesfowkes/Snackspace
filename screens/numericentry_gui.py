from __future__ import division

import pygame

## Safe wild import: all constants
from displayconstants import * #@UnusedWildImport

from LCARSGui import LCARSCappedBar, CapLocation

from border import Border
from screen_gui import ScreenGUI

class NumericEntryGUI(ScreenGUI):

	def __init__(self, width, height, owner):
		
		ScreenGUI.__init__(self, width, height, owner)
		
		border = Border(width, height)
		
		self.setConstants()
		
		##
		## Fixed position objects
		##
		
		buttonw = 100
		largebuttonw = buttonw * 2
		amountentryw = (buttonw * 4) + (BORDER_W * 4)
		
		c1x = 200
		c2x = c1x + buttonw + BORDER_W
		c3x = c2x + buttonw + BORDER_W		
		c4x = c3x + buttonw + BORDER_W + BORDER_W
		buttonh = 50
		amountentryh = buttonh * 1.5
		
		r1y = 125
		r2y = r1y + amountentryh + BORDER_W
		r3y = r2y + buttonh + BORDER_W
		r4y = r3y + buttonh + BORDER_W
		r5y = r4y + buttonh + BORDER_W
		r6y = r5y + buttonh + BORDER_W
		
		cancelbuttonx = c4x + buttonw - largebuttonw #Right align the "cancel" button
		
		self.objects = {
			self.AMOUNT : LCARSCappedBar(pygame.Rect(c1x, r1y, amountentryw, amountentryh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "\xA30.00", RGB_FG, RGB_BG, True),
		
			self.KEY0 : LCARSCappedBar(pygame.Rect(c1x, r5y, buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "0", RGB_FG, RGB_BG, True),
			self.KEY1 : LCARSCappedBar(pygame.Rect(c1x, r4y, buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "1", RGB_FG, RGB_BG, True),
			self.KEY2 : LCARSCappedBar(pygame.Rect(c2x, r4y, buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "2", RGB_FG, RGB_BG, True),
			self.KEY3 : LCARSCappedBar(pygame.Rect(c3x, r4y, buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "3", RGB_FG, RGB_BG, True),
			self.KEY4 : LCARSCappedBar(pygame.Rect(c1x, r3y, buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "4", RGB_FG, RGB_BG, True),
			self.KEY5 : LCARSCappedBar(pygame.Rect(c2x, r3y, buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "5", RGB_FG, RGB_BG, True),
			self.KEY6 : LCARSCappedBar(pygame.Rect(c3x, r3y, buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "6", RGB_FG, RGB_BG, True),
			self.KEY7 : LCARSCappedBar(pygame.Rect(c1x, r2y, buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "7", RGB_FG, RGB_BG, True),
			self.KEY8 : LCARSCappedBar(pygame.Rect(c2x, r2y, buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "8", RGB_FG, RGB_BG, True),
			self.KEY9 : LCARSCappedBar(pygame.Rect(c3x, r2y, buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "9", RGB_FG, RGB_BG, True),
			
			self.FIVEPOUNDS :	LCARSCappedBar(pygame.Rect(c4x, r2y, buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, u"\xA35", RGB_FG, RGB_BG, True),
			self.TENPOUNDS :	LCARSCappedBar(pygame.Rect(c4x, r3y, buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, u"\xA310", RGB_FG, RGB_BG, True),
			self.TWENTYPOUNDS :	LCARSCappedBar(pygame.Rect(c4x, r4y, buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, u"\xA320", RGB_FG, RGB_BG, True),
			
			self.DONE : LCARSCappedBar(pygame.Rect(c1x, r6y, largebuttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "Done", RGB_FG, RGB_BG, True),
			self.CANCEL : LCARSCappedBar(pygame.Rect(cancelbuttonx, r6y, largebuttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "Cancel", RGB_FG, RGB_BG, True),
			}
		
		##
		## Import standard objects
		
		self.objects.update(border.getBorder());

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
		window.fill(RGB_BG)
	
		for guiObject in self.objects.values():
			guiObject.draw(window)
				
		pygame.display.flip()
