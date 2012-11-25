import pygame

## Safe wild import: all constants, all start with SS_
from ssdisplayconstants import * #@UnusedWildImport

from lcarsgui.lcarsimage import LCARSImage
from lcarsgui.lcarstext import LCARSText, TextAlign

from ssborder import SSBorder
from ssscreen_gui import SSScreenGUI

class SSIntroScreenGUI(SSScreenGUI):

	def __init__(self, width, height, owner):
		
		SSScreenGUI.__init__(self, width, height, owner)
		
		ssBorder = SSBorder(width, height)
		
		##
		## Fixed position objects
		##
		
		self.objects = {
			'titleimage' : LCARSImage(pygame.Rect(width/2, height*3/5, 0, 0), "hackspace_logo.png", True),
			}
		
		##
		## Import standard objects
		
		self.objects.update(ssBorder.getBorder());

		##
		## Position-dependant objects
		##
		
		## The intro text is positioned centrally between the sweep and image
		textYPosition = (ssBorder.innerY() + self.objects['titleimage'].t()) / 2
		self.objects['introtext'] = LCARSText((width/2, textYPosition), 
			"Scan an item or swipe your card to start",
			36,
			TextAlign.XALIGN_CENTRE, SS_FG, SS_BG, True)
			
			
	def draw(self, window):
		window.fill(SS_BG)
	
		for drawObj in self.objects.values():
			drawObj.draw(window)
				
		pygame.display.flip()
		
		
		