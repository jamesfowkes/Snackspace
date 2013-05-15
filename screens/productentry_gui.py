from __future__ import division

import pygame #@UnresolvedImport

## Safe wild import: all constants
from displayconstants import * #@UnusedWildImport

from LCARSGui import LCARSCappedBar, CapLocation

from border import Border
from screen_gui import ScreenGUI

class ProductEntryGUI(ScreenGUI):

    def __init__(self, width, height, owner):
        
        ScreenGUI.__init__(self, width, height, owner)
        
        border = Border(width, height)
        
        self.setConstants()
        
        ##
        ## Fixed position objects
        ##
        
        minx = border.innerX() + BORDER_W
        maxx = width - BORDER_W
        miny = border.innerY() + BORDER_W
        maxy = height - BORDER_W
        
        buttonh = 50
        buttonw = 100
        
        fullwidth = maxx - minx
        
        self.objects = {
            self.TEXTENTRY : LCARSCappedBar(pygame.Rect(minx, miny, fullwidth, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "Scan an item", RGB_FG, RGB_BG, True),
            self.DONE : LCARSCappedBar(pygame.Rect(minx, maxy-buttonh, buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "Done", RGB_FG, RGB_BG, True),
            self.CANCEL : LCARSCappedBar(pygame.Rect(maxx - buttonw, maxy-buttonh, buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "Cancel", RGB_FG, RGB_BG, True),
        }
        
        ##
        ## Import standard objects
        
        self.objects.update(border.getBorder());

        ##
        ## Position-dependant objects
        ##
    
    def setConstants(self):
        # Object constant definitions
        self.TEXTENTRY = 0
        self.DONE = 1
        self.CANCEL = 2
                
    def draw(self, window):
        window.fill(RGB_BG)
    
        for guiObject in self.objects.values():
            guiObject.draw(window)
                
        pygame.display.flip()
