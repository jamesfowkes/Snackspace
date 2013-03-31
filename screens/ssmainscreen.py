import logging

from ssconstants import SSRequests, SSScreens

# # Safe wild import: all constants, all start with SS_
from ssdisplayconstants import *  # @UnusedWildImport

from ssmainscreen_gui import SSMainScreenGUI

from enum import Enum

class SimpleStateMachine:
	
	class StateNotFoundException(Exception):
		pass
	
	class EventNotFoundException(Exception):
		pass
	
	class BadHandlerException(Exception):
		pass
	
	def __init__(self, startstate, entries):
		self.state = startstate
		self.entries = entries
		self.eventQueue = []
		self.executing = False
		self.logger = logging.getLogger("SimpleStateMachine")
		
	def onStateEvent(self, event):
		
		self.eventQueue.append(event)
		
		if not self.executing:
			self.handleEventQueue()
		
	def handleEventQueue(self):
		
		self.executing = True
		while len(self.eventQueue) > 0:
			
			event = self.eventQueue[0]
			self.eventQueue = self.eventQueue[1:]
			
			oldState = self.state
			
			# Find entries for this state
			entries = [entry for entry in self.entries if entry.state == self.state]
			
			if len(entries) == 0:
				raise self.StateNotFoundException("State %s not found" % self.state)
			
			# Find the handler for this event
			try:
				[handler] = [entry.handler for entry in entries if entry.event == event]
			except ValueError:
				raise self.EventNotFoundException("Event %s in state %s" % (event, self.state))
	
			self.state = handler()
				
			if self.state is None:
				raise self.BadHandlerException("Handler did not return next state")
			
			self.logger.info("Got event %s in state %s, new state %s" % (event, oldState, self.state))
			
		self.executing = False

class SimpleStateMachineEntry:
	def __init__(self, state, event, handler):
		self.state = state
		self.event = event
		self.handler = handler
			
class SSMainScreen:

	def __init__(self, width, height, screenFuncs, userFuncs, itemFuncs):
		
		self.gui = SSMainScreenGUI(width, height, self)
		
		self.__setConstants__()
		self.__setVariables__()
		
		self.ItemFuncs = itemFuncs
		self.ScreenFuncs = screenFuncs
		self.UserFuncs = userFuncs
		
	###
	### Public Functions
	###
		
	def draw(self, window):
		self.logger.info("Drawing self")
		self.gui.draw(window)
	
	def clearAll(self):
		self.logger.info("Clearing items")
		
		self.acceptInput = True
		
		self.gui.clearItems()
		self.gui.setUnknownUser()
		
		self.UserFuncs.Forget()
		self.ItemFuncs.RemoveAll()
			
	def OnGuiEvent(self, pos):
		
		if self.acceptInput:
			self.lastGuiPosition = pos
			self.SM.onStateEvent(self.events.GUIEVENT)

	def OnScan(self, item):
		if self.acceptInput:
			self.newItem = item
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
		return self.__totalPrice__()
	
	def UserLogged(self):
		return self.__isUserLogged__()
	
	def UserInDebt(self):
		return self.__isUserInDebt__()
	
	###
	### Private Functions
	###
	
	def __totalPrice__(self):
		return self.ItemFuncs.TotalPrice()
	
	def __requestRedraw__(self):
		self.ScreenFuncs.RequestScreen(SSScreens.MAINSCREEN, SSRequests.MAIN, True)
		return self.states.IDLE
	
	def __isUserLogged__(self):
		return self.__user__()
	
	def __isUserInDebt__(self):
		try:
			return self.__user__().getBalance() < 0
		except AttributeError:
			return True
	
	def __isUserInCredit__(self):
		try:
			return self.__user__().getBalance() >= 0
		except AttributeError:
			return False
	
	def __setVariables__(self):
		
		self.SM = SimpleStateMachine(self.states.INACTIVE,
		[
			SimpleStateMachineEntry(self.states.INACTIVE, self.events.SCAN, 		self.__onIdleScanEvent__),
			SimpleStateMachineEntry(self.states.INACTIVE, self.events.BADSCAN, 		self.__onIdleBadScanEvent__),
			SimpleStateMachineEntry(self.states.INACTIVE, self.events.RFID, 		self.__onRFIDEvent__),
			SimpleStateMachineEntry(self.states.INACTIVE, self.events.BADRFID, 		self.__onBadRFIDEvent__),
			SimpleStateMachineEntry(self.states.INACTIVE, self.events.GUIEVENT, 	self.__onIdleGuiEvent__),
			
			SimpleStateMachineEntry(self.states.IDLE, self.events.GUIEVENT, 		self.__onIdleGuiEvent__),
			SimpleStateMachineEntry(self.states.IDLE, self.events.SCAN, 			self.__onIdleScanEvent__),
			SimpleStateMachineEntry(self.states.IDLE, self.events.BADSCAN, 			self.__onIdleBadScanEvent__),
			SimpleStateMachineEntry(self.states.IDLE, self.events.RFID, 			self.__onRFIDEvent__),
			SimpleStateMachineEntry(self.states.IDLE, self.events.BADRFID, 			self.__onBadRFIDEvent__),
			SimpleStateMachineEntry(self.states.IDLE, self.events.ITEMUPDATED, 		self.__requestRedraw__),
									
			SimpleStateMachineEntry(self.states.PAYMENTMESSAGE,	 self.events.BANNERTIMEOUT,	self.__returnToIntro__),
								
			SimpleStateMachineEntry(self.states.WARNING, self.events.BANNERTIMEOUT, self.__removeWarning__),
			SimpleStateMachineEntry(self.states.WARNING, self.events.SCAN, 			self.__onIdleScanEvent__),
			SimpleStateMachineEntry(self.states.WARNING, self.events.BADSCAN, 		self.__updateBarcodeWarning__),
			SimpleStateMachineEntry(self.states.WARNING, self.events.RFID, 			self.__onRFIDEvent__),
			SimpleStateMachineEntry(self.states.WARNING, self.events.BADRFID, 		self.__onBadRFIDEvent__),
			SimpleStateMachineEntry(self.states.WARNING, self.events.GUIEVENT, 		self.__removeWarning__),

		])
									
		self.logger = logging.getLogger("MainScreen")
		
		self.acceptInput = True
		
	def __setConstants__(self):
		self.states = Enum(["INACTIVE", "IDLE", "NUMERIC", "PAYMENTMESSAGE", "WARNING"])
		self.events = Enum(["GUIEVENT", "SCAN", "BADSCAN", "RFID", "BADRFID", "ITEMUPDATED", "BANNERTIMEOUT"])

	def __onIdleGuiEvent__(self):
		
		pos = self.lastGuiPosition
		button = self.gui.getObjectId(pos)
		
		# Default to staying in same state
		nextState = self.SM.state
		
		if button > -1:
			self.gui.playSound()
			
		if (button == self.gui.DONE):
			nextState = self.__chargeUser__()	
			
		if (button == self.gui.CANCEL):
			nextState = self.__returnToIntro__()
			
		if (button == self.gui.PAY):
			nextState = self.states.NUMERIC
			self.ScreenFuncs.RequestScreen(SSScreens.MAINSCREEN, SSRequests.PAYMENT, False)
		
		if (button == self.gui.DOWN):
			self.gui.moveDown()
			self.__requestRedraw__()
			
		if (button == self.gui.UP):
			self.gui.moveUp()
			self.__requestRedraw__()
			
		if (button == self.gui.REMOVE):
					
			ssitem = self.gui.getItemAtPosition(pos)
			self.logger.info("Removing item %s" % ssitem.Barcode)
						
			if self.ItemFuncs.RemoveItem(ssitem) == 0:
				# No items of this type left in list
				self.gui.removeItem(ssitem)

			self.__requestRedraw__()
			
		return nextState
	
	def __onIdleScanEvent__(self):
		
		self.logger.info("Got barcode %s" % self.newItem.Barcode)
		
		# Ensure that the warning banner goes away
		self.gui.HideBanner()

		self.gui.addDisplayItem(self.newItem)
		self.__requestRedraw__()
			
		self.newItem = None
			
		return self.states.IDLE
	
	def __onIdleBadScanEvent__(self):
		
		self.logger.info("Got unrecognised barcode %s" % self.badcode)
		self.gui.SetBannerWithTimeout("Unknown barcode: '%s'" % self.badcode, 4, SS_WARNING_FG, self.__bannerTimeout__)
		self.__requestRedraw__()
		self.badcode = ""
		
		return self.states.WARNING
	
	def __onRFIDEvent__(self):
	
		self.logger.info("Got user %s" % self.__user__().Name)
		self.gui.HideBanner()
		self.gui.setUser(self.__user__().Name, self.__user__().Balance)		
		self.__requestRedraw__()
		
		return self.SM.state

	def __onBadRFIDEvent__(self):
	
		self.gui.SetBannerWithTimeout("Unknown RFID card!", 4, SS_WARNING_FG, self.__bannerTimeout__)
		
		self.__requestRedraw__()
		
		return self.states.WARNING
	
	def __bannerTimeout__(self):
		self.SM.onStateEvent(self.events.BANNERTIMEOUT)
	
	def __updateBarcodeWarning__(self):
		self.logger.info("Got unrecognised barcode %s" % self.badcode)
		self.gui.SetBannerWithTimeout("Unknown barcode: '%s'" % self.badcode, 4, SS_WARNING_FG, self.__bannerTimeout__)
		self.__requestRedraw__()
		return self.states.WARNING
	
	def __removeWarning__(self):
		self.gui.HideBanner()
		self.__requestRedraw__()
		return self.states.IDLE
		
	def __returnToIntro__(self):
		self.clearAll()
		self.ScreenFuncs.RequestScreen(SSScreens.MAINSCREEN, SSRequests.INTRO, False)
		return self.states.INACTIVE
	
	def __chargeUser__(self):
		self.acceptInput = False
		
		nextState = self.states.PAYMENTMESSAGE
		
		amountinpounds = self.__totalPrice__()
		if self.UserFuncs.ChargeAll() == True:
			self.gui.SetBannerWithTimeout("Thank you! You have been charged \xA3%.2f" % amountinpounds, 10, SS_INFO_FG, self.__bannerTimeout__)
		else:
			self.gui.SetBannerWithTimeout("An error occurred and has been logged.", 10, SS_WARNING_FG, self.__bannerTimeout__)
			self.logger.error("Failed to charge user %s %d pence")

		self.__requestRedraw__()
		
		return nextState
	def __user__(self):
		return self.UserFuncs.Get()
