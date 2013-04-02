import sys
import pygame

import argparse

import logging

import time

from rfid import RFIDReader

from bunch import Bunch

from constants import Requests, Screens

from item import Item
from user import User

from dbremote import DbRemote

from screens.introscreen import IntroScreen
from screens.numericentry import NumericEntry
from screens.mainscreen import MainScreen
from screens.productentry import ProductEntry

class Snackspace:
	def __init__(self, window, size, localdb, rfid_port=None):
		
		self.inittime = int(time.time())
		
		self.window = window
		self.width = size[0]
		self.height = size[1]
		
		self.localdb = localdb
		self.rfid_port = rfid_port

		self.__setConstants__()
		
		self.__setVariables__()
		
		self.ScreenFunctions = Bunch(
			RequestScreen = self.__RequestScreen__)		
	
		self.UserFunctions = Bunch(
			Get=lambda: self.user,
			ChargeAll = self.__ChargeAll__,
			PayDebt = self.__CreditUser__,
			Forget = self.__ForgetUser__
			)
		
		self.ItemFunctions = Bunch(
			RequestAllItems = self.__RequestAllItems__,
			TotalPrice = self.__TotalPrice__,
			RemoveItem = self.__RemoveItem__,
			RemoveAll = self.__RemoveAllItems__,
			NewItems = self.__NewItems__)
		
		# Instantiate all the screens now
		self.screens = {
			Screens.INTROSCREEN.value	: IntroScreen(self.width, self.height, self.ScreenFunctions, self.UserFunctions, self.ItemFunctions),
			Screens.NUMERICENTRY.value	: NumericEntry(self.width, self.height, self.ScreenFunctions, self.UserFunctions),
			Screens.MAINSCREEN.value	: MainScreen(self.width, self.height, self.ScreenFunctions, self.UserFunctions, self.ItemFunctions),
			Screens.PRODUCTENTRY.value	: ProductEntry(self.width, self.height, self.ScreenFunctions, self.ItemFunctions)
			}
		
		self.screens[Screens.INTROSCREEN.value].acceptGUIEvents = False
		self.screens[Screens.NUMERICENTRY.value].acceptGUIEvents = True
		self.screens[Screens.MAINSCREEN.value].acceptGUIEvents = True
		
		self.currentscreen = Screens.BLANKSCREEN
		self.__setScreen__(Screens.INTROSCREEN, False)
		
		if not self.dbaccess.isConnected:
			self.logger.warning("Could not find remote database")
			self.screens[Screens.INTROSCREEN.value].setIntroText(
				"ERROR: Cannot access Snackspace remote database",
				(0xFF, 0, 0))
			self.__setScreen__(Screens.INTROSCREEN, True)
		else:
			self.logger.info("Found remote database")
			self.screens[Screens.INTROSCREEN.value].acceptGUIEvents = True
		
	def StartEventLoop(self):
		
		ticks = 0
		
		while (1):
			for event in pygame.event.get():
				if event.type == pygame.QUIT: sys.exit()
				if event.type == pygame.MOUSEBUTTONUP:
					self.logger.info("GUI Event")
					try:
						self.screens[self.currentscreen.value].OnGuiEvent(event.pos)
					except AttributeError:  # Screen does not handle Gui events
						if "OnGuiEvent" in dir(self.screens[self.currentscreen.value]):
							raise  # # Only raise error if the OnGuiEvent method exists
				if event.type == pygame.KEYDOWN:
					self.__inputHandler__(event)
			
			if (pygame.time.get_ticks() - ticks) > 1000:
				ticks = pygame.time.get_ticks()
				
				if self.rfid is not None:
					rfid = self.rfid.PollForCardID()
				else:
					rfid = self.fakeRFID
					self.fakeRFID = []
					
				if len(rfid):
					self.__onSwipeEvent__(self.__mangleRFID__(rfid))
	
	def __mangleRFID__(self, rfid):
		
		mangled = ""
		
		for byte in rfid:
			mangled += "%02X" % byte
			
		print mangled
		return mangled 
		
	def __inputHandler__(self, event):
		if (event.key in self.validKeys):
			#Add new keypress to buffer
			self.scannedinput += event.dict['unicode']
			
		elif (event.key == pygame.K_RETURN):
			## Buffer is complete, process it
			self.logger.info("Got raw input '%s'" % self.scannedinput)
			self.__onScanEvent__(self.scannedinput)
			
			self.scannedinput = ''
				
		elif (event.key == pygame.K_a) and (pygame.key.get_mods() & pygame.KMOD_CTRL):
			## Go to product entry screen
			self.__RequestScreen__(Screens.MAINSCREEN, Requests.PRODUCTS, False)
			
		elif (event.key == pygame.K_u) and (pygame.key.get_mods() & pygame.KMOD_CTRL):
			## Fake an RFID swipe
			if self.rfid is None:
				self.fakeRFID = [0x1B, 0x7F, 0x2D, 0x2D]
			
			
					
	def __onSwipeEvent__(self, cardnumber):
		userdata = self.dbaccess.GetUserData(cardnumber)
		
		if userdata is not None:
			self.user = User(*userdata)
			self.logger.info("Got user %s" % self.user.Name)
		else:
			self.logger.info("Bad RFID %s" % cardnumber)
						
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
			
	def __onScanEvent__(self, barcode):
		
		newitem = self.__AddItem__(barcode)
		
		if newitem is not None:
			for screen in self.screens.values():
				try:
					screen.OnScan(newitem)
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
					
	def __setScreen__(self, newscreen, force):	
		if (newscreen.value != self.currentscreen.value or force):
			self.logger.info("Changing screen from %s to %s" % (self.currentscreen.str, newscreen.str))
			self.currentscreen = newscreen
			self.screens[newscreen.value].draw(self.window)
				
	def __setConstants__(self):
		self.validKeys = [
			pygame.K_0, pygame.K_1, 	pygame.K_2, pygame.K_3, pygame.K_4,
			pygame.K_5, pygame.K_6, 	pygame.K_7, pygame.K_8, pygame.K_9
		]
	
	def __setVariables__(self):
		self.scannedinput = ''
		
		self.dbaccess = DbRemote(self.localdb)
		
		self.logger = logging.getLogger("snackspace")
		
		if self.rfid_port != 'fake':
			self.rfid = RFIDReader(self.rfid_port);
		else:
			self.rfid = None
			self.fakeRFID = []

		self.user = None
		self.items = []
		
	def __RequestScreen__(self, currentscreenid, request, force):
		if request == Requests.MAIN:
			self.__setScreen__(Screens.MAINSCREEN, force)
		elif request == Requests.PAYMENT:
			self.__setScreen__(Screens.NUMERICENTRY, force)
		elif request == Requests.INTRO:
			self.__setScreen__(Screens.INTROSCREEN, force)
		elif request == Requests.PRODUCTS:
			self.__setScreen__(Screens.PRODUCTENTRY, force)
				
	def __ChargeAll__(self):
		if self.user is not None:
			items = [(item.Barcode, item.Count) for item in self.items]
			return self.dbaccess.SendTransactions(items, self.user.MemberID)
		else:
			return False
		
	def __CreditUser__(self, amount):
		self.dbaccess.AddCredit(self.user.MemberID, amount)
	
	def __ForgetUser__(self):
		self.user = None
					
	def __RequestUser__(self):
		return None
	
	def __RequestAllItems__(self):
		return None
		
	def __AddItem__(self, barcode):
		
		item = next((item for item in self.items if barcode == item.Barcode), None)
		
		if item is not None:
			item.Increment()
		else:
			itemdata = self.dbaccess.GetItem(barcode) 
			
			if itemdata:
				item = Item(*itemdata)
				
				if item is not None and item.Valid:
					self.items.append(item)
				else:
					item = None
			
		return item
		
	def __TotalPrice__(self):
		return sum([item.TotalPrice for item in self.items])
		
	def __RemoveItem__(self, itemToRemove):
		
		if itemToRemove.Decrement() == 0:
			self.items = [item for item in self.items if item != itemToRemove]
				
		return itemToRemove.Count
		
	def __RemoveAllItems__(self):
		self.items = []

	def __NewItems__(self, itemlist):
		pass
	
def main(argv=None):

	parser = argparse.ArgumentParser(description='Snackspace Server')
	parser.add_argument('-L', dest='localmode', nargs='?', default='n', const='y')
	parser.add_argument('-P', dest='rfid_port', nargs='?', default='/dev/ttyUSB0')
	
	args = parser.parse_args()
	
	pygame.init()
	
	size = [800, 600]
	
	window = pygame.display.set_mode(size)
	
	s = Snackspace(window, size, args.localmode == 'y', args.rfid_port)
	
	logging.basicConfig(level=logging.DEBUG)

	s.StartEventLoop()

if __name__ == "__main__":
	main()
