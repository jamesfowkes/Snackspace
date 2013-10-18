'''
const.py

Simple class for defining constants
'''

from copy import deepcopy

class ConstSetException(Exception):
    """ When attempting to set a constant, this is thrown """
    def __init__(self, value): #pylint: disable=W0231
        self.value = value
    def __str__(self):
        repr(self.value)
        
class Const(object): #pylint: disable=R0902,R0903

    """ A small class for holding constants """
    def __setattr__(self, name, value):
        if self.__dict__.has_key(name):
            raise ConstSetException("Attempt to set the value of a constant")
        self.__dict__[name] = value

    def __getattr__(self, name, value):
        if self.__dict__.has_key(name):
            return deepcopy(self.__dict__[name])

    def __delattr__(self, item):
        if self.__dict__.has_key(item):
            print 'NOOOOO' # throw exception if needed