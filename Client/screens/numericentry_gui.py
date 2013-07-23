"""
numericentry_gui.py
"""

from __future__ import division

import pygame #@UnresolvedImport

from enum import Enum

from screens.displayconstants import Widths, Colours

from LCARSGui import LCARSCappedBar, CapLocation

from screens.border import Border
from screens.screen_gui import ScreenGUI

class NumericEntryGUI(ScreenGUI):
    
    """ Describes the graphical elements of the numeric entry screen """
    
    def __init__(self, width, height, owner):

        ScreenGUI.__init__(self, width, height, owner)

        border = Border(width, height)

        ##
        ## Fixed position objects
        ##

        buttonw = 100
        largebuttonw = buttonw * 2
        amountentryw = (buttonw * 4) + (Widths.BORDER * 4)

        ## Column and row x, y locations
        cx = [0, 0, 0, 0] #pylint: disable=C0103
        cx[0] = 200
        cx[1] = cx[0] + buttonw + Widths.BORDER
        cx[2] = cx[1] + buttonw + Widths.BORDER
        cx[3] = cx[2] + buttonw + Widths.BORDER + Widths.BORDER
        buttonh = 50
        amountentryh = buttonh * 1.5

        ry = [0, 0, 0, 0] #pylint: disable=C0103
        ry[0] = 125
        ry[1] = ry[0] + amountentryh + Widths.BORDER
        ry[2] = ry[1] + buttonh + Widths.BORDER
        ry[3] = ry[2] + buttonh + Widths.BORDER
        r5y = ry[3] + buttonh + Widths.BORDER
        r6y = r5y + buttonh + Widths.BORDER

        cancelbuttonx = cx[3] + buttonw - largebuttonw #Right align the "cancel" button
        
        self.keys = Enum("KEY0", "KEY1", "KEY2", "KEY3", "KEY4", "KEY5", "KEY6", "KEY7", "KEY8", "KEY9",
        "FIVEPOUNDS", "TENPOUNDS", "TWENTYPOUNDS", "DONE", "CANCEL", "AMOUNT")
        
        self.objects = {
                self.keys.AMOUNT : LCARSCappedBar(pygame.Rect(cx[0], ry[0], amountentryw, amountentryh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "\xA30.00", Colours.FG, Colours.BG, True),

                self.keys.KEY0 : LCARSCappedBar(pygame.Rect(cx[0], r5y, buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "0", Colours.FG, Colours.BG, True),
                self.keys.KEY1 : LCARSCappedBar(pygame.Rect(cx[0], ry[3], buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "1", Colours.FG, Colours.BG, True),
                self.keys.KEY2 : LCARSCappedBar(pygame.Rect(cx[1], ry[3], buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "2", Colours.FG, Colours.BG, True),
                self.keys.KEY3 : LCARSCappedBar(pygame.Rect(cx[2], ry[3], buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "3", Colours.FG, Colours.BG, True),
                self.keys.KEY4 : LCARSCappedBar(pygame.Rect(cx[0], ry[2], buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "4", Colours.FG, Colours.BG, True),
                self.keys.KEY5 : LCARSCappedBar(pygame.Rect(cx[1], ry[2], buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "5", Colours.FG, Colours.BG, True),
                self.keys.KEY6 : LCARSCappedBar(pygame.Rect(cx[2], ry[2], buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "6", Colours.FG, Colours.BG, True),
                self.keys.KEY7 : LCARSCappedBar(pygame.Rect(cx[0], ry[1], buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "7", Colours.FG, Colours.BG, True),
                self.keys.KEY8 : LCARSCappedBar(pygame.Rect(cx[1], ry[1], buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "8", Colours.FG, Colours.BG, True),
                self.keys.KEY9 : LCARSCappedBar(pygame.Rect(cx[2], ry[1], buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "9", Colours.FG, Colours.BG, True),

                self.keys.FIVEPOUNDS :       LCARSCappedBar(pygame.Rect(cx[3], ry[1], buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, u"\xA35", Colours.FG, Colours.BG, True),
                self.keys.TENPOUNDS :        LCARSCappedBar(pygame.Rect(cx[3], ry[2], buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, u"\xA310", Colours.FG, Colours.BG, True),
                self.keys.TWENTYPOUNDS :     LCARSCappedBar(pygame.Rect(cx[3], ry[3], buttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, u"\xA320", Colours.FG, Colours.BG, True),

                self.keys.DONE : LCARSCappedBar(pygame.Rect(cx[0], r6y, largebuttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "Done", Colours.FG, Colours.BG, True),
                self.keys.CANCEL : LCARSCappedBar(pygame.Rect(cancelbuttonx, r6y, largebuttonw, buttonh), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "Cancel", Colours.FG, Colours.BG, True),
                }

        ##
        ## Import standard objects

        self.objects.update(border.get_border())

        ##
        ## Position-dependant objects
        ##

    def update_amount(self, amount):
        """ Set the total amount text """
        self.objects[self.keys.AMOUNT].setText("\xA3%.2f" % (amount / 100))

    def draw(self, window):
        """ Redraw the numeric entry screen """
        window.fill(Colours.BG)

        for gui_object in self.objects.values():
            gui_object.draw(window)

        pygame.display.flip()
