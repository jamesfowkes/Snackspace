"""
numericentry.py
"""

from __future__ import division

from screenmanager import Screens

from screens.numericentry_gui import NumericEntryGUI
from screens.screen import Screen

class NumericEntry(Screen, NumericEntryGUI):

    """ Implements the numeric entry screen """
    
    def __init__(self, width, height, manager, owner):
        
        Screen.__init__(self, manager, owner, Screens.NUMERICENTRY)
        NumericEntryGUI.__init__(self, width, height, self)
        self.amountinpence = 0
        self.preset_amount = False

    def on_gui_event(self, pos):

        button = self.get_object_id(pos)

        if button >= self.keys.KEY0 and button <= self.keys.KEY9:
            #Let button press decide whether to play sound or not
            self._new_button_press(button)
        else:
            #Play sound unconditionally for other buttons
            self.play_sound()
            if button == self.keys.FIVEPOUNDS:
                self.preset_amount = True
                self._set_amount(500)
            elif button == self.keys.TENPOUNDS:
                self.preset_amount = True
                self._set_amount(1000)
            elif button == self.keys.TWENTYPOUNDS:
                self.preset_amount = True
                self._set_amount(2000)
            elif button == self.keys.DONE:
                self._credit_and_exit()
            elif button == self.keys.CANCEL:
                self._exit()

    def _update_on_active(self):
        """ No action when active state changes """
        pass

    def on_scan(self, product):
        """ No action when product scanned """
        pass

    def on_bad_scan(self, badcode):
        """ No action when product scanned """
        pass

    def on_key_event(self, key):
        """ No action when key pressed """
        pass

    def on_rfid(self):
        """ No action when RFID scanned """
        pass

    def on_bad_rfid(self):
        """ No action when bad RFID scanned """
        pass

    def _set_amount(self, amount):
        """ Update the amount shown on the entry bar """
        self.amountinpence = amount
        self.update_amount(self.amountinpence)
        self.screen_manager.req(Screens.NUMERICENTRY)

    def _new_button_press(self, key):
        """ One of the 0-9 button has been pressed, set a new amount """
               
        if self.preset_amount:
            ## Clear the preset amount and assume starting from scratch
            self.preset_amount = False
            self.amountinpence = 0

        if ((self.amountinpence * 10) + key) <= 5000:

            self.play_sound()

            self.amountinpence *= 10
            self.amountinpence += key

            self.update_amount(self.amountinpence)
            self.screen_manager.req(Screens.NUMERICENTRY)

    def _credit_and_exit(self):
        """ Credit the user with the amount entered and then exit to the mainscreen """
        self.owner.credit_user(self.amountinpence)
        self._exit()

    def _exit(self):
        """ Reset this screen and return to mainscreen """
        self._set_amount(0)
        self.screen_manager.req(Screens.MAINSCREEN)
