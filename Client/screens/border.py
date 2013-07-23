"""
border.py
"""
import pygame #@UnresolvedImport

from screens.displayconstants import Widths, Colours

from LCARSGui import LCARSText, TextAlign, LCARSSweep, LCARSCappedBar, CapLocation

##
## Standard Border for all Snackspace LCARS screens
##

class Border:
    """ Defines objects for the Snackspace border (LCARS sweep and title text) """
    def __init__(self, width, height):

        self.ENDCAP = -1    #pylint: disable=C0103
        self.TEXT = -2    #pylint: disable=C0103
        self.SWEEP = -3    #pylint: disable=C0103

        capped_bar_length = width / 16
        sweep_end_y = height - Widths.BORDER
        sweep_height = sweep_end_y - Widths.BORDER

        self.objects = {
                self.ENDCAP : LCARSCappedBar(pygame.Rect(width - Widths.BORDER - capped_bar_length, 
                                        Widths.BORDER, capped_bar_length, Widths.LARGE_BAR),
                                        CapLocation.CAP_RIGHT, '', Colours.FG, Colours.BG, True)
                }

        ## The title text is to the immediate left of the endcap
        text_right = self.objects[self.ENDCAP].l() - Widths.BORDER
        self.objects[self.TEXT] = LCARSText((text_right, Widths.BORDER + Widths.LARGE_BAR/2),
                "SNACKSPACE v1.0",
                80,
                TextAlign.XALIGN_RIGHT, Colours.FG, Colours.BG, True)

        ## The sweep starts at the immediate left of the text
        sweep_end_x = self.objects[self.TEXT].l() - Widths.BORDER
        sweep_width = sweep_end_x - Widths.BORDER

        self.objects[self.SWEEP] = LCARSSweep(
                pygame.Rect(Widths.BORDER, Widths.BORDER, sweep_width, sweep_height),
                'TL', Widths.SMALL_BAR, Widths.LARGE_BAR, Colours.FG, Colours.BG, True)

    def inner_y(self):
        """
        The sweep defines the inner edge of the snackspace screen
        Return the y location of the inner edge of the border
        """
        return self.objects[self.ENDCAP].b()

    def inner_x(self):
        """
        The sweep defines the inner edge of the snackspace screen
        Return the x location of the inner edge of the border
        """
        return self.objects[self.SWEEP].l()

    def bottom(self):
        """ y-coordinate of the bottom of the sweep """
        return self.objects[self.SWEEP].b()

    def get_border(self):
        """ The LCARS objects constituting the border """
        return self.objects
