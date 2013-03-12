import sys
import pygame

import argparse

import logging

import time

from bunch import Bunch

from ssconstants import SSRequests, SSScreens

from ssitem import SSItem
from ssuser import SSUser

from ssdbremote import SSDbRemote

from screens.ssintroscreen import SSIntroScreen
from screens.ssnumericentry import SSNumericEntry
from screens.ssmainscreen import SSMainScreen

class Snackspace:
	def __init__(self, window, size, localdb):
		
		self.inittime = int(time.time())
		
		self.window = window
		self.width = size[0]
		self.height = size[1]
		
		self.localdb = localdb
		
		self.__setConstants__()
		
		self.__setVariables__()
		
		self.ScreenFunctions = Bunch(
			RequestScreen = self.__RequestScreen__)		
	
		self.UserFunctions = Bunch(
			Get = lambda: self.user,
			ChargeAll = self.__ChargeAll__,
			Forget = self.__ForgetUser__
			)
		
		self.ItemFunctions = Bunch(
			RequestAllItems = self.__RequestAllItems__,
			TotalPrice = self.__TotalPrice__,
			RemoveItem = self.__RemoveItem__,
			RemoveAll = self.__RemoveAllItems__)
		
		# Instantiate all the screens now
		self.screens = {
			SSScreens.INTROSCREEN.value	: SSIntroScreen(self.width, self.height, self.ScreenFunctions, self.UserFunctions, self.ItemFunctions),
			SSScreens.NUMERICENTRY.value	: SSNumericEntry(self.width, self.height, self.ScreenFunctions, self.UserFunctions),
			SSScreens.MAINSCREEN.value	: SSMainScreen(self.width, self.height, self.ScreenFunctions, self.UserFunctions, self.ItemFunctions)
			}
		
		self.screens[SSScreens.INTROSCREEN.value].acceptGUIEvents = False
		self.screens[SSScreens.NUMERICENTRY.value].acceptGUIEvents = True
		self.screens[SSScreens.MAINSCREEN.value].acceptGUIEvents = True
		
		self.currentscreen = SSScreens.BLANKSCREEN
		self.__setScreen__(SSScreens.INTROSCREEN, False)
		
		if not self.dbaccess.isConnected:
			self.logger.warning("Could not find remote database")
			self.screens[SSScreens.INTROSCREEN.value].setIntroText(
				"ERROR: Cannot access Snackspace remote database",
				(0xFF, 0, 0))
			self.__setScreen__(SSScreens.INTROSCREEN, True)
		else:
			self.logger.info("Found remote database")
			self.screens[SSScreens.INTROSCREEN.value].acceptGUIEvents = True
		
	def StartEventLoop(self):
		while (1):
			for event in pygame.event.get():
				if event.type == pygame.QUIT: sys.exit()
				if event.type == pygame.MOUSEBUTTONUP:
					self.logger.info("GUI Event")
					try:
						self.screens[self.currentscreen.value].OnGuiEvent(event.pos)
					except AttributeError:  # Screen does not handle Gui events
						if "OnGuiEvent" in dir(self.screens[self.currentscreen.value]):
							raise  # # Only raise error if the onScanEvent method exists
				if event.type == pygame.KEYDOWN:
					self.__inputHandler__(event)

	def __inputHandler__(self, event):
		if (event.key in self.validKeys):
			self.scannedinput += event.dict['unicode']
		elif (event.key == pygame.K_RETURN):
			
			self.logger.info("Got raw input '%s'" % self.scannedinput)
			if (self.scannedinput == "4574"):
				self.__onSwipeEvent__(4574)
			elif (self.scannedinput == "123"):
				self.__onSwipeEvent__(123)
			else:
				self.__onScanEvent__(self.scannedinput)
			
			self.scannedinput = ''
					
	def __onSwipeEvent__(self, cardnumber):
		userdata = self.dbaccess.GetUserData(cardnumber)
		
		if userdata is not None:
			self.user = SSUser(*userdata)
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
			pygame.K_0, pygame.K_1,	pygame.K_2, pygame.K_3, pygame.K_4,
			pygame.K_5, pygame.K_6,	pygame.K_7, pygame.K_8, pygame.K_9
		]
	
	def __setVariables__(self):
		self.scannedinput = ''
		
		self.dbaccess = SSDbRemote(self.localdb)
		
		self.logger = logging.getLogger("snackspace")
		
		self.user = None
		self.items = []
		
	def __RequestScreen__(self, currentscreenid, request, force):
		if request == SSRequests.MAIN:
			self.__setScreen__(SSScreens.MAINSCREEN, force)
		elif request == SSRequests.PAYMENT:
			self.__setScreen__(SSScreens.NUMERICENTRY, force)
		elif request == SSRequests.INTRO:
			self.__setScreen__(SSScreens.INTROSCREEN, force)
	
	def __ChargeAll__(self):
		if self.user is not None:
			items = [(item.Barcode, item.Count) for item in self.items]
			return self.dbaccess.SendTransactions(items, self.user.RFID)
		else:
			return False
		
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
			itemdata  = self.dbaccess.GetItem(barcode) 
			
			if itemdata:
				item = SSItem(*itemdata)
				
				if item is not None and item.Valid:
					self.items.append( item )
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

def main(argv=None):

	parser = argparse.ArgumentParser(description='Snackspace Server')
	parser.add_argument('-L', dest='localmode', nargs='?',default='n', const='y')
	
	args = parser.parse_args()
	
	pygame.init()
	
	size = [800, 600]
	
	window = pygame.display.set_mode(size)
	
	if args.localmode == 'y':
		s = Snackspace(window, size, True)
	else:
		s = Snackspace(window, size, False)

	logging.basicConfig(level=logging.DEBUG)

	s.StartEventLoop()

if __name__ == "__main__":
	main()
