import pygame
import inspect, os


## Safe wild import: all constants, all start with SS_
from ssdisplayconstants import * #@UnusedWildImport

from lcarsimage import LCARSImage
from lcarstext import LCARSText, TextAlign

from ssborder import SSBorder
from ssscreen_gui import SSScreenGUI

class SSIntroScreenGUI(SSScreenGUI):

	def __init__(self, width, height, owner):
		
		SSScreenGUI.__init__(self, width, height, owner)
		
		self.ssBorder = SSBorder(width, height)
		
		##
		## Fixed position objects
		##
		self.path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory
		self.objects = {
			'titleimage' : LCARSImage(pygame.Rect(width/2, height*3/5, 0, 0), self.path + "/hackspace_logo.png", True),
			}
		
		##
		## Import standard objects
		
		self.objects.update(self.ssBorder.getBorder());

		##
		## Position-dependant objects
		##
		
		self.setIntroText("Scan an item or swipe your card to start", SS_FG)
		self.setIntroText2("Don't have a card? Pop money in the pot instead!", SS_FG)
			
	def setIntroText(self, text, color):
		## The intro text is positioned centrally between the sweep and image
		textYPosition = (self.ssBorder.innerY() + self.objects['titleimage'].t()) / 2
		self.objects['introtext'] = LCARSText((self.w/2, textYPosition), 
			text,
			36,
			TextAlign.XALIGN_CENTRE, color, SS_BG, True)

	def setIntroText2(self, text, color):
		## The intro text is positioned between the image and the base
		textYPosition = (self.objects['titleimage'].b() + self.ssBorder.b()) / 2
		self.objects['introtext2'] = LCARSText((self.w/2, textYPosition), 
			text,
			36,
			TextAlign.XALIGN_CENTRE, color, SS_BG, True)
			
	def draw(self, window):
		window.fill(SS_BG)
	
		for drawObj in self.objects.values():
			drawObj.draw(window)
		
		#Ensure text is drawn on top
		self.objects['introtext'].draw(window)
		self.objects['introtext2'].draw(window)
		
		pygame.display.flip()
		
		
		