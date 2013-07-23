"""
display_constants.py

Constant values for layout, color, etc.

pylint message C0103 disabled due to requiring UPPERCASE identifiers for constants
and Proper Case for classes/collections
"""

from enum import Enum
from const import Const

# Available snackspace screens
Screens = Enum("BLANKSCREEN", "INTROSCREEN", "MAINSCREEN", "NUMERICENTRY", "PRODUCTENTRY", "WAITING") #pylint: disable=C0103

# Global widths for LCARS style interface
Widths = Const() #pylint: disable=C0103
Widths.BORDER = 20  #pylint: disable=W0201,C0103
Widths.LARGE_BAR = 60 #pylint: disable=W0201,C0103
Widths.SMALL_BAR = 30 #pylint: disable=W0201,C0103

# Global colour pallette
Colours = Const() #pylint: disable=C0103
Colours.BG =    (  0,   0,   0) #pylint: disable=W0201,C0103
Colours.FG =    ( 40,  89,  45) #pylint: disable=W0201,C0103
Colours.WARN =  (255, 255,   0) #pylint: disable=W0201,C0103
Colours.ERR =   (255,   0,   0) #pylint: disable=W0201,C0103
Colours.INFO =  (  0, 255,   0) #pylint: disable=W0201,C0103
Colours.ENTRY = (  0, 128,   0) #pylint: disable=W0201,C0103

# Name of sound file for touchscreen press 
SOUNDFILE = "press_sound.ogg"
