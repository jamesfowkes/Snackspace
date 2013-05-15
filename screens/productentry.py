from __future__ import division

import logging

from constants import Screens

# # Safe wild import: all constants
from displayconstants import *  # @UnusedWildImport

from productentry_gui import ProductEntryGUI

from SimpleStateMachine import SimpleStateMachine, SimpleStateMachineEntry

from enum import Enum

class ProductEntry:

    def __init__(self, width, height, screenFuncs, productFuncs):
        
        self.gui = ProductEntryGUI(width, height, self)    
    
        self.acceptInput = False
        
        self.ScreenFuncs = screenFuncs
        self.ProductFuncs = productFuncs
        
        self.states = Enum(["BARCODE", "DESCRIPTION", "PRICE", "ADDING", "WARNING"])
        self.events = Enum(["GUIEVENT", "SCAN", "BADSCAN", "KEYPRESS", "ADDED", "TIMEOUT"])
        
        self.SM = SimpleStateMachine(self.states.BARCODE,
        [        
            SimpleStateMachineEntry(self.states.BARCODE, self.events.GUIEVENT,      self.__onGuiEvent),
            SimpleStateMachineEntry(self.states.BARCODE, self.events.SCAN,          self.__gotBarcode),
            SimpleStateMachineEntry(self.states.BARCODE, self.events.BADSCAN,       self.__gotNewBarcode),
            SimpleStateMachineEntry(self.states.BARCODE, self.events.KEYPRESS,      lambda: self.states.BARCODE),
            
            SimpleStateMachineEntry(self.states.DESCRIPTION, self.events.GUIEVENT,  self.__onGuiEvent),
            SimpleStateMachineEntry(self.states.DESCRIPTION, self.events.KEYPRESS,  self.__gotNewBarcode),
            SimpleStateMachineEntry(self.states.DESCRIPTION, self.events.SCAN,      lambda: self.states.DESCRIPTION),
            SimpleStateMachineEntry(self.states.DESCRIPTION, self.events.BADSCAN,   lambda: self.states.DESCRIPTION),
            
            SimpleStateMachineEntry(self.states.PRICE, self.events.GUIEVENT,        self.__onGuiEvent),
            SimpleStateMachineEntry(self.states.PRICE, self.events.KEYPRESS,        self.__gotNewBarcode),
            SimpleStateMachineEntry(self.states.PRICE, self.events.SCAN,            lambda: self.states.DESCRIPTION),
            SimpleStateMachineEntry(self.states.PRICE, self.events.BADSCAN,         lambda: self.states.DESCRIPTION),
            
            SimpleStateMachineEntry(self.states.ADDING, self.events.ADDED,          lambda: self.states.BARCODE),
            
            SimpleStateMachineEntry(self.states.WARNING, self.events.TIMEOUT,       lambda: self.states.BARCODE),
        ])
        
        self.logger = logging.getLogger("ProductEntry")
        
    def setActive(self, state):
        self.acceptInput = state
    
    def OnKeyPress(self, char):
        self.lastChar = char
        self.SM.onStateEvent(self.events.GUIEVENT)
        
    def OnGuiEvent(self, pos):
        if self.acceptInput:
            self.lastGuiPosition = pos
            self.SM.onStateEvent(self.events.GUIEVENT)
               
    def __onGuiEvent(self):
    
        pos = self.lastGuiPosition
        button = self.gui.getObjectId(pos)
               
        if button == self.gui.BARCODE:
            self.gui.SetActiveEntry(self.gui.BARCODE)
            self.__requestRedraw()
            return self.states.BARCODE
        
        if button == self.gui.DESCRIPTION:
            self.gui.SetActiveEntry(self.gui.DESCRIPTION)
            self.__requestRedraw()
            return self.states.DESCRIPTION
        
        if button == self.gui.PRICE:
            self.gui.SetActiveEntry(self.gui.PRICE)
            self.__requestRedraw()
            return self.states.PRICE
        
        if button == self.gui.DONE:
            self._addProduct()
            return self.states.ADDING
        
        if button == self.gui.CANCEL:
            self.__quit()
            return self.states.BARCODE
        
    def __gotNewBarcode(self):
        self.gui.ChangeBarcode(self.barcode)
        self.__requestRedraw()
        return self.states.BARCODE
    
    def __gotBarcode(self):
        self.gui.SetBannerWithTimeout("Barcode already exists!", 4, RGB_WARNING_FG, self.__bannerTimeout)
        self.__requestRedraw()
        return self.states.WARNING
        
    def OnScan(self, product, barcode):
        if self.acceptInput:
            if product is None:
                self.barcode = barcode
                self.SM.onStateEvent(self.events.BADSCAN)
            else:
                self.SM.onStateEvent(self.events.SCAN)

    def __bannerTimeout(self):
        self.gui.HideBanner()
        self.__requestRedraw()
        self.SM.onStateEvent(self.events.TIMEOUT)
    
    def __requestRedraw(self):
        self.ScreenFuncs.RequestScreen(Screens.PRODUCTENTRY)
        
    def draw(self, window):
        self.logger.info("Drawing self")
        self.gui.draw(window)
        
    def __exit(self):
        #self.ProductFuncs.__NewProducts__(self.productlist)
        #self.productlist = []
        self.ScreenFuncs.RequestScreen(Screens.INTROSCREEN)
        