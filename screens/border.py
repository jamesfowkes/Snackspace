import pygame

## Safe wild import: all constants
from displayconstants import * #@UnusedWildImport

from LCARSGui import LCARSText, TextAlign, LCARSSweep, LCARSCappedBar, CapLocation

##
## Standard Border for all Snackspace LCARS screens
##

class Border:

	def __init__(self, width, height):
		
		self.setConstants()
		
		cappedBarLength = width / 16
		sweepEndY = height - BORDER_W		
		sweepHeight = sweepEndY - BORDER_W
		
		self.objects = {
			self.ENDCAP : LCARSCappedBar(pygame.Rect(width - BORDER_W - cappedBarLength, BORDER_W, cappedBarLength, LARGE_BAR_W), 
						CapLocation.CAP_RIGHT, '', RGB_FG, RGB_BG, True)
			}
			
		## The title text is to the immediate left of the endcap
		textRight = self.objects[self.ENDCAP].l() - BORDER_W
		self.objects[self.TEXT] = LCARSText((textRight, BORDER_W + LARGE_BAR_W/2),
			"SNACKSPACE v1.0",
			80,
			TextAlign.XALIGN_RIGHT, RGB_FG, RGB_BG, True)

		## The sweep starts at the immediate left of the text
		sweepEndX = self.objects[self.TEXT].l() - BORDER_W
		sweepWidth = sweepEndX - BORDER_W

		self.objects[self.SWEEP] = LCARSSweep(
			pygame.Rect(BORDER_W, BORDER_W, sweepWidth, sweepHeight), 'TL', SMALL_BAR_W, LARGE_BAR_W, RGB_FG, RGB_BG, True)

	def setConstants(self):
		# Object constant definitions
		# Assume all other dictionary keys are +ve
		self.ENDCAP = -1
		self.TEXT = -2
		self.SWEEP = -3
		
	def innerY(self):
		return self.objects[self.ENDCAP].b()
	
	def innerX(self):
		return self.objects[self.SWEEP].l()
	
	def b(self):
		return self.objects[self.SWEEP].b()
	
	def getBorder(self):
		return self.objects
