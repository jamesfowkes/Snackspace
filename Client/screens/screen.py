"""
screen.py
"""

class Screen: #pylint: disable=R0921
    
    """ Defines a standard interface for a snackspace screen
    pylint R0921 disable - this class is referenced """
    
    def __init__(self, manager, owner, screen_id):
        self.screen_manager = manager
        self.owner = owner
        self.last_gui_position = None
        self.last_keypress = ''
        self.screen_id = screen_id
        self.active = False
        
    def set_active(self, state):
        """
        Active state can be changed by the screen manager
        """
        if (not self.active) and state:
            #On transition from inactive->active, update the GUI
            self.active = state
            self._update_on_active()
        else:
            #Otherwise, just set new the active state
            self.active = state
    
    def _update_on_active(self):
        """ Called when active state changes """
        raise NotImplementedError
    
    def on_gui_event(self, pos):
        """ Called when a GUI event is is triggered """
        raise NotImplementedError
    
    def on_scan(self, product):
        """ Called when a product is scanned """
        raise NotImplementedError
    
    def on_bad_scan(self, badcode):
        """ Called when an unknown product is scanned """
        raise NotImplementedError
    
    def on_key_event(self, key):
        """ Called on keyboard press """
        raise NotImplementedError

    def on_rfid(self):
        """ Called when a known RFID is scanned """
        raise NotImplementedError
    
    def on_bad_rfid(self):
        """ Called when an unknown RFID is scanned """
        raise NotImplementedError
    