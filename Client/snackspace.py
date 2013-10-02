"""
snackspace

A "self-checkout" application for Nottingham Hackspace

Intended to run on a raspberry pi with USB barcode scanner and serial RFID reader

Communicates with server-side snackspace application via XML packets over TCP socket
"""

import sys
import pygame #@UnresolvedImport

import argparse #@UnresolvedImport

import ConfigParser

import logging

import time

from rfid import RFIDReader

from screenmanager import Screens

from product import Product
from user import User

from dbclient import DbClient

from screenmanager import ScreenManager

from task import TaskHandler

from collections import namedtuple

SnackspaceOptions = namedtuple("SnackspaceOptions", "localdb rfid_port limit_action credit_action") #pylint: disable=C0103

class InputHandler: #pylint: disable=R0903
    """ Implements functionality for managing keyboard input """
    
    NEW_SCANNED_INPUT = 0
    PRODUCT_ENTRY = 1
    FAKE_RFID = 2
    FAKE_GOOD_PRODUCT = 3
    FAKE_BAD_PRODUCT = 4
    QUIT = 5
    
    def __init__(self):
        """ Initialise the class """
        self.scanned_input = ''
        
        ## Only numeric keys are valid
        self.valid_scan_keys = [
                pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9
        ]
        
    def new_event(self, event):
        """ For each key event, translate into appropriate snackspace event """ 
        key = event.dict['unicode']
        result = None
           
        if (event.key in self.valid_scan_keys):
            #Add new keypress to buffer
            self.scanned_input += key
    
        elif (event.key == pygame.K_RETURN):
            result = self.NEW_SCANNED_INPUT
    
        elif (event.key == pygame.K_a) and (pygame.key.get_mods() & pygame.KMOD_CTRL):
            result = self.PRODUCT_ENTRY
    
        elif (event.key == pygame.K_u) and (pygame.key.get_mods() & pygame.KMOD_CTRL):
            result = self.FAKE_RFID
    
        elif (event.key == pygame.K_p) and (pygame.key.get_mods() & pygame.KMOD_CTRL):
            result = self.FAKE_GOOD_PRODUCT
    
        elif (event.key == pygame.K_f) and (pygame.key.get_mods() & pygame.KMOD_CTRL):
            result = self.FAKE_BAD_PRODUCT
        
        elif (event.key == pygame.K_c) and (pygame.key.get_mods() & pygame.KMOD_CTRL):
            result = self.QUIT
            
        return result

class Snackspace: #pylint: disable=R0902
    """ Implements the main snackspace class. Responsible for:
    DB and screen managers
    RFID and barcode scanners
    UI interaction via pygame
    pylint R0902 disabled: too many instance attributes
    """
    def __init__(self, window, size, options):

        """ Initialise and start the snackspace application """
        
        self.inittime = int(time.time())

        self.options = options

        self.input_handler = InputHandler()
        
        self.task_handler = TaskHandler(self)
        self.task_handler.add_function(self.rfid_task, 500, True)
        self.task_handler.add_function(self.db_task, 60000, True)
        
        self.dbaccess = DbClient(self.options.localdb, self.task_handler)

        self.logger = logging.getLogger("snackspace")

        self.rfid = RFIDReader(self.options.rfid_port)
        
        self.screen_manager = ScreenManager(self, window, size)
        self.screen_manager.get(Screens.INTROSCREEN).set_db_state(self.dbaccess.found_server)

        self.user = None
        self.products = []

        if not self.dbaccess.found_server:
            self.logger.warning("Could not find remote database")
            self.screen_manager.req(Screens.INTROSCREEN)
        else:
            self.logger.debug("Found remote database")
            self.screen_manager.get(Screens.INTROSCREEN).active = True

    def start(self):
        """ The main snackspace event loop """
        ticks = 0

        while (1):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    self.logger.debug("GUI Event")
                    self.screen_manager.current.on_gui_event(event.pos)

                if event.type == pygame.KEYDOWN:
                    self.keypress(event)

            if (pygame.time.get_ticks() - ticks) > 0:

                ticks = pygame.time.get_ticks()

                self.task_handler.tick()

    def keypress(self, event):
        """ Handle a keyboard press or barcode scan character """ 
        # Push keypress to the current screen
        self.screen_manager.current.on_key_event(event.dict['unicode'])
        
        # Then do our own handling via the input handler
        result = self.input_handler.new_event(event)
        
        if result == InputHandler.FAKE_BAD_PRODUCT:
            ## Fake a bad product scan
            self.on_scan_event('BADBARCODE')
            
        elif result == InputHandler.FAKE_GOOD_PRODUCT:
            ## Fake a good product scan
            data = self.dbaccess.get_random_product()
            self.on_scan_event(data[0])
            
        elif result == InputHandler.FAKE_RFID:
            ## Fake an RFID swipe
            self.rfid.set_fake_rfid()
                
        elif result == InputHandler.NEW_SCANNED_INPUT:
            ## Buffer is complete, process it
            scanned_input = self.input_handler.scanned_input
            self.input_handler.scanned_input = ''
            self.logger.debug("Got raw input '%s'" % scanned_input)
            self.on_scan_event(scanned_input)
        
        elif result == InputHandler.PRODUCT_ENTRY:
            ## Go to product entry screen
            self.screen_manager.req(Screens.PRODUCTENTRY)
        
        elif result == InputHandler.QUIT:
            sys.exit()

    def rfid_task(self):
        """ To be run periodically to check for an RFID swipe """
        rfid = self.rfid.poll()
        
        if rfid is not None:
            self.on_swipe_event( self.rfid.mangle_rfid(rfid) )

    def db_task(self):
        """ To be run periodically to check the database status """
        was_connected = self.dbaccess.found_server
        connected = self.dbaccess.ping_server()

        if connected != was_connected:
            self.screen_manager.get(Screens.INTROSCREEN).set_db_state(connected)
            self.screen_manager.get(Screens.INTROSCREEN)
            if not connected:
                self.logger.debug("Lost server connection.")
                self.screen_manager.get(Screens.MAINSCREEN).clear_all()
                self.forget_products()
                self.forget_user()
            else:
                self.logger.debug("Got server connection.")

    def on_swipe_event(self, cardnumber):
        """ When an RFID swipe is made, gets user from the database """
        if not self.dbaccess.found_server:
            return

        userdata = self.dbaccess.get_user_data(cardnumber)

        if userdata is not None:
            self.user = User(*userdata, options = self.options) #pylint: disable=W0142
            self.logger.debug("Got user %s" % self.user.name)
        else:
            self.logger.debug("Bad RFID %s" % cardnumber)

        if self.user is not None:
            self.screen_manager.current.on_rfid()
        else:
            self.screen_manager.current.OnBadRFID()

    def on_scan_event(self, barcode):
        """ When a barcode scan is made, pulls product from the database """ 
        if not self.dbaccess.found_server or len(barcode) == 0:
            return

        newproduct = self.add_product_to_basket(barcode)

        if newproduct is not None:
            self.screen_manager.current.on_scan(newproduct)
        else:
            self.screen_manager.current.on_bad_scan(barcode)

    def charge_all(self):
        """ Charge the current user for the current set of products """ 
        success = False
        if self.user is not None:
            products = [(product.barcode, product.count) for product in self.products]
            success = self.dbaccess.send_transactions(products, self.user.member_id)
        else:
            success =  False

        if (self.user.credit > 0):
            success = success and self.dbaccess.add_credit(self.user.member_id, self.user.credit)

        return success

    def credit_user(self, amount):
        """ Adds credit to a user's account """
        self.user.add_credit(amount)

    def forget_user(self):
        """ Clear the user """
        self.user = None

    def total_price(self):
        """ Get the total price of the basket """
        return sum([product.total_price for product in self.products])

    def remove_product(self, product_to_remove):
        """ Remove a product from the basket """
        
        # First reduce the count of this product.
        # If zero, the product itself can be removed from the list
        if product_to_remove.decrement() == 0:
            self.products = [product for product in self.products if product != product_to_remove]

        return product_to_remove.count

    def forget_products(self):
        """ Delete the product basket """
        self.products = []

    def new_product(self, barcode, description, priceinpence):
        """ Add a new product to the database """
        return self.dbaccess.add_product(barcode, description, priceinpence)

    def add_product_to_basket(self, barcode):
        """ Adds a new scanned product to the list ('basket') of scanned products """
        product = next((product for product in self.products if barcode == product.barcode), None)

        if product is not None:
            product.increment() # Product already exists once, so just increment its count
        else:
            #Otherwise need to get product info from the database
            productdata = self.dbaccess.get_product(barcode)

            product = None

            if productdata:
                product = Product(*productdata) #pylint: disable=W0142

                if product is not None and product.valid:
                    self.products.append(product)                 

        return product
    
def main(_argv=None):
    """ Entry point for snackspace client application """
    argparser = argparse.ArgumentParser(description='Snackspace Server')
    argparser.add_argument('-L', dest='local_mode', nargs='?', default='n', const='y')
    argparser.add_argument('-P', dest='rfid_port', nargs='?', default=None)
    argparser.add_argument('--limitaction', dest='limit_action', nargs='?', default='ignore')
    argparser.add_argument('--creditaction', dest='credit_action', nargs='?', default='disallow')
    argparser.add_argument('--file', dest='conffile', nargs='?', default='')

    args = argparser.parse_args()

    ## Read arguments from configuration file
    try:
        confparser = ConfigParser.ConfigParser()
        confparser.readfp(open(args.conffile))

    except IOError:
        ## Configuration file does not exist, or no filename supplied
        confparser = None

    pygame.init()
    
    size = [800, 600]

    window = pygame.display.set_mode(size)

    if confparser is None:
        local_mode = args.local_mode = 'y'
        rfid_port = args.rfid_port
        limit_action = args.limit_action
        credit_action = args.credit_action
    else:
        local_mode = confparser.get('ClientConfig','local_mode') == 'y'
        limit_action = confparser.get('ClientConfig','limit_action')
        credit_action = confparser.get('ClientConfig','credit_action')
        try:
            rfid_port = confparser.get('ClientConfig','rfid_port')
        except ConfigParser.NoOptionError:
            rfid_port = None
        
    options = SnackspaceOptions(local_mode, rfid_port, limit_action, credit_action)
    snackspace = Snackspace(window, size, options)

    logging.basicConfig(level=logging.DEBUG)

    snackspace.start()

if __name__ == "__main__":
    main()