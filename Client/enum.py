"""
enum.py
""" 
   
def Enum(*sequential, **named): #pylint: disable=C0103
    """ Simple C-like enumeration class. Each item available as integer """ 
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)