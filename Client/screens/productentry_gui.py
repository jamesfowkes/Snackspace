"""
productentry_gui.py
"""

from __future__ import division

import pygame  # @UnresolvedImport

from enum import Enum

from screens.displayconstants import Widths, Colours

from LCARSGui import LCARSCappedBar, CapLocation

from screens.border import Border
from screens.screen_gui import ScreenGUI


class ProductEntryGUI(ScreenGUI):
    
    """ Describes the graphical elements of the product entry screen """
    
    def __init__(self, width, height, owner):

        ScreenGUI.__init__(self, width, height, owner)

        border = Border(width, height)

        self.buttons = Enum("BARCODE", "DESCRIPTION", "PRICE", "DONE", "CANCEL")

        # #
        # # Fixed position objects
        # #

        minx = border.inner_x() + 4 * Widths.BORDER
        maxx = width - Widths.BORDER
        miny = border.inner_y() + 4 * Widths.BORDER
        maxy = height - Widths.BORDER

        buttonh = 50
        buttonw = 100

        fullwidth = maxx - minx

        self.default_text = {
                        self.buttons.BARCODE : "1. Scan an item",
                        self.buttons.DESCRIPTION : "2. Type a description",
                        self.buttons.PRICE : "3. Set a price",
                        }

        self.objects = {
            self.buttons.BARCODE        : LCARSCappedBar(pygame.Rect(minx, miny, fullwidth, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "1. Scan an item", Colours.ENTRY, Colours.BG, True),
            self.buttons.DESCRIPTION    : LCARSCappedBar(pygame.Rect(minx, miny + (2 * buttonh), fullwidth, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "2. Type a description", Colours.ERR, Colours.BG, True),
            self.buttons.PRICE          : LCARSCappedBar(pygame.Rect(minx, miny + (4 * buttonh), fullwidth, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "3. Set a price", Colours.ERR, Colours.BG, True),
            self.buttons.DONE           : LCARSCappedBar(pygame.Rect(minx, maxy - buttonh, buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "Done", Colours.FG, Colours.BG, True),
            self.buttons.CANCEL         : LCARSCappedBar(pygame.Rect(maxx - buttonw, maxy - buttonh, buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "Cancel", Colours.FG, Colours.BG, True),
        }

        # #
        # # Import standard objects
        # #
        self.objects.update(border.get_border())

    def reset_entry(self, entry):
        
        """ Reset the text of the selected entry to the default """
        if entry == self.buttons.BARCODE:
            self.objects[entry].fg = Colours.FG
        else:
            self.objects[entry].fg = Colours.ERR
            
        self.objects[entry].setText(self.default_text[entry])
        
    def set_active_entry(self, entry):

        """ Change the current entry textbox to one of barcode, description or price """
        
        for key, gui_object in self.objects.iteritems():
            if key == entry:
                gui_object.fg = Colours.ENTRY
                gui_object.setText("")
            else:
                if key in [self.buttons.BARCODE, self.buttons.DESCRIPTION, self.buttons.PRICE]:
                    if (len(gui_object.getText()) == 0) or (gui_object.getText() == self.default_text[key]):
                        # No entry in this box. Set error colour
                        gui_object.fg = Colours.ERR
                        gui_object.setText(self.default_text[key])
                    else:
                        gui_object.fg = Colours.FG
                        gui_object.setText(gui_object.getText())  # Forces colour update

    def change_barcode(self, barcode):
        """ Set a new barocde for this product """
        self.objects[self.buttons.BARCODE].setText(barcode)

    def change_description(self, description):
        """ Set a new description for this product """
        self.objects[self.buttons.DESCRIPTION].setText(description)

    def change_price(self, priceinpence):
        """ Set a new price for this product """
        self.objects[self.buttons.PRICE].setText("\xA3%.2f" % (priceinpence / 100))

    def draw(self, window):
        """ Redraw the product entry screen """
        window.fill(Colours.BG)

        for gui_object in self.objects.values():
            gui_object.draw(window)

        if self.banner is not None:
            self.banner.draw(window)

        pygame.display.flip()
