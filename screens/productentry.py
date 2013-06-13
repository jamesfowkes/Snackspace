from __future__ import division

import logging

from constants import Screens

# # Safe wild import: all constants
from displayconstants import *  # @UnusedWildImport

from productentry_gui import ProductEntryGUI

from SimpleStateMachine import SimpleStateMachine, SimpleStateMachineEntry

from enum import Enum

class ProductEntry:

    def __init__(self, width, height, manager, owner):
        
        self.gui = ProductEntryGUI(width, height, self)    
    
        self.acceptInput = False
        
        self.ScreenManager = manager
        self.Owner = owner
        
        self.allowDescChars = " !$%^&*(){}[]:@~;'#<>?,./\\"
        self.states = Enum(["BARCODE", "DESCRIPTION", "PRICE", "ADDING", "WARNING"])
        self.events = Enum(["GUIEVENT", "SCAN", "BADSCAN", "KEYPRESS", "TIMEOUT"])
        
        self.barcode = ""
        self.price = 0
        self.description = ""
        
        self.SM = SimpleStateMachine(self.states.BARCODE,
        [        
            SimpleStateMachineEntry(self.states.BARCODE, self.events.GUIEVENT,      self.__onGuiEvent),
            SimpleStateMachineEntry(self.states.BARCODE, self.events.SCAN,          self.__gotBarcode),
            SimpleStateMachineEntry(self.states.BARCODE, self.events.BADSCAN,       self.__gotNewBarcode),
            SimpleStateMachineEntry(self.states.BARCODE, self.events.KEYPRESS,      lambda: self.states.BARCODE),
            
            SimpleStateMachineEntry(self.states.DESCRIPTION, self.events.GUIEVENT,  self.__onGuiEvent),
            SimpleStateMachineEntry(self.states.DESCRIPTION, self.events.KEYPRESS,  self.__gotNewDescChar),
            SimpleStateMachineEntry(self.states.DESCRIPTION, self.events.SCAN,      lambda: self.states.DESCRIPTION),
            SimpleStateMachineEntry(self.states.DESCRIPTION, self.events.BADSCAN,   lambda: self.states.DESCRIPTION),
            
            SimpleStateMachineEntry(self.states.PRICE, self.events.GUIEVENT,        self.__onGuiEvent),
            SimpleStateMachineEntry(self.states.PRICE, self.events.KEYPRESS,        self.__gotNewPriceChar),
            SimpleStateMachineEntry(self.states.PRICE, self.events.SCAN,            lambda: self.states.DESCRIPTION),
            SimpleStateMachineEntry(self.states.PRICE, self.events.BADSCAN,         lambda: self.states.DESCRIPTION),
            
            SimpleStateMachineEntry(self.states.ADDING, self.events.TIMEOUT,        self.__exit),
            
            SimpleStateMachineEntry(self.states.WARNING, self.events.TIMEOUT,       lambda: self.states.BARCODE),
        ])
        
        self.logger = logging.getLogger("ProductEntry")
        
    def SetActive(self, state):
        self.acceptInput = state
    
    def OnKeyEvent(self, char):
        if self.acceptInput:
            self.lastChar = char
            self.SM.onStateEvent(self.events.KEYPRESS)
        
    def OnGuiEvent(self, pos):
        if self.acceptInput:
            self.lastGuiPosition = pos
            self.SM.onStateEvent(self.events.GUIEVENT)
    
    def OnBadScan(self, barcode):
        if self.acceptInput:
            self.barcode = barcode
            self.SM.onStateEvent(self.events.BADSCAN)
         
    def OnScan(self, __product):
        if self.acceptInput:
            self.SM.onStateEvent(self.events.SCAN)
                       
    def __onGuiEvent(self):
    
        pos = self.lastGuiPosition
        button = self.gui.getObjectId(pos)
               
        if button == self.gui.BARCODE:
            self.barcode = ""
            self.gui.SetActiveEntry(self.gui.BARCODE)
            self.__requestRedraw()
            return self.states.BARCODE
        
        if button == self.gui.DESCRIPTION:
            self.description = ""
            self.gui.SetActiveEntry(self.gui.DESCRIPTION)
            self.__requestRedraw()
            return self.states.DESCRIPTION
        
        if button == self.gui.PRICE:
            self.price = 0
            self.gui.SetActiveEntry(self.gui.PRICE)
            self.__requestRedraw()
            return self.states.PRICE
        
        if button == self.gui.DONE:
            if self.__dataReady():
                self.__addProduct()
                return self.states.ADDING
            else:
                self.gui.SetBannerWithTimeout("One or more entries not valid!", 4, RGB_WARNING_FG, self.__bannerTimeout)
                self.__requestRedraw()
                return self.states.WARNING
                
        
        if button == self.gui.CANCEL:
            self.__exit()
            return self.states.BARCODE
    
        #No GUI object hit:
        return self.SM.state
    
    def __gotNewDescChar(self):
        
        if self.lastChar.isalnum() or (self.lastChar in self.allowDescChars):
            self.description += self.lastChar
        elif self.lastChar ==  "\b":
            self.description = self.description[:-1]
        
        self.gui.ChangeDescription(self.description)
        self.__requestRedraw()
        return self.states.DESCRIPTION
    
    def __gotNewPriceChar(self):
        
        if self.lastChar.isdigit():
            self.price *= 10
            self.price += int(self.lastChar)
        elif self.lastChar == "\b":
            self.price = int(self.price / 10)
        
        self.gui.ChangePrice(self.price)
        self.__requestRedraw()
        return self.states.PRICE
               
    def __dataReady(self):
        dataReady = len(self.barcode) > 0
        dataReady &= self.price > 0
        dataReady &= len(self.description) > 0
        return dataReady
    
    def __addProduct(self):
        if self.Owner.NewProduct(self.barcode, self.description, self.price):
            self.gui.SetBannerWithTimeout("New product %s added!" % self.description, 3, RGB_INFO_FG, self.__bannerTimeout)
        else:
            self.gui.SetBannerWithTimeout("New product %s was not added!" % self.description, 3, RGB_WARNING_FG, self.__bannerTimeout)
    
        self.__requestRedraw()
        
        return self.states.ADDING
            
    def __gotNewBarcode(self):
        self.gui.ChangeBarcode(self.barcode)
        self.__requestRedraw()
        return self.states.BARCODE
    
    def __gotBarcode(self):
        self.gui.SetBannerWithTimeout("Barcode already exists!", 4, RGB_WARNING_FG, self.__bannerTimeout)
        self.__requestRedraw()
        return self.states.WARNING
        
    def __bannerTimeout(self):
        self.gui.HideBanner()
        self.__requestRedraw()
        self.SM.onStateEvent(self.events.TIMEOUT)
    
    def __requestRedraw(self):
        self.ScreenManager.Req(Screens.PRODUCTENTRY)
        
    def draw(self, window):
        self.logger.info("Drawing self")
        self.gui.draw(window)
        
    def __exit(self):
        self.ScreenManager.Req(Screens.INTROSCREEN)
        return self.states.BARCODE