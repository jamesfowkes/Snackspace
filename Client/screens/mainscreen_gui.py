"""
mainscreen_gui.py
"""

from __future__ import division

import pygame #@UnresolvedImport
import logging

from enum import Enum
from const import Const

from screens.productdisplay import ProductDisplayCollection

from screens.displayconstants import Widths, Colours

from LCARSGui import LCARSCappedBar, CapLocation

from screens.border import Border
from screens.screen_gui import ScreenGUI
           
class MainScreenLayout:

    """ Describes the graphical elements of the main screen and
    provides methods for setting introduction text """

    def __init__(self, width, height, border):
     
        self.button_data = Const()
        self.button_data.width = 100
        self.button_data.large_width = self.button_data.width * 2
        self.button_data.height = 50

        ## Spread buttons out between sweep and edge
        self.button_data.done_x = border.inner_x() + Widths.BORDER
        self.button_data.cancel_x = width - Widths.BORDER - self.button_data.large_width
        self.button_data.pay_x = (self.button_data.done_x + self.button_data.cancel_x) / 2
        self.button_data.y = height - Widths.BORDER - self.button_data.height  # Put buttons at bottom of screen

        ## Put the top bar below the sweep
        self.top_bar = Const()
        self.top_bar.x = border.inner_x() + Widths.BORDER
        self.top_bar.y = border.inner_y() + Widths.BORDER

        ## This allows caculation of the inner width of the useable screen area
        self.inner_width = width - self.top_bar.x - Widths.BORDER

        ## And then the small amount  bar can be defined 
        self.amount = Const()
        self.amount.y = self.top_bar.y
        self.amount.width = 2 * self.button_data.width
        self.amount.x = width - Widths.BORDER - self.amount.width

        ## And finally the top bar width can be defined
        self.top_bar.width = self.inner_width - self.amount.width - Widths.BORDER

        ## The first product entry starts below the top bar
        self.product_entries = Const()
        self.product_entries.top_y = self.top_bar.y + self.button_data.height + Widths.BORDER

        # The up/dn scroll buttons cover the whole height of the screen
        scroll_height = (self.button_data.y - self.product_entries.top_y) / 2
        scroll_height -= Widths.BORDER
        
        self.scroll = Const()
        self.scroll.height = scroll_height

        self.scroll.width = self.button_data.height
        self.scroll.x = width - Widths.BORDER - self.scroll.width
        self.scroll.up_y = self.product_entries.top_y
        self.scroll.dn_y = self.scroll.up_y + self.scroll.height + Widths.BORDER

        # Position constants for product objects
        
        self.product_entries.desc_x = self.top_bar.x
        self.product_entries.desc_w = self.button_data.large_width * 1.8
        self.product_entries.price_x = self.product_entries.desc_x + self.product_entries.desc_w + Widths.BORDER
        self.product_entries.price_w = self.button_data.large_width / 2
        self.product_entries.remove_x = self.product_entries.price_x + self.product_entries.price_w + Widths.BORDER
        self.product_entries.row_h = self.button_data.height + 20
        
    def get_done_rect(self):
        """ Return rectangle representing the Done button """
        return pygame.Rect(self.button_data.done_x, self.button_data.y, self.button_data.large_width, self.button_data.height)

    def get_pay_rect(self):
        """ Return rectangle representing the Pay button """
        return pygame.Rect(self.button_data.pay_x, self.button_data.y, self.button_data.large_width, self.button_data.height)

    def get_cancel_rect(self):
        """ Return rectangle representing the Cancel button """
        return pygame.Rect(self.button_data.cancel_x, self.button_data.y, self.button_data.large_width, self.button_data.height)

    def get_top_bar_rect(self):
        """ Return rectangle representing the top information bar """
        return pygame.Rect(self.top_bar.x, self.top_bar.y, self.top_bar.width, self.button_data.height)

    def get_amount_rect(self):
        """ Return rectangle representing the total amount bar """
        return pygame.Rect(self.amount.x, self.amount.y, self.amount.width, self.button_data.height)

    def get_up_scroll_rect(self):
        """ Return rectangle representing the up scroll button """
        return pygame.Rect(self.scroll.x, self.scroll.up_y, self.scroll.width, self.scroll.height)

    def get_down_scroll_rect(self):
        """ Return rectangle representing the down scroll button """
        return pygame.Rect(self.scroll.x, self.scroll.dn_y, self.scroll.width, self.scroll.height)

    def get_description_rect(self, index):
        """ Returns a rectangle representing the description display for a product """
        y_position = self.product_entries.top_y + (self.product_entries.row_h * index)
        return pygame.Rect(self.product_entries.desc_x, y_position, self.product_entries.desc_w, self.button_data.height)
    
    def get_price_rect(self, index):
        """ Returns a rectangle representing the price display for a product """
        y_position = self.product_entries.top_y + (self.product_entries.row_h * index)
        return pygame.Rect(self.product_entries.price_x, y_position, self.product_entries.price_w, self.button_data.height)
    
    def get_remove_rect(self, index, width):
        """ Returns a rectangle representing the remove button for a product """
        y_position = self.product_entries.top_y + (self.product_entries.row_h * index)
        return pygame.Rect(self.product_entries.remove_x, y_position, width, self.button_data.height)
    
class MainScreenGUI(ScreenGUI):

    """ Describes the graphical elements of the main screen and
    provides methods for adding and remove products """
    
    def __init__(self, width, height, owner):
        
        ScreenGUI.__init__(self, width, height, owner)
        self.border = Border(width, height)

        # Object constant definitions
        # Reverse draw order - 0 drawn last
        self.ids = Enum("DONE", "CANCEL", "PAY", "TOPBAR", "AMOUNT", "UP", "DOWN", "PRODUCT", "REMOVE")
        
        self.limits = Const()
        self.limits.screen_products = 5
        self.limits.objects_per_product_row = 3

        self.logger = logging.getLogger("MainScreen.GUI")
        
        self.product_displays = ProductDisplayCollection(self.limits.screen_products)
        
        # #
        # # Fixed position objects
        # #
        self.layout = MainScreenLayout(width, height, self.border)

        self.objects = {
            self.ids.DONE: LCARSCappedBar(
                self.layout.get_done_rect(), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "Done", Colours.FG, Colours.BG, False),
            self.ids.PAY:LCARSCappedBar(
                self.layout.get_pay_rect(), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "Pay debt", Colours.FG, Colours.BG, False),
            self.ids.CANCEL:LCARSCappedBar(
                self.layout.get_cancel_rect(), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "Cancel", Colours.FG, Colours.BG, True),
            self.ids.TOPBAR:LCARSCappedBar(
                self.layout.get_top_bar_rect(), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "User: <No user scanned>", Colours.FG, Colours.BG, True),
            self.ids.UP: LCARSCappedBar(
                self.layout.get_up_scroll_rect(), CapLocation.CAP_TOP, "UP", Colours.FG, Colours.BG, False),
            self.ids.DOWN: LCARSCappedBar(
                self.layout.get_down_scroll_rect(), CapLocation.CAP_BOTTOM, "DN", Colours.FG, Colours.BG, False),
            self.ids.AMOUNT:LCARSCappedBar(
                self.layout.get_amount_rect(), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "Total Spend: \xA30.00", Colours.FG, Colours.BG, True)
        }

        # #
        # # Import standard objects
        # #
        self.objects.update(self.border.get_border())
                  
    def add_to_product_display(self, product):
        """ Add a new product to the list """
        self.product_displays.add(product)

    def update_total(self):
        """ Update the total spend value """
        self.objects[self.ids.AMOUNT].setText("Total Spend: \xA3%.2f" % (self.owner.total_price() / 100))

    def _remove_button_width(self):
        """ The width of the remove button depends on whether the up/dn buttons are displayed """
        removew = self.width - self.layout.product_entries.remove_x - Widths.BORDER

        if self._test_display_down_button() or self._test_display_up_button():
            removew -= (self.layout.scroll.width + Widths.BORDER)

        return removew

    def get_object_id(self, pos):
        """ Returns the ID of the object at the given position """
        object_id = ScreenGUI.get_object_id(self, pos)

        if object_id == -1:
            # Try searching remove buttons
            if self.product_displays.collide_on_remove(pos) is not None:
                object_id = self.ids.REMOVE
            
        return object_id

    def set_unknown_user(self):
        """ Indicate that an unknown card was scanned """
        self.objects[self.ids.TOPBAR].setText("User: <Unknown card>")

    def set_user(self, name, balance, credit):
        """ Set the current username """
        if balance >= 0:
            text = u"%s (Balance: \xA3%.2f" % (name, balance / 100)
        else:
            text = u"%s (Balance: -\xA3%.2f" % (name, -balance / 100)

        if credit > 0:
            text += u", Pending Credit: \xA3%.2f" % (credit / 100)

        text += ")"

        self.objects[self.ids.TOPBAR].setText(text)

    def _test_display_up_button(self):
        """ Returns TRUE if the up button should be displayed """
        return (self.product_displays.top_index > 0)

    def _test_display_down_button(self):
        """ Returns TRUE if the down button should be displayed """
        return (self.product_displays.top_index + self.limits.screen_products) < len(self.product_displays)

    def clear_products(self):
        """ Reset the products list to nothing """
        self.product_displays.clear()

    def draw(self, window):
        
        """ Redraw the main screen """
        window.fill(Colours.BG)

        self._set_show_hide_products()
        self._draw_products(window)
        self._draw_static_objects(window)

        pygame.display.flip()

    def _set_show_hide_products(self):

        """ Scan down the product list and set the visible
        state of the product objects """
        
        visible_count = 0

        for (counter, product) in enumerate(self.product_displays):

            if (counter < self.product_displays.top_index):
                # Hide all the products above the list product top
                product.set_visible(False)
            elif visible_count < self.limits.screen_products:
                # Show screen products based on their quantity
                product.visible = True
                visible_count += 1
            else:
                # Hide products below list bottom
                product.set_visible(False)

    def _draw_products(self, window):

        """ Draw all visible product objects on the window """
        
        # Iterate over all products in list
        index = 0
        for product in self.product_displays:
            if product.visible:
                product.draw(self.layout, index, self._remove_button_width(), window)
                index += 1

    def _draw_static_objects(self, window):

        """ Draw all the static objects on the window """
        
        self.update_total()

        ## Draw border
        for draw_object in self.border.get_border().values():
            draw_object.draw(window)

        # Draw the fixed objects
        static_objs = [
                self.objects[self.ids.TOPBAR],
                self.objects[self.ids.PAY],
                self.objects[self.ids.CANCEL],
                self.objects[self.ids.DONE],
                self.objects[self.ids.AMOUNT],
                self.objects[self.ids.UP],
                self.objects[self.ids.DOWN]
        ]

        # Decide which objects should be shown
        if self.owner.user is not None:
            self.objects[self.ids.PAY].visible = self.owner.user.credit_allowed()
            self.objects[self.ids.DONE].visible = self.owner.user.has_added_credit() or (len(self.product_displays) > 0)
            
        self.objects[self.ids.UP].visible = self._test_display_up_button()
        self.objects[self.ids.DOWN].visible = self._test_display_down_button()

        for static_obj in static_objs:
            static_obj.draw(window)

        if self.banner is not None:
            self.banner.draw(window)

    def active(self):
        """ Abstraction for the active state of the screen """
        return self.owner.active