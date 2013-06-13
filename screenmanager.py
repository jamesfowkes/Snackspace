import logging

from screens.introscreen import IntroScreen
from screens.numericentry import NumericEntry
from screens.mainscreen import MainScreen
from screens.productentry import ProductEntry

from constants import Screens

class ScreenManager:
    
    def __init__(self, owner, window, width, height):
        
        self.window = window
        
        # Instantiate all the screens now
        self.screens = {
            Screens.INTROSCREEN.value   : IntroScreen(width, height, self, owner),
            Screens.NUMERICENTRY.value  : NumericEntry(width, height, self, owner),
            Screens.MAINSCREEN.value    : MainScreen(width, height, self, owner),
            Screens.PRODUCTENTRY.value  : ProductEntry(width, height, self, owner)
            }
        
        self.validScreenTransitions = {
            Screens.BLANKSCREEN     : [Screens.INTROSCREEN],
            Screens.INTROSCREEN     : [Screens.MAINSCREEN, Screens.PRODUCTENTRY],
            Screens.MAINSCREEN      : [Screens.INTROSCREEN, Screens.NUMERICENTRY],
            Screens.NUMERICENTRY    : [Screens.MAINSCREEN],
            Screens.PRODUCTENTRY    : [Screens.INTROSCREEN]
            }
        
        self.logger = logging.getLogger("screenmanager")
        
        self.screens[Screens.INTROSCREEN.value].active = False
        self.screens[Screens.NUMERICENTRY.value].active = False
        self.screens[Screens.MAINSCREEN.value].active = False
        
        self.currentscreen = Screens.BLANKSCREEN
        self.Req(Screens.INTROSCREEN)
        
    def Get(self, screen):
        return self.screens[screen.value]
    
    @property
    def Current(self):
        return self.screens[self.currentscreen.value]

    def Req(self, newscreen):
            
            valid = False
            if (newscreen.value == self.currentscreen.value) or self.__isValidTransition(newscreen):
                self.logger.debug("Changing screen from %s to %s" % (self.currentscreen.str, newscreen.str))
                
                if self.currentscreen.value not in [-1, newscreen.value]:
                    self.screens[self.currentscreen.value].SetActive(False)
                self.currentscreen = newscreen
                self.screens[newscreen.value].SetActive(True)
                
                valid = True
                self.screens[newscreen.value].draw(self.window)
            else:
                self.logger.debug("Could not change screen from %s to %s" % (self.currentscreen.str, newscreen.str))
                    
            return valid
    
    def __isValidTransition(self, newscreen):
        
        validTransitions = self.validScreenTransitions[self.currentscreen]    
        return newscreen in validTransitions