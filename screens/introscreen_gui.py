import pygame #@UnresolvedImport
import inspect, os


## Safe wild import: all constants
from displayconstants import * #@UnusedWildImport

from LCARSGui import LCARSImage, LCARSText, TextAlign

from border import Border
from screen_gui import ScreenGUI

if pygame.image.get_extended() != 0:
	logo_path = "/hackspace_logo.png"
else:
	logo_path = "/hackspace_logo.bmp"
	
class IntroScreenGUI(ScreenGUI):

	def __init__(self, width, height, owner):
		
		ScreenGUI.__init__(self, width, height, owner)
		
		self.border = Border(width, height)
		
		##
		## Fixed position objects
		##
		self.path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory
		self.objects = {
			'titleimage' : LCARSImage(pygame.Rect(width/2, height*3/5, 0, 0), self.path + logo_path, True),
			}
		
		##
		## Import standard objects
		
		self.objects.update(self.border.getBorder());

		##
		## Position-dependant objects
		##
		
		self.setIntroText("Scan an item or swipe your card to start", RGB_FG)
		self.setIntroText2("Don't have a card? Seeing error messages?", RGB_FG)
		self.setIntroText3("Pop money in the pot instead!", RGB_FG)
		
	def setIntroText(self, text, color):
		## The intro text is positioned centrally between the sweep and image
		textYPosition = (self.border.innerY() + self.objects['titleimage'].t()) / 2
		self.objects['introtext'] = LCARSText((self.w/2, textYPosition), 
			text,
			36,
			TextAlign.XALIGN_CENTRE, color, RGB_BG, True)

	def setIntroText2(self, text, color):
		## The intro text is positioned between the image and the base
		textYPosition = (self.objects['titleimage'].b() + self.border.b()) / 2
		self.objects['introtext2'] = LCARSText((self.w/2, textYPosition), 
			text,
			36,
			TextAlign.XALIGN_CENTRE, color, RGB_BG, True)
		
	def setIntroText3(self, text, color):
		## The intro text is positioned between the image and the base
		textYPosition = self.objects['introtext2'].t() + 50
		self.objects['introtext3'] = LCARSText((self.w/2, textYPosition), 
			text,
			36,
			TextAlign.XALIGN_CENTRE, color, RGB_BG, True)
					
	def draw(self, window):
		window.fill(RGB_BG)
	
		for drawObj in self.objects.values():
			drawObj.draw(window)
		
		#Ensure text is drawn on top
		self.objects['introtext'].draw(window)
		self.objects['introtext2'].draw(window)
		self.objects['introtext3'].draw(window)
		
		pygame.display.flip()
		
		
		