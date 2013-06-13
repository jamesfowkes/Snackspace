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
        
        minx = border.innerX() + 4*BORDER_W
        maxx = width - BORDER_W
        miny = border.innerY() + 4*BORDER_W
        maxy = height - BORDER_W
        
        buttonh = 50
        buttonw = 100
        
        fullwidth = maxx - minx
        
        self.defaultText = {
			self.BARCODE : "1. Scan an item",
			self.DESCRIPTION : "2. Type a description",
			self.PRICE : "3. Set a price",
			}
        
        self.objects = {
            self.BARCODE        : LCARSCappedBar(pygame.Rect(minx, miny, fullwidth, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "1. Scan an item", RGB_ENTRY_FG, RGB_BG, True),
            self.DESCRIPTION    : LCARSCappedBar(pygame.Rect(minx, miny + (2*buttonh), fullwidth, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "2. Type a description", RGB_ERROR_FG, RGB_BG, True),
            self.PRICE          : LCARSCappedBar(pygame.Rect(minx, miny + (4*buttonh), fullwidth, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "3. Set a price", RGB_ERROR_FG, RGB_BG, True),
            self.DONE           : LCARSCappedBar(pygame.Rect(minx, maxy-buttonh, buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "Done", RGB_FG, RGB_BG, True),
            self.CANCEL         : LCARSCappedBar(pygame.Rect(maxx - buttonw, maxy-buttonh, buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "Cancel", RGB_FG, RGB_BG, True),
        }
        
        ##
        ## Import standard objects
        ##
        self.objects.update(border.getBorder());

        ##
        ## Position-dependant objects
        ##
    
    def SetActiveEntry(self, entry):

        for key, guiObject in self.objects.iteritems():
            if key == entry:
                guiObject.fg = RGB_ENTRY_FG
                guiObject.setText("")
            else:
                if key in [self.BARCODE, self.DESCRIPTION, self.PRICE]:
                    if (len(guiObject.getText()) == 0) or (guiObject.getText() == self.defaultText[key]):
                        #No entry in this box. Set error colour
                        guiObject.fg = RGB_ERROR_FG
                        guiObject.setText(self.defaultText[key])
                    else:
                        guiObject.fg = RGB_FG
                        guiObject.setText(guiObject.getText()) #Forces colour update

    def ChangeBarcode(self, barcode):
        self.objects[self.BARCODE].setText(barcode)
   
    def ChangeDescription(self, description):
        self.objects[self.DESCRIPTION].setText(description) 

    def ChangePrice(self, priceinpence):
        self.objects[self.PRICE].setText("\xA3%.2f" % (priceinpence / 100)) 
                    
    def setConstants(self):
        # Object constant definitions
        self.BARCODE = 0
        self.DESCRIPTION = 1
        self.PRICE = 2
        self.DONE = 3
        self.CANCEL = 4
                
    def draw(self, window):
        window.fill(RGB_BG)
    
        for guiObject in self.objects.values():
            guiObject.draw(window)
            
        if self.banner is not None:
            self.banner.draw(window)

        pygame.display.flip()
