"""
introscreen_gui.py
"""

import pygame #@UnresolvedImport
import inspect, os

from screens.displayconstants import Colours

from LCARSGui import LCARSImage, LCARSText, TextAlign

from screens.border import Border
from screens.screen_gui import ScreenGUI

if pygame.image.get_extended() != 0:
    LOGO_PATH = "/hackspace_logo.png"
else:
    LOGO_PATH = "/hackspace_logo.bmp"

class IntroScreenGUI(ScreenGUI):

    """ Describes the graphical elements of the intro screen and
    provides methods for setting introduction text """
    
    def __init__(self, width, height, owner):

        ScreenGUI.__init__(self, width, height, owner)

        self.border = Border(width, height)

        ##
        ## Fixed position objects
        ##
        self.path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory
        self.objects = {
                'titleimage' : LCARSImage(pygame.Rect(width/2, height*3/5, 0, 0), self.path + LOGO_PATH, True),
                }

        ##
        ## Import standard objects

        self.objects.update(self.border.get_border())

        ##
        ## Position-dependant objects
        ##

        self.set_intro_text("Searching for remote database...", Colours.FG)
        self.set_intro_text_2("Don't have a card? Seeing error messages?", Colours.FG)
        self.set_intro_text_3("Pop money in the pot instead!", Colours.FG)

    def set_intro_text(self, text, color):
        """ The intro text is positioned centrally between the sweep and image """
        text_y_position = (self.border.inner_y() + self.objects['titleimage'].t()) / 2
        self.objects['introtext'] = LCARSText((self.width/2, text_y_position),
                text,
                36,
                TextAlign.XALIGN_CENTRE, color, Colours.BG, True)

    def set_intro_text_2(self, text, color):
        """ The intro text is positioned between the image and the base """
        text_y_position = (self.objects['titleimage'].b() + self.border.bottom()) / 2
        self.objects['introtext2'] = LCARSText((self.width/2, text_y_position),
                text,
                36,
                TextAlign.XALIGN_CENTRE, color, Colours.BG, True)

    def set_intro_text_3(self, text, color):
        """ The intro text is positioned between the image and the base """
        text_y_position = self.objects['introtext2'].t() + 50
        self.objects['introtext3'] = LCARSText((self.width/2, text_y_position),
                text,
                36,
                TextAlign.XALIGN_CENTRE, color, Colours.BG, True)

    def draw(self, window):
        
        """ Draw the screen objects on the supplied window """
        
        window.fill(Colours.BG)

        for draw_obj in self.objects.values():
            draw_obj.draw(window)

        #Ensure text is drawn on top
        self.objects['introtext'].draw(window)
        self.objects['introtext2'].draw(window)
        self.objects['introtext3'].draw(window)
        
        if self.banner is not None:
            self.banner.draw(window)
            
        pygame.display.flip()
