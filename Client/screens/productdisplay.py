'''
productdisplay.py

Classes to handle display of products on snackspace main screen
'''

from __future__ import division

from const import Const

from screens.displayconstants import Colours

from LCARSGui import LCARSCappedBar, CapLocation

class ProductDisplay():

    """
    Class representing the display objects for a single product entry
    """
    
    def __init__(self, product):

        self.product = product

        self.formats = Const()
        self.formats.desc_pence = "%s (%dp)"
        self.formats.desc_pounds = u"%s (\xA3%.2f)"

        self.formats.price_pence = "%dp"
        self.formats.price_pounds = "\xA3%.2f"

        self.lcars_objects = [None] * 3

        self.description = ''
        self.price_string = ''
        
        self.visible = True
    
    def set_visible(self, visible):
        """ Sets the visible state of the product display """ 
        self.visible = visible
        
    def collide_on_remove(self, pos):
        """ Remove the product entry at the given position """
        collide = False

        if self.visible:
            try:
                collide = self.lcars_objects[2].collidePoint(pos)
            except AttributeError:
                # Off-screen products might not have GUI objects.
                # This is OK.
                pass

        return collide

    def update_strings(self):
        """ Sets internal strings from the associated snackspace product """
        description = self.product.description
        priceinpence = self.product.price_in_pence
        totalprice = self.product.total_price

        self.description = self.format_desciption(description, priceinpence)
        self.price_string = self.format_price(totalprice)

    def format_desciption(self, description, priceinpence):
        """ Returns a formatted description string """
        if (priceinpence < 100):
            description = self.formats.desc_pence % (description, priceinpence)
        else:
            description = self.formats.desc_pounds % (description, int(priceinpence) / 100)

        return description

    def format_price(self, price_in_pence):
        """ Returns a formatted price string """
        if (price_in_pence < 100):
            price_string = self.formats.price_pence % price_in_pence
        else:
            price_string = self.formats.price_pounds % (int(price_in_pence) / 100)

        return price_string

    def draw(self, layout, index, remove_width, window):

        """
        Draws the three product LCARS objects with the requested layout, y position and remove button width
        """
        
        self.update_strings()

        # Redraw description bar
        self.lcars_objects[0] = LCARSCappedBar(
                layout.get_description_rect(index),
                CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, self.description, Colours.FG, Colours.BG, self.visible)

        self.lcars_objects[0].draw(window)

        # Redraw total price bar
        self.lcars_objects[1] = LCARSCappedBar(
                layout.get_price_rect(index),                              
                CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, self.price_string, Colours.FG, Colours.BG, self.visible)

        self.lcars_objects[1].draw(window)

        # Redraw remove button
        self.lcars_objects[2] = LCARSCappedBar(
                layout.get_remove_rect(index, remove_width),
                CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "Remove", Colours.FG, Colours.BG, self.visible)

        self.lcars_objects[2].draw(window)

class ProductDisplayCollection():
    
    """
    A collection of product display objects
    """
    
    def __init__(self, display_limit):
        
        # Array of ProductDisplays
        self.product_displays = []
        self.top_index = 0
        self.display_limit = display_limit
    
    def __iter__(self):
        return iter(self.product_displays)
    
    def __len__(self):
        return len(self.product_displays)
    
    def __getitem__(self, key):
        return self.product_displays[key]
        
    def __delitem__(self, key):
        self.remove(key)
    
    def __setitem__(self, key):
        pass
    
    def add(self, product):
        """ Add a new product to the list """
        if product not in [displayproduct.product for displayproduct in self.product_displays]:
            self.product_displays.append(ProductDisplay(product))
            
    def get_at_position(self, pos):
        """ Get the product at a specific location """
        product = next((product.product for product in self.product_displays if product.collide_on_remove(pos)), None)
        return product

    def remove(self, product_to_remove):
        """ Delete a product entry from the list """
        self.product_displays = [product for product in self.product_displays if product_to_remove != product.product]

        if self.top_index > 0:
            self.top_index -= 1
            
    def move_up(self):
        """ Shift the displayed products list up """
        if self.top_index > 0:
            self.top_index -= 1

    def move_down(self):
        """ Shift the displayed products list down """
        if (self.top_index + self.display_limit) < len(self.product_displays):
            self.top_index += 1
    
    def collide_on_remove(self, pos):
        """ Return the product if its remove button was pressed """
        found_product = None
        for product in self.product_displays:
            if product.collide_on_remove(pos):
                found_product = product
        
        return found_product
    
    def clear(self):
        """ Reset the products list to nothing """
        self.product_displays = []
        self.top_index = 0
        