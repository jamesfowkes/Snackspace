""" 
introscreen.py
The first screen to be displayed when snackspace starts.
"""

from .displayconstants import Colours, Screens

from .screen import Screen
from .introscreen_gui import IntroScreenGUI

class IntroScreen(Screen, IntroScreenGUI):
    """ Implementation of introduction screen """
    def __init__(self, width, height, manager, owner):
        
        Screen.__init__(self, manager, owner, Screens.INTROSCREEN)
        IntroScreenGUI.__init__(self, width, height, self)

    def _update_on_active(self):
        pass

    def on_rfid(self):
        """ Handle RFID swipe: just request a switch to main screen """
        if self.active:
            self.screen_manager.req(Screens.MAINSCREEN)
            
    def on_bad_rfid(self):
        """ Do nothing on touchscreen press """ 
        pass
    
    def on_gui_event(self, pos):
        """ Do nothing on touchscreen press """ 
        pass

    def on_key_event(self, key):
        """ Do nothing on keyboard press """
        pass

    def on_scan(self, __product):
        """ Handle barcode scan: just request a switch to main screen """
        if self.active:
            self.screen_manager.req(Screens.MAINSCREEN)

    def on_bad_scan(self, __barcode):
        """ Handle invalid barcode scan: show a banner """
        if self.active:
            self.set_banner_with_timeout("Unknown barcode: '%s'" % __barcode, 4, Colours.ERR, self._banner_timeout)
            self._request_redraw()

    def set_db_state(self, db_connected):
        """ Handle change of database state: update GUI to reflect """
        if not db_connected:
            self.set_intro_text("ERROR: Cannot access Snackspace remote database", Colours.ERR)
        else:
            self.set_intro_text("Scan an item or swipe your card to start", Colours.FG)
    
    def _banner_timeout(self):
        """ Callback from GUI indicating banner has timed out """
        self.hide_banner()
        self._request_redraw()
        
    def _request_redraw(self):
        """ Push a request for this screen to be drawn again """
        self.screen_manager.req(self.screen_id)