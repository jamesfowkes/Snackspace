""" 
screenmanager.py

Handles switching between snackspace SCREENS
"""

import logging

from screens.displayconstants import Screens

from screens.introscreen import IntroScreen
from screens.numericentry import NumericEntry
from screens.mainscreen import MainScreen
from screens.productentry import ProductEntry
   
class ScreenManager:
    """ Implements a management class for handling screens and transitions between them """
    def __init__(self, owner, window, size):

        width, height = size[0], size[1]
        
        self.window = window

        # Instantiate all the SCREENS now
        self.screens = {
            Screens.INTROSCREEN   : IntroScreen(width, height, self, owner),
            Screens.NUMERICENTRY  : NumericEntry(width, height, self, owner),
            Screens.MAINSCREEN    : MainScreen(width, height, self, owner),
            Screens.PRODUCTENTRY  : ProductEntry(width, height, self, owner)
            }

        self.valid_screen_transitions = {
            Screens.BLANKSCREEN     : [Screens.INTROSCREEN],
            Screens.INTROSCREEN     : [Screens.MAINSCREEN, Screens.PRODUCTENTRY],
            Screens.MAINSCREEN      : [Screens.INTROSCREEN, Screens.NUMERICENTRY],
            Screens.NUMERICENTRY    : [Screens.MAINSCREEN],
            Screens.PRODUCTENTRY    : [Screens.INTROSCREEN]
            }

        self.logger = logging.getLogger("screenmanager")

        self.screens[Screens.INTROSCREEN].active = False
        self.screens[Screens.NUMERICENTRY].active = False
        self.screens[Screens.MAINSCREEN].active = False

        self.currentscreen = Screens.BLANKSCREEN
        self.req(Screens.INTROSCREEN)

    def get(self, screen):
        """ Get the requested screen object """
        return self.screens[screen]

    @property
    def current(self):
        """ Return the current screen object """
        return self.screens[self.currentscreen]

    def req(self, newscreen):
        """ Request to show a new screen """
        valid = False
        if (newscreen == self.currentscreen) or self.is_valid_transition(newscreen):
            self.logger.debug("Changing screen from %s to %s" % (self.currentscreen, newscreen))

            if self.currentscreen not in [Screens.BLANKSCREEN, newscreen]:
                self.screens[self.currentscreen].set_active(False)
            self.currentscreen = newscreen
            self.screens[newscreen].set_active(True)

            valid = True
            self.screens[newscreen].draw(self.window)
        else:
            self.logger.debug("Could not change screen from %s to %s" % (self.currentscreen, newscreen))

        return valid

    def is_valid_transition(self, newscreen):
        """ Returns true if the new screen is reachable from the current one """
        valid_transitions = self.valid_screen_transitions[self.currentscreen]
        return newscreen in valid_transitions
