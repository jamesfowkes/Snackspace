import sys
import pygame #@UnresolvedImport

import argparse #@UnresolvedImport

import ConfigParser

import logging

import time

from rfid import RFIDReader

from bunch import Bunch

from constants import Screens

from product import Product
from user import User

from dbclient import DbClient

from screens.introscreen import IntroScreen
from screens.numericentry import NumericEntry
from screens.mainscreen import MainScreen
from screens.productentry import ProductEntry

class Task:
	def __init__(self, func, time, active):
		self.Function = func
		self._period = time
		self.Ticks = time
		self.Active = active			
	
	def Reload(self):
		self.Ticks = self._period
		
class TaskHandler:
			
	def __init__(self, parent):
		self._tasks = []
		self._parent = parent
	
	def addFunction(self, function, time, active = True):
		newTask = Task(function, time, active)
		self._tasks.append(newTask)
		
	def tick(self):
		for t in self._tasks:
			if t.Active and t.Ticks > 0:
				t.Ticks -= 1
				if t.Ticks == 0:
					t.Reload()
					t.Function()

class Snackspace:
	
	def __init__(self, window, size, localdb, rfid_port=None, limitAction='ignore', creditAction='disallow'):
		
		self.inittime = int(time.time())
		
		self.window = window
		self.width = size[0]
		self.height = size[1]
		
		self.localdb = localdb
		self.rfid_port = rfid_port
		self.limitAction = limitAction
		self.creditAction = creditAction
		
		self.__setConstants()
		
		self.__setVariables()
		
		self.ScreenFunctions = Bunch(
			RequestScreen = self.__RequestScreen)		
	
		self.UserFunctions = Bunch(
			Get=lambda: self.user,
			ChargeAll = self.__ChargeAll,
			PayDebt = self.__CreditUser,
			Forget = self.__ForgetUser
			)
		
		self.ProductFunctions = Bunch(
			RequestAllProducts = self.__RequestAllProducts,
			TotalPrice = self.__TotalPrice,
			RemoveProduct = self.__RemoveProduct,
			RemoveAll = self.__RemoveAllProducts,
			NewProducts = self.__NewProducts
			)
		
		# Instantiate all the screens now
		self.screens = {
			Screens.INTROSCREEN.value	: IntroScreen(self.width, self.height, self.ScreenFunctions, self.UserFunctions, self.ProductFunctions),
			Screens.NUMERICENTRY.value	: NumericEntry(self.width, self.height, self.ScreenFunctions, self.UserFunctions),
			Screens.MAINSCREEN.value	: MainScreen(self.width, self.height, self.ScreenFunctions, self.UserFunctions, self.ProductFunctions),
			Screens.PRODUCTENTRY.value	: ProductEntry(self.width, self.height, self.ScreenFunctions, self.ProductFunctions)
			}
		
		self.screens[Screens.INTROSCREEN.value].acceptGUIEvents = False
		self.screens[Screens.NUMERICENTRY.value].acceptGUIEvents = True
		self.screens[Screens.MAINSCREEN.value].acceptGUIEvents = True
		
		self.currentscreen = Screens.BLANKSCREEN
		self.__setScreen(Screens.INTROSCREEN)
		
		self.screens[Screens.INTROSCREEN.value].setDbState(self.dbaccess.isConnected)
		
		if not self.dbaccess.isConnected:
			self.logger.warning("Could not find remote database")
			self.__setScreen(Screens.INTROSCREEN)
		else:
			self.logger.debug("Found remote database")
			self.screens[Screens.INTROSCREEN.value].acceptGUIEvents = True
		
		self.oldConnectState = self.dbaccess.isConnected
		
	def StartEventLoop(self):
		
		ticks = 0
		
		while (1):
			for event in pygame.event.get():
				if event.type == pygame.QUIT: sys.exit()
				if event.type == pygame.MOUSEBUTTONUP:
					self.logger.debug("GUI Event")
					try:
						self.screens[self.currentscreen.value].OnGuiEvent(event.pos)
					except AttributeError:  # Screen does not handle Gui events
						if "OnGuiEvent" in dir(self.screens[self.currentscreen.value]):
							raise  # # Only raise error if the OnGuiEvent method exists
				if event.type == pygame.KEYDOWN:
					self.__inputHandler(event)
			
			if (pygame.time.get_ticks() - ticks) > 0:
				
				ticks = pygame.time.get_ticks()
				
				self.taskHandler.tick()
	
	def rfidTask(self):
		if self.rfid is not None:
			rfid = self.rfid.PollForCardID()
		else:
			rfid = self.dummyRFID
			self.dummyRFID = []
	
		if len(rfid):
			self.__onSwipeEvent(self.__mangleRFID(rfid))
	
	def dbTask(self):
		connected = self.dbaccess.PingServer()
		
		if connected != self.oldConnectState:
			self.screens[Screens.INTROSCREEN.value].setDbState(connected)
			self.__setScreen(Screens.INTROSCREEN, True)
			if not connected:
				self.logger.debug("Lost server connection.")
				self.screens[Screens.MAINSCREEN.value].clearAll()
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
		if (event.key in self.validKeys):
			#Add new keypress to buffer
			self.scannedinput += event.dict['unicode']
			
		elif (event.key == pygame.K_RETURN):
			## Buffer is complete, process it
			self.logger.debug("Got raw input '%s'" % self.scannedinput)
			self.__onScanEvent(self.scannedinput)
			
			self.scannedinput = ''
				
		elif (event.key == pygame.K_a) and (pygame.key.get_mods() & pygame.KMOD_CTRL):
			## Go to product entry screen
			self.__setScreen(Screens.PRODUCTENTRY)
			
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
						
		for screen in self.screens.values():
			if self.user is not None:
				try:
					screen.OnRFID()
				except AttributeError:
					if "OnRFID" in dir(screen):
						raise  # # Only raise error if the method exists
			else:
				try:
					screen.OnBadRFID()
				except AttributeError:
					if "OnBadRFID" in dir(screen):
						raise  # # Only raise error if the method exists
			
	def __onScanEvent(self, barcode):
		
		if not self.dbaccess.isConnected or len(barcode) == 0:
			return
		
		newproduct = self.__AddProduct(barcode)
		
		if newproduct is not None:
			for screen in self.screens.values():
				try:
					screen.OnScan(newproduct, barcode)
				except AttributeError:
					if "OnScan" in dir(screen):
						raise  # # Only raise error if the method exists
		else:
			for screen in self.screens.values():
				try:
					screen.OnBadScan(barcode)
				except AttributeError:
					if "OnBadScan" in dir(screen):
						raise  # # Only raise error if the method exists
					
	def __setScreen(self, newscreen):
		
		valid = False
		if (newscreen.value == self.currentscreen.value) or self.__isValidTransition(newscreen):
			self.logger.debug("Changing screen from %s to %s" % (self.currentscreen.str, newscreen.str))
			
			if self.currentscreen.value != -1:
				self.screens[self.currentscreen.value].setActive(False)
			self.currentscreen = newscreen
			self.screens[newscreen.value].setActive(True)
			
			valid = True
			self.screens[newscreen.value].draw(self.window)
		else:
			self.logger.debug("Could not change screen from %s to %s" % (self.currentscreen.str, newscreen.str))
				
		return valid

	def __isValidTransition(self, newscreen):
		
		validTransitions = self.validScreenTransitions[self.currentscreen]	
		return newscreen in validTransitions
	
	def __setConstants(self):
		self.validKeys = [
			pygame.K_0, pygame.K_1, 	pygame.K_2, pygame.K_3, pygame.K_4,
			pygame.K_5, pygame.K_6, 	pygame.K_7, pygame.K_8, pygame.K_9
		]
	
	def __setVariables(self):
		self.scannedinput = ''
		
		self.dbaccess = DbClient(self.localdb)
		
		self.logger = logging.getLogger("snackspace")
		
		if self.rfid_port != 'dummy':
			self.rfid = RFIDReader(self.rfid_port);
		else:
			self.rfid = None
			self.dummyRFID = []

		self.user = None
		self.products = []

		self.validScreenTransitions = {
			Screens.BLANKSCREEN		: [Screens.INTROSCREEN],
			Screens.INTROSCREEN		: [Screens.MAINSCREEN, Screens.PRODUCTENTRY],
			Screens.MAINSCREEN		: [Screens.INTROSCREEN, Screens.NUMERICENTRY],
			Screens.NUMERICENTRY	: [Screens.MAINSCREEN],
			Screens.PRODUCTENTRY	: [Screens.INTROSCREEN]
			}
				
		self.taskHandler = TaskHandler(self)
		self.taskHandler.addFunction(self.rfidTask, 500, True)
		self.taskHandler.addFunction(self.dbTask, 5000, True)

	def __RequestScreen(self, screen):
		self.__setScreen(screen)
						
	def __ChargeAll(self):
		if self.user is not None:
			products = [(product.Barcode, product.Count) for product in self.products]
			return self.dbaccess.SendTransactions(products, self.user.MemberID)
		else:
			return False
		
	def __CreditUser(self, amount):
		self.user.addCredit(amount)
		return self.dbaccess.AddCredit(self.user.MemberID, amount)
	
	def __ForgetUser(self):
		self.user = None
					
	def __RequestUser(self):
		return None
	
	def __RequestAllProducts(self):
		return None
		
	def __AddProduct(self, barcode):
		
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
		
	def __TotalPrice(self):
		return sum([product.TotalPrice for product in self.products])
		
	def __RemoveProduct(self, productToRemove):
		
		if productToRemove.Decrement() == 0:
			self.products = [product for product in self.products if product != productToRemove]
				
		return productToRemove.Count
		
	def __RemoveAllProducts(self):
		self.products = []

	def __NewProducts(self, productlist):
		pass
	
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

	s.StartEventLoop()

if __name__ == "__main__":
	main()
