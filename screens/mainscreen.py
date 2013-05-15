from __future__ import division

import logging

from constants import Screens

# # Safe wild import: all constants
from displayconstants import *  # @UnusedWildImport

from mainscreen_gui import MainScreenGUI

from SimpleStateMachine import SimpleStateMachine, SimpleStateMachineEntry

from enum import Enum
			
class MainScreen:

	def __init__(self, width, height, screenFuncs, userFuncs, productFuncs):
		
		self.gui = MainScreenGUI(width, height, self)
		
		self.__setConstants()
		self.__setVariables()
		
		self.ProductFuncs = productFuncs
		self.ScreenFuncs = screenFuncs
		self.UserFuncs = userFuncs
		
	###
	### Public Functions
	###
	
	def setActive(self, state):
		pass
				
	def draw(self, window):
		self.logger.info("Drawing self")
		self.gui.draw(window)
	
	def clearAll(self):
		self.logger.info("Clearing products")
			
		self.gui.clearProducts()
		self.gui.setUnknownUser()
		
		self.UserFuncs.Forget()
		self.ProductFuncs.RemoveAll()
			
	def OnGuiEvent(self, pos):
		
		if self.acceptInput:
			self.lastGuiPosition = pos
			self.SM.onStateEvent(self.events.GUIEVENT)

	def OnScan(self, product, __barcode):
		self.newProduct = product
		if self.acceptInput:
			self.SM.onStateEvent(self.events.SCAN)
			
	def OnBadScan(self, badcode):
		if self.acceptInput:
			self.badcode = badcode
			self.SM.onStateEvent(self.events.BADSCAN)
		
	def OnRFID(self):
		if self.acceptInput:
			self.SM.onStateEvent(self.events.RFID)
	
	def OnBadRFID(self):
		if self.acceptInput:
			self.SM.onStateEvent(self.events.BADRFID)
	
	def TotalPrice(self):
		return self.__totalPrice()
	
	def UserLogged(self):
		return self.__isUserLogged()
	
	def UserAllowCredit(self):
		return self.__userAllowCredit()
	
	###
	### Private Functions
	###
	
	def __totalPrice(self):
		return self.ProductFuncs.TotalPrice()
	
	def __requestRedraw(self):
		self.ScreenFuncs.RequestScreen(Screens.MAINSCREEN)
		return self.states.IDLE
	
	def __isUserLogged(self):
		return self.__user
	
	def __isUserInDebt(self):
		try:
			return self.__user.getBalance() < 0
		except AttributeError:
			return True
	
	def __userAllowCredit(self):
		try:
			return self.__user.creditAllowed()
		except AttributeError:
			return False
	
	def __setVariables(self):
		
		self.SM = SimpleStateMachine(self.states.IDLE,
		[		
			SimpleStateMachineEntry(self.states.IDLE, self.events.GUIEVENT, 		self.__onIdleGuiEvent),
			SimpleStateMachineEntry(self.states.IDLE, self.events.SCAN, 			self.__onIdleScanEvent),
			SimpleStateMachineEntry(self.states.IDLE, self.events.BADSCAN, 			self.__onIdleBadScanEvent),
			SimpleStateMachineEntry(self.states.IDLE, self.events.RFID, 			self.__onRFIDEvent),
			SimpleStateMachineEntry(self.states.IDLE, self.events.BADRFID, 			self.__onBadRFIDEvent),
			SimpleStateMachineEntry(self.states.IDLE, self.events.PRODUCTUPDATED, 	self.__requestRedraw),
									
			SimpleStateMachineEntry(self.states.PAYMENTMESSAGE,	 self.events.BANNERTIMEOUT,	self.__returnToIntro),
								
			SimpleStateMachineEntry(self.states.WARNING, self.events.BANNERTIMEOUT, self.__removeWarning),
			SimpleStateMachineEntry(self.states.WARNING, self.events.SCAN, 			self.__onIdleScanEvent),
			SimpleStateMachineEntry(self.states.WARNING, self.events.BADSCAN, 		self.__updateBarcodeWarning),
			SimpleStateMachineEntry(self.states.WARNING, self.events.RFID, 			self.__onRFIDEvent),
			SimpleStateMachineEntry(self.states.WARNING, self.events.BADRFID, 		self.__onBadRFIDEvent),
			SimpleStateMachineEntry(self.states.WARNING, self.events.GUIEVENT, 		self.__removeWarning),

		])
									
		self.logger = logging.getLogger("MainScreen")
		
		self.acceptInput = True
		
	def __setConstants(self):
		self.states = Enum(["IDLE", "PAYMENTMESSAGE", "WARNING"])
		self.events = Enum(["GUIEVENT", "SCAN", "BADSCAN", "RFID", "BADRFID", "PRODUCTUPDATED", "BANNERTIMEOUT"])

	def __onIdleGuiEvent(self):
		
		pos = self.lastGuiPosition
		button = self.gui.getObjectId(pos)
		
		# Default to staying in same state
		nextState = self.SM.state
		
		if button > -1:
			self.gui.playSound()
			
		if (button == self.gui.DONE):
			nextState = self.__chargeUser()	
			
		if (button == self.gui.CANCEL):
			nextState = self.__returnToIntro()
			
		if (button == self.gui.PAY):
			self.ScreenFuncs.RequestScreen(Screens.NUMERICENTRY)
		
		if (button == self.gui.DOWN):
			self.gui.moveDown()
			self.__requestRedraw()
			
		if (button == self.gui.UP):
			self.gui.moveUp()
			self.__requestRedraw()
			
		if (button == self.gui.REMOVE):
					
			product = self.gui.getProductAtPosition(pos)
			self.logger.info("Removing product %s" % product.Barcode)
						
			if self.ProductFuncs.RemoveProduct(product) == 0:
				# No products of this type left in list
				self.gui.removeProduct(product)

			self.__requestRedraw()
			
		return nextState
	
	def __onIdleScanEvent(self):
		
		self.logger.info("Got barcode %s" % self.newProduct.Barcode)
		
		# Ensure that the warning banner goes away
		self.gui.HideBanner()
		
		nextState = self.states.IDLE
		
		if self.__user is not None:
			transAllowedState = self.__user.TransactionAllowed(self.newProduct.PriceEach)
			
			if transAllowedState == self.__user.XACTION_ALLOWED:
				## Add product, nothing else to do
				self.gui.addToProductDisplay(self.newProduct)
			elif transAllowedState == self.__user.XACTION_OVERLIMIT:
				## Add product, but also warn about being over credit limit
				self.gui.addToProductDisplay(self.newProduct)
				self.gui.SetBannerWithTimeout("Warning: you have reached your credit limit!", 4, RGB_WARNING_FG, self.__bannerTimeout)
				nextState = self.states.WARNING
			elif transAllowedState == self.__user.XACTION_DENIED:
				## Do not add the product to screen. Request removal from product list and warn user
				self.gui.SetBannerWithTimeout("Sorry, you have reached your credit limit!", 4, RGB_ERROR_FG, self.__bannerTimeout)
				self.ProductFuncs.RemoveProduct(self.newProduct)
				nextState = self.states.WARNING
		else:
			#Assume that the user is allowed to buy this
			self.gui.addToProductDisplay(self.newProduct)

		self.__requestRedraw()
		self.newProduct = None
		
		return nextState
	
	def __onIdleBadScanEvent(self):
		
		self.logger.info("Got unrecognised barcode %s" % self.badcode)
		self.gui.SetBannerWithTimeout("Unknown barcode: '%s'" % self.badcode, 4, RGB_ERROR_FG, self.__bannerTimeout)
		self.__requestRedraw()
		self.badcode = ""
		
		return self.states.WARNING
	
	def __onRFIDEvent(self):
	
		self.logger.info("Got user %s" % self.__user.Name)
		self.gui.HideBanner()
		self.gui.setUser(self.__user.Name, self.__user.Balance)		
		self.__requestRedraw()
		
		return self.SM.state

	def __onBadRFIDEvent(self):
	
		self.gui.SetBannerWithTimeout("Unknown RFID card!", 4, RGB_ERROR_FG, self.__bannerTimeout)
		
		self.__requestRedraw()
		
		return self.states.WARNING
	
	def __bannerTimeout(self):
		self.SM.onStateEvent(self.events.BANNERTIMEOUT)
	
	def __updateBarcodeWarning(self):
		self.logger.info("Got unrecognised barcode %s" % self.badcode)
		self.gui.SetBannerWithTimeout("Unknown barcode: '%s'" % self.badcode, 4, RGB_ERROR_FG, self.__bannerTimeout)
		self.__requestRedraw()
		return self.states.WARNING
	
	def __removeWarning(self):
		self.gui.HideBanner()
		self.__requestRedraw()
		return self.states.IDLE
		
	def __returnToIntro(self):
		self.clearAll()
		self.ScreenFuncs.RequestScreen(Screens.INTROSCREEN)
		return self.states.IDLE
	
	def __chargeUser(self):
		self.acceptInput = False
		
		nextState = self.states.PAYMENTMESSAGE
		
		amountinpounds = self.__totalPrice() / 100
		
		if self.UserFuncs.ChargeAll() == True:
			self.gui.SetBannerWithTimeout("Thank you! You have been charged \xA3%.2f" % amountinpounds, 8, RGB_INFO_FG, self.__bannerTimeout)
		else:
			self.gui.SetBannerWithTimeout("An error occurred and has been logged.", 10, RGB_ERROR_FG, self.__bannerTimeout)
			self.logger.error("Failed to charge user %s %d pence")

		self.__requestRedraw()
		
		return nextState
	
	@property
	def __user(self):
		return self.UserFuncs.Get()
