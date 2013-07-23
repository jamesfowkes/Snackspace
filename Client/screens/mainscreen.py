"""
mainscreen.py
"""

from __future__ import division

import logging

from screenmanager import Screens

from screens.displayconstants import Colours

from screens.mainscreen_gui import MainScreenGUI

from screens.screen import Screen

from SimpleStateMachine import SimpleStateMachine

from enum import Enum
        
class MainScreen(Screen, MainScreenGUI):

    """ Implements the main checkout screen """
    
    def __init__(self, width, height, manager, owner):
        Screen.__init__(self, manager, owner, Screens.MAINSCREEN)
        MainScreenGUI.__init__(self, width, height, self)
        
        self.states = Enum("IDLE", "PAYMENTMSG", "WARNING")
        self.events = Enum("GUIEVENT", "SCAN", "BADSCAN", "RFID", "BADRFID", "BANNERTIMEOUT")
        
        self.sm = SimpleStateMachine(self.states.IDLE, #pylint: disable=C0103
        [
                [self.states.IDLE,          self.events.GUIEVENT,       self._on_idle_gui_event],
                [self.states.IDLE,          self.events.SCAN,           self._on_idle_scan_event],
                [self.states.IDLE,          self.events.BADSCAN,        self._on_idle_bad_scan_event],
                [self.states.IDLE,          self.events.RFID,           self._on_rfid_event],
                [self.states.IDLE,          self.events.BADRFID,        self._on_bad_rfid_event],

                [self.states.PAYMENTMSG,    self.events.BANNERTIMEOUT,  self._return_to_intro],
                [self.states.PAYMENTMSG,    self.events.GUIEVENT,       lambda: self.states.PAYMENTMSG],
                [self.states.PAYMENTMSG,    self.events.SCAN,           lambda: self.states.PAYMENTMSG],
                [self.states.PAYMENTMSG,    self.events.BADSCAN,        lambda: self.states.PAYMENTMSG],
                [self.states.PAYMENTMSG,    self.events.RFID,           lambda: self.states.PAYMENTMSG],
                [self.states.PAYMENTMSG,    self.events.BADRFID,        lambda: self.states.PAYMENTMSG],

                [self.states.WARNING,       self.events.BANNERTIMEOUT,  self._remove_warning],
                [self.states.WARNING,       self.events.SCAN,           self._on_idle_scan_event],
                [self.states.WARNING,       self.events.BADSCAN,        self._update_barcode_warning],
                [self.states.WARNING,       self.events.RFID,           self._on_rfid_event],
                [self.states.WARNING,       self.events.BADRFID,        self._on_bad_rfid_event],
                [self.states.WARNING,       self.events.GUIEVENT,       self._remove_warning],

        ])

        self.logger = logging.getLogger("MainScreen")

        self.new_product = None
        self.badcode = ""
        
    def on_gui_event(self, pos):
        """ Called from owner to trigger a GUI press """
        if self.active:
            self.last_gui_position = pos
            self.sm.on_state_event(self.events.GUIEVENT)

    def on_scan(self, product):
        """ Called from owner to trigger a known product scan """
        self.new_product = product
        if self.active:
            self.sm.on_state_event(self.events.SCAN)

    def on_bad_scan(self, badcode):
        """ Called from owner to trigger an unknown product scan """
        if self.active:
            self.badcode = badcode
            self.sm.on_state_event(self.events.BADSCAN)

    def on_key_event(self, key):
        """ Called from owner to trigger keyboard press """
        pass

    def on_rfid(self):
        """ Called from owner to trigger a known RFID scan """
        if self.active:
            self.sm.on_state_event(self.events.RFID)

    def on_bad_rfid(self):
        """ Called from owner to trigger an unknown RFID scan """
        if self.active:
            self.sm.on_state_event(self.events.BADRFID)

    def user_allow_credit(self):
        """ Is the user allow to add credit to their account? """
        try:
            return self.user.creditAllowed()
        except AttributeError:
            return False

    def user_added_credit(self):
        """ Has the user added credit to their account? """
        return (self.user.Credit > 0)

    def _update_on_active(self):
        """ When active state changes, this is called to update screen """
        if self.user:
            self.set_user(self.user.name, self.user.balance, self.user.credit)
        else:
            self.set_unknown_user()

        for product in self.owner.products:
            self.on_scan(product)

    def total_price(self):
        """ Abstraction for total price """
        return self.owner.total_price()

    def _on_idle_gui_event(self):

        """ State machine function
        Runs when a GUI event has been triggered in idle
        """
        pos = self.last_gui_position
        button = self.get_object_id(pos)

        # Default to staying in same state
        next_state = self.sm.state

        if button > -1:
            self.play_sound()

        if (button == self.ids.DONE):
            next_state = self._charge_user()

        if (button == self.ids.CANCEL):
            next_state = self._return_to_intro()

        if (button == self.ids.PAY):
            self.screen_manager.req(Screens.NUMERICENTRY)

        if (button == self.ids.DOWN):
            self.product_displays.move_down()
            self._request_redraw()

        if (button == self.ids.UP):
            self.product_displays.move_up()
            self._request_redraw()

        if (button == self.ids.REMOVE):

            product = self.product_displays.get_at_position(pos)
            self.logger.info("Removing product %s" % product.barcode)

            if self.owner.remove_product(product) == 0:
                # No products of this type left in list
                self.product_displays.remove(product)

            self._request_redraw()

        return next_state

    def _on_idle_scan_event(self):
        """ State machine function
        Runs when a barcode scan has been triggered in idle
        """
        self.logger.info("Got barcode %s" % self.new_product.barcode)

        # Ensure that the warning banner goes away
        self.hide_banner()

        next_state = self.states.IDLE

        if self.user is not None:
            trans_allowed_state = self.user.transaction_allowed(self.new_product.price_in_pence)

            if trans_allowed_state == self.user.XACTION_ALLOWED:
                ## Add product, nothing else to do
                self.product_displays.add(self.new_product)
            elif trans_allowed_state == self.user.XACTION_OVERLIMIT:
                ## Add product, but also warn about being over credit limit
                self.product_displays.add(self.new_product)
                self.set_banner_with_timeout("Warning: you have reached your credit limit!", 4, Colours.WARN, self._banner_timeout)
                next_state = self.states.WARNING
            elif trans_allowed_state == self.user.XACTION_DENIED:
                ## Do not add the product to screen. Request removal from product list and warn user
                self.set_banner_with_timeout("Sorry, you have reached your credit limit!", 4, Colours.ERR, self._banner_timeout)
                self.owner.RemoveProduct(self.new_product)
                next_state = self.states.WARNING
        else:
            #Assume that the user is allowed to buy this
            self.product_displays.add(self.new_product)

        self._request_redraw()
        self.new_product = None

        return next_state

    def _on_idle_bad_scan_event(self):
        """ State machine function
        Runs when a bad barcode has been scanned in idle
        """
        self.logger.info("Got unrecognised barcode %s" % self.badcode)
        self.set_banner_with_timeout("Unknown barcode: '%s'" % self.badcode, 4, Colours.ERR, self._banner_timeout)
        self._request_redraw()
        self.badcode = ""

        return self.states.WARNING

    def _on_rfid_event(self):
        """ State machine function
        Runs when a known RFID card has been scanned in idle
        """
        self.logger.info("Got user %s" % self.user.name)
        self.hide_banner()
        self.set_user(self.user.name, self.user.balance, self.user.credit)
        self._request_redraw()

        return self.sm.state

    def _on_bad_rfid_event(self):
        """ State machine function
        Runs when an unknown RFID card has been scanned in idle
        """
        self.set_banner_with_timeout("Unknown RFID card!", 4, Colours.ERR, self._banner_timeout)
        self._request_redraw()
        return self.states.WARNING

    def _banner_timeout(self):
        """ Callback from GUI indicating banner has timed out """
        self.sm.on_state_event(self.events.BANNERTIMEOUT)

    def _update_barcode_warning(self):
        """ Show a warning about an unknown barcode """ 
        self.logger.info("Got unrecognised barcode %s" % self.badcode)
        self.set_banner_with_timeout("Unknown barcode: '%s'" % self.badcode, 4, Colours.ERR, self._banner_timeout)
        self._request_redraw()
        return self.states.WARNING

    def _remove_warning(self):
        """ Get rid of any banner """
        self.hide_banner()
        self._request_redraw()
        return self.states.IDLE

    def _return_to_intro(self):
        """ Request a return to the intro screen """
        self.hide_banner()
        
        ## Forget everything about the user and products
        self.clear_products()
        self.set_unknown_user()
        self.owner.forget_user()
        self.owner.forget_products()
        
        self.screen_manager.req(Screens.INTROSCREEN)
        return self.states.IDLE

    def _charge_user(self):

        """ Calculate the final amount to charge the user and request the charge 
        Then show appropriate banner """
        next_state = self.states.PAYMENTMSG

        amountinpounds = self.total_price() / 100
        creditinpounds = self.user.credit / 100
        banner_width = 0.6

        if self.owner.charge_all() == True:
            text = u"Thank you! You have been charged \xA3%.2f" % amountinpounds
            if creditinpounds > 0:
                text += u" and credited \xA3%.2f" % creditinpounds
                banner_width = 0.8

            self.set_banner_with_timeout(text, 8, Colours.INFO, self._banner_timeout)
            self.set_banner_width_fraction(banner_width)
        else:
            self.set_banner_with_timeout("An error occurred and has been logged.", 10, Colours.ERR, self._banner_timeout)
            self.logger.error("Failed to charge user %s %d pence")

        self._request_redraw()

        return next_state
    
    def _request_redraw(self):
        """ Push a request for this screen to be drawn again """
        self.screen_manager.req(self.screen_id)
        
    @property
    def user(self):
        """ Easy access to the user """
        return self.owner.user
