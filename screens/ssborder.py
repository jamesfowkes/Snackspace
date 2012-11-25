import pygame

## Safe wild import: all constants, all start with SS_
from ssdisplayconstants import *

from lcarsgui.lcarstext import LCARSText, TextAlign
from lcarsgui.lcarstlsweep import LCARSTLSweep
from lcarsgui.lcarscappedbar import LCARSCappedBar, CapLocation

##
## Standard Border for all Snackspace LCARS screens
##

class SSBorder:

	def __init__(self, width, height):
		
		self.setConstants()
		
		cappedBarLength = width / 16
		sweepEndY = height - SS_BORDER		
		sweepHeight = sweepEndY - SS_BORDER
		
		self.objects = {
			self.ENDCAP : LCARSCappedBar(pygame.Rect(width - SS_BORDER - cappedBarLength, SS_BORDER, cappedBarLength, SS_LARGE_BAR), 
						CapLocation.CAP_RIGHT, '', SS_FG, SS_BG, True)
			}
			
		## The title text is to the immediate left of the endcap
		textRight = self.objects[self.ENDCAP].l() - SS_BORDER
		self.objects[self.TEXT] = LCARSText((textRight, SS_BORDER + SS_LARGE_BAR/2),
			"SNACKSPACE v1.0",
			80,
			TextAlign.XALIGN_RIGHT, SS_FG, SS_BG, True)

		## The sweep starts at the immediate left of the text
		sweepEndX = self.objects[self.TEXT].l() - SS_BORDER
		sweepWidth = sweepEndX - SS_BORDER

		self.objects[self.SWEEP] = LCARSTLSweep(
			pygame.Rect(SS_BORDER, SS_BORDER, sweepWidth, sweepHeight), SS_SMALL_BAR, SS_LARGE_BAR, SS_FG, SS_BG, True)

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
		
	def getBorder(self):
		return self.objects
