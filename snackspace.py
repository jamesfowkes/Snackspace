import sys
import pygame #@UnresolvedImport

import argparse #@UnresolvedImport

import ConfigParser

import logging

import time

from rfid import RFIDReader

from constants import Screens

from product import Product
from user import User

from dbclient import DbClient

from screenmanager import ScreenManager

from task import TaskHandler

class Snackspace:
	
	def __init__(self, window, size, localdb, rfid_port=None, limitAction='ignore', creditAction='disallow'):
		
		self.inittime = int(time.time())
		
		width = size[0]
		height = size[1]
		
		self.localdb = localdb
		self.rfid_port = rfid_port
		self.limitAction = limitAction
		self.creditAction = creditAction
		
		self.validScanKeys = [
			pygame.K_0, pygame.K_1, 	pygame.K_2, pygame.K_3, pygame.K_4,
			pygame.K_5, pygame.K_6, 	pygame.K_7, pygame.K_8, pygame.K_9
		]
		
		self.scannedinput = ''
		
		self.dbaccess = DbClient(self.localdb)
		
		self.logger = logging.getLogger("snackspace")
		
		if self.rfid_port != 'dummy':
			self.rfid = RFIDReader(self.rfid_port);
		else:
			self.rfid = None
			self.dummyRFID = []

		self.ScreenManager = ScreenManager(self, window, width, height)
		self.ScreenManager.Get(Screens.INTROSCREEN).SetDbState(self.dbaccess.isConnected)
		
		self.user = None
		self.products = []
				
		self.taskHandler = TaskHandler(self)
		self.taskHandler.addFunction(self.__rfidTask, 500, True)
		self.taskHandler.addFunction(self.__dbTask, 60000, True)	
		
		if not self.dbaccess.isConnected:
			self.logger.warning("Could not find remote database")
			self.__setScreen(Screens.INTROSCREEN)
		else:
			self.logger.debug("Found remote database")
			self.ScreenManager.Get(Screens.INTROSCREEN).active = True
		
		self.oldConnectState = self.dbaccess.isConnected
	
	@property
	def User(self):
		return self.user
	
	def Start(self):
		
		ticks = 0
		
		while (1):
			for event in pygame.event.get():
				if event.type == pygame.QUIT: sys.exit()
				if event.type == pygame.MOUSEBUTTONUP:
					self.logger.debug("GUI Event")
					self.ScreenManager.Current.OnGuiEvent(event.pos)

				if event.type == pygame.KEYDOWN:
					self.__inputHandler(event)
			
			if (pygame.time.get_ticks() - ticks) > 0:
				
				ticks = pygame.time.get_ticks()
				
				self.taskHandler.tick()
	
	def __rfidTask(self):
		if self.rfid is not None:
			rfid = self.rfid.PollForCardID()
		else:
			rfid = self.dummyRFID
			self.dummyRFID = []
	
		if len(rfid):
			self.__onSwipeEvent(self.__mangleRFID(rfid))
	
	def __dbTask(self):
		
		connected = self.dbaccess.PingServer()
		
		if connected != self.oldConnectState:
			self.ScreenManager.Get(Screens.INTROSCREEN).setDbState(connected)
			self.__setScreen(Screens.INTROSCREEN, True)
			if not connected:
				self.logger.debug("Lost server connection.")
				self.ScreenManager.Get(Screens.MAINSCREEN).clearAll()
				self.__RemoveAllProducts()
				self.__ForgetUser()
			else:
				self.logger.debug("Got server connection.")
		self.oldConnectState = connected
			
	def __mangleRFID(self, rfid):
		
		mangled = ""
		
		for byte in rfid:
			mangled += "%02X" % byte
			
		print mangled
		return mangled 
		
	def __inputHandler(self, event):
		
		key = event.dict['unicode']
		
		self.__onKeyEvent(key)
		
		if (event.key in self.validScanKeys):
			#Add new keypress to buffer
			self.scannedinput += key
	
		elif (event.key == pygame.K_RETURN):
			## Buffer is complete, process it
			self.logger.debug("Got raw input '%s'" % self.scannedinput)
			self.__onScanEvent(self.scannedinput)
			
			self.scannedinput = ''
				
		elif (event.key == pygame.K_a) and (pygame.key.get_mods() & pygame.KMOD_CTRL):
			## Go to product entry screen
			self.ScreenManager.Req(Screens.PRODUCTENTRY)
			
		elif (event.key == pygame.K_u) and (pygame.key.get_mods() & pygame.KMOD_CTRL):
			## Fake an RFID swipe
			if self.rfid is None:
				self.dummyRFID = [0x1B, 0x7F, 0x2D, 0x2D]
			
		elif (event.key == pygame.K_p) and (pygame.key.get_mods() & pygame.KMOD_CTRL):
			## Fake a good product scan
			self.__onScanEvent('7613033126321')
					
		elif (event.key == pygame.K_f) and (pygame.key.get_mods() & pygame.KMOD_CTRL):
			## Fake a bad product scan
			self.__onScanEvent('BADBARCODE')
						
	def __onSwipeEvent(self, cardnumber):
		
		if not self.dbaccess.isConnected:
			return
		
		userdata = self.dbaccess.GetUserData(cardnumber)
		
		if userdata is not None:
			self.user = User(*userdata, limitAction = self.limitAction, allowCredit = self.creditAction)
			self.logger.debug("Got user %s" % self.user.Name)
		else:
			self.logger.debug("Bad RFID %s" % cardnumber)
						
		if self.user is not None:
			self.ScreenManager.Current.OnRFID()
		else:
			self.ScreenManager.Current.OnBadRFID()
			
	def __onScanEvent(self, barcode):
		
		if not self.dbaccess.isConnected or len(barcode) == 0:
			return
		
		newproduct = self.__addProductToBasket(barcode)
		
		if newproduct is not None:
			self.ScreenManager.Current.OnScan(newproduct)

		else:
			self.ScreenManager.Current.OnBadScan(barcode)
	
	def __onKeyEvent(self, key):
		self.ScreenManager.Current.OnKeyEvent(key)
	
	def ChargeAll(self):
		
		success = False
		if self.user is not None:
			products = [(product.Barcode, product.Count) for product in self.products]
			success = self.dbaccess.SendTransactions(products, self.user.MemberID)
		else:
			success =  False
		
		if (self.user.Credit > 0):
			success = success and self.dbaccess.AddCredit(self.user.MemberID, self.user.Credit)
			
		return success
		
	def CreditUser(self, amount):
		self.user.addCredit(amount)
	
	def ForgetUser(self):
		self.user = None
					
	def RequestAllProducts(self):
		return self.products
			
	def TotalPrice(self):
		return sum([product.TotalPrice for product in self.products])
		
	def RemoveProduct(self, productToRemove):
		
		if productToRemove.Decrement() == 0:
			self.products = [product for product in self.products if product != productToRemove]
				
		return productToRemove.Count
		
	def ForgetProducts(self):
		self.products = []

	def NewProduct(self, barcode, description, priceinpence):
		
		return self.dbaccess.AddProduct(barcode, description, priceinpence)
	
	def __addProductToBasket(self, barcode):
		
		product = next((product for product in self.products if barcode == product.Barcode), None)
		
		if product is not None:
			product.Increment()
		else:
			productdata = self.dbaccess.GetProduct(barcode) 
			
			if productdata:
				product = Product(*productdata)
				
				if product is not None and product.Valid:
					self.products.append(product)
				else:
					product = None
			
		return product
def main(argv=None):

	argparser = argparse.ArgumentParser(description='Snackspace Server')
	argparser.add_argument('-L', dest='localMode', nargs='?', default='n', const='y')
	argparser.add_argument('-P', dest='rfidPort', nargs='?', default='/dev/ttyUSB0')
	argparser.add_argument('--limitaction', dest='limitAction', nargs='?', default='ignore')
	argparser.add_argument('--creditaction', dest='creditAction', nargs='?', default='disallow')
	argparser.add_argument('--file', dest='conffile', nargs='?',default='')
	
	args = argparser.parse_args()
	
	## Read arguments from configuration file
	try:
		confparser = ConfigParser.ConfigParser()
		confparser.readfp(open(args.conffile))
		
	except IOError:
		## Configuration file does not exist, or no filename supplied
		confparser = None
		pass
	
	pygame.init()
	
	size = [800, 600]
	
	window = pygame.display.set_mode(size)
	
	if confparser is None:
		localMode = args.localMode = 'y'
		rfidPort = args.rfidPort
		limitAction = args.limitAction
		creditAction = args.creditAction
	else:
		localMode = confparser.get('ClientConfig','localmode') == 'y'
		rfidPort = confparser.get('ClientConfig','rfidport')
		limitAction = confparser.get('ClientConfig','limitaction')
		creditAction = confparser.get('ClientConfig','creditaction')
	
	s = Snackspace(window, size, localMode, rfidPort, limitAction, creditAction)
	
	logging.basicConfig(level=logging.DEBUG)

	s.Start()

if __name__ == "__main__":
	main()
