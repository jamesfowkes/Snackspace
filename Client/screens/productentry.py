"""
productentry.py
"""

from __future__ import division

from screens.displayconstants import Colours, Screens

from screens.screen import Screen

from screens.productentry_gui import ProductEntryGUI

from SimpleStateMachine import SimpleStateMachine

from enum import Enum

class ProductEntry(Screen, ProductEntryGUI): #pylint: disable=R0902

    """ Implements the product entry screen
    pylint R0902 disabled as one 1 more attribute than recommened.
    Alternatives make code more complex than it needs to be for such a simple class"""
    
    def __init__(self, width, height, manager, owner):

        Screen.__init__(self, manager, owner, Screens.PRODUCTENTRY)
        ProductEntryGUI.__init__(self, width, height, self)

        self.states = Enum("BARCODE", "DESCRIPTION", "PRICE", "ADDING", "WARNING")
        self.events = Enum("GUIEVENT", "SCAN", "BADSCAN", "KEYPRESS", "TIMEOUT")

        self.barcode = ""
        self.price = 0
        self.description = ""
       
        self.sm = SimpleStateMachine(self.states.BARCODE, #pylint: disable=C0103
        [
            (self.states.BARCODE, self.events.GUIEVENT,      self._on_gui_event),
            (self.states.BARCODE, self.events.SCAN,          self._got_barcode),
            (self.states.BARCODE, self.events.BADSCAN,       self._got_new_barcode),
            (self.states.BARCODE, self.events.KEYPRESS,      lambda: self.states.BARCODE),

            (self.states.DESCRIPTION, self.events.GUIEVENT,  self._on_gui_event),
            (self.states.DESCRIPTION, self.events.KEYPRESS,  self._got_new_desc_char),
            (self.states.DESCRIPTION, self.events.SCAN,      lambda: self.states.DESCRIPTION),
            (self.states.DESCRIPTION, self.events.BADSCAN,   lambda: self.states.DESCRIPTION),

            (self.states.PRICE, self.events.GUIEVENT,        self._on_gui_event),
            (self.states.PRICE, self.events.KEYPRESS,        self._got_new_price_char),
            (self.states.PRICE, self.events.SCAN,            lambda: self.states.DESCRIPTION),
            (self.states.PRICE, self.events.BADSCAN,         lambda: self.states.DESCRIPTION),

            (self.states.ADDING, self.events.TIMEOUT,        self._exit),
            (self.states.ADDING, self.events.GUIEVENT,       lambda: self.states.ADDING),
            (self.states.ADDING, self.events.KEYPRESS,       lambda: self.states.ADDING),
            (self.states.ADDING, self.events.SCAN,           lambda: self.states.ADDING),
            (self.states.ADDING, self.events.BADSCAN,        lambda: self.states.ADDING),
            
            (self.states.WARNING, self.events.TIMEOUT,       lambda: self.states.BARCODE),
            (self.states.WARNING, self.events.GUIEVENT,       lambda: self.states.WARNING),
            (self.states.WARNING, self.events.KEYPRESS,       lambda: self.states.WARNING),
            (self.states.WARNING, self.events.SCAN,           lambda: self.states.WARNING),
            (self.states.WARNING, self.events.BADSCAN,        lambda: self.states.WARNING),
        ])

    def on_key_event(self, char):
        self.last_keypress = char
        self.sm.on_state_event(self.events.KEYPRESS)

    def on_gui_event(self, pos):
        self.last_gui_position = pos
        self.sm.on_state_event(self.events.GUIEVENT)

    def on_bad_scan(self, barcode):
        self.barcode = barcode
        self.sm.on_state_event(self.events.BADSCAN)

    def on_scan(self, __product):
        self.sm.on_state_event(self.events.SCAN)

    def _update_on_active(self):
        """ No need to change anything on active state """
        pass
    
    def on_rfid(self):
        """ Do nothing on RFID scans """
        pass
    
    def on_bad_rfid(self):
        """ Do nothing on RFID scans """
        pass
    
    def _on_gui_event(self):

        """ Move focus and state to pressed object """    
        pos = self.last_gui_position
        button = self.get_object_id(pos)
        next_state = self.sm.state 
        
        if button == self.buttons.BARCODE:
            self.barcode = ""
            self.set_active_entry(self.buttons.BARCODE)
            self._request_redraw()
            next_state = self.states.BARCODE

        if button == self.buttons.DESCRIPTION:
            self.description = ""
            self.set_active_entry(self.buttons.DESCRIPTION)
            self._request_redraw()
            next_state = self.states.DESCRIPTION

        if button == self.buttons.PRICE:
            self.price = 0
            self.set_active_entry(self.buttons.PRICE)
            self._request_redraw()
            next_state = self.states.PRICE

        if button == self.buttons.DONE:
            if self.data_ready():
                self.add_product()
                next_state = self.states.ADDING
            else:
                self.set_banner_with_timeout("One or more entries not valid!", 4, Colours.WARN, self._banner_timeout)
                self._request_redraw()
                next_state = self.states.WARNING

        if button == self.buttons.CANCEL:
            self._exit()
            next_state = self.states.BARCODE

        #No GUI object hit:
        return next_state

    def _got_new_desc_char(self):
        """ Update the description field on keypress """
        
        allow_desc_chars = " !$%^&*(){}[]:@~;'#<>?,./\\"
                
        if self.last_keypress.isalnum() or (self.last_keypress in allow_desc_chars):
            self.description += self.last_keypress
        elif self.last_keypress ==  "\b":
            self.description = self.description[:-1]

        self.change_description(self.description)
        self._request_redraw()
        return self.states.DESCRIPTION

    def _got_new_price_char(self):
        """ Update the price field on keypress """
        if self.last_keypress.isdigit():
            self.price *= 10
            self.price += int(self.last_keypress)
        elif self.last_keypress == "\b":
            self.price = int(self.price / 10)

        self.change_price(self.price)
        self._request_redraw()
        return self.states.PRICE

    def data_ready(self):
        """ Determine if all data is set """
        data_ready = len(self.barcode) > 0
        data_ready &= self.price > 0
        data_ready &= len(self.description) > 0
        return data_ready

    def add_product(self):
        """ Try to add the new product to the database """
        self.owner.new_product(self.barcode, self.description, self.price, self._add_product_callback)
    
    def _add_product_callback(self, barcode, description, result):
        """ Callback from database when adding product """
        if result:
            self.set_banner_with_timeout("New product %s added!" % description, 3, Colours.INFO, self._banner_timeout)
        else:
            self.set_banner_with_timeout("New product %s was not added!" % description, 3, Colours.WARN, self._banner_timeout)

        self._request_redraw()

        return self.states.ADDING
    
    def _got_new_barcode(self):
        """ On a new barcode scan, update the barcode field """
        self.change_barcode(self.barcode)
        self._request_redraw()
        return self.states.BARCODE

    def _got_barcode(self):
        """ If the barcode scanned exists, warn the user """
        self.set_banner_with_timeout("Barcode already exists!", 4, Colours.WARN, self._banner_timeout)
        self._request_redraw()
        return self.states.WARNING

    def _banner_timeout(self):
        """ Callback from GUI indicating banner has timed out """
        self.hide_banner()
        self._request_redraw()
        self.sm.on_state_event(self.events.TIMEOUT)

    def _request_redraw(self):
        """ Push a request for this screen to be drawn again """
        self.screen_manager.req(Screens.PRODUCTENTRY)

    def _exit(self):
        """ Request a return to the intro screen """
        self.reset_entry(self.buttons.BARCODE)
        self.reset_entry(self.buttons.PRICE)
        self.reset_entry(self.buttons.DESCRIPTION)
        
        self.screen_manager.req(Screens.INTROSCREEN)
        return self.states.BARCODE
