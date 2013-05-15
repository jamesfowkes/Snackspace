from __future__ import division

from constants import Requests, Screens

from productentry_gui import ProductEntryGUI

class ProductEntry:

    def __init__(self, width, height, screenFuncs, productFuncs):
        
        self.gui = ProductEntryGUI(width, height, self)    
        self.amountinpence = 0
        self.presetAmount = False
    
        self.ScreenFuncs = screenFuncs
        self.ProductFuncs = productFuncs
        
    def draw(self, window):
        self.gui.draw(window)
    
    def OnGuiEvent(self, pos, _modifiers):
    
        button = self.gui.getObjectId(pos)
        
        if button == self.gui.CANCEL:
            self.__exit()
        
    def __exit(self):
        #self.ProductFuncs.__NewProducts__(self.productlist)
        #self.productlist = []
        self.ScreenFuncs.RequestScreen(Screens.NUMERICENTRY, Requests.INTRO, False)
        