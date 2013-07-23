"""
screen_gui.py

Base class for a snackspace screen GUI
"""

import pygame #@UnresolvedImport

from threading import Timer

from screens.displayconstants import Colours, Widths

from LCARSGui import LCARSCappedBar, CapLocation

class Banner(LCARSCappedBar):
    
    """ A banner to be shown for a period of time """
    def __init__(self, x_full, y_full, text, colour):
        
        #pylint: disable=W0231
        self.x_full = x_full
        self.y_full = y_full
        self.banner_text = text
        self.colour = colour
        self.banner_width = self.x_full * 0.6
        self.refresh()
        
    def set_width_fraction(self, fraction):
        """ Change the default width fraction for this banner """
        self.banner_width = self.x_full * fraction
        self.refresh()
    
    def refresh(self):
        """ Recalculate the position and dimensions for this banner """
        x = (self.x_full - self.banner_width) / 2 #pylint: disable=C0103
        y = (self.y_full - Widths.LARGE_BAR) / 2 #pylint: disable=C0103
        
        LCARSCappedBar.__init__(self, 
            pygame.Rect(x, y, self.banner_width, Widths.LARGE_BAR),
            CapLocation.CAP_RIGHT + CapLocation.CAP_LEFT, self.banner_text, self.colour, Colours.BG , True)

        
class ScreenGUI:

    """ The implementation of the screen GUI """
    
    def __init__(self, width, height, owner):
        self.screen = owner
        self.width = width
        self.height = height
        self.last_press_id = -1
        self.banner = None
        self.timer = None
        self.objects = {}
        
        try:
            pass #self.sound = pygame.mixer.Sound(SOUNDFILE)
        except:
            raise

    def get_object_id(self, pos):

        """ Return the ID of the object clicked """

        object_id = -1

        if self.screen.active:
            for key, gui_object in self.objects.items():
                if gui_object.collidePoint(pos) and gui_object.visible:
                    object_id = key
                    break

            if object_id > -1:
                self.last_press_id = object_id

        return object_id

    def play_sound(self):
        """ Play the GUI click sound """
        pass #self.sound.play()

    def set_banner_width_fraction(self, fraction):
        """Set the banner width as a fraction of the screen width """
        self.banner.set_width_fraction(fraction)
        
    def set_banner_with_timeout(self, text, timeout, colour, callback):
        """ Displays a banner on the screen with a timeout.
        Calls callback when timeout expires """
        try:
            self.timer.cancel()
        except AttributeError:
            pass

        self.banner = Banner(self.width, self.height, text, colour)

        if timeout > 0:
            self.timer = Timer(timeout, callback)
            self.timer.start()


    def hide_banner(self):
        """ Allows a banner to be hidden ahead of any timeout expiring"""
        try:
            self.timer.cancel()
        except AttributeError:
            pass
        self.banner = None