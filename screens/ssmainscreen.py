
from ssconstants import SSRequests, SSScreens, SSData

from ssitem import SSItem

from xml.dom.minidom import parse

from ssmainscreen_gui import SSMainScreenGUI

from mydebug import debugPrint

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
			
			#Find entries for this state
			entries = [entry for entry in self.entries if entry.state == self.state]
			
			if len(entries) == 0:
				raise self.StateNotFoundException("State %s not found" % self.state)
			
			#Find the handler for this event
			try:
				[handler] = [entry.handler for entry in entries if entry.event == event]
			except ValueError:
				raise self.EventNotFoundException("Event %s in state %s" % (event, self.state))
	
			self.state = handler()
				
			if self.state is None:
				raise self.BadHandlerException("Handler did not return next state")
			
			debugPrint("Got event %s in state %s, new state %s" % (event, oldState, self.state))
			
		self.executing = False
			
class SimpleStateMachineEntry:
	def __init__(self, state, event, handler):
		self.state = state
		self.event = event
		self.handler = handler
		
class ItemQueryFunctions:
	
	def __init__(self, DescriptionQuery, PriceQuery, QuantityQuery, TotalPriceQuery):
		self.Description = DescriptionQuery
		self.Price = PriceQuery
		self.Quantity = QuantityQuery
		self.TotalPrice = TotalPriceQuery
		
class SSMainScreen:

	def __init__(self, width, height, user, callback):
		
		self.gui = SSMainScreenGUI(width, height, self)
		
		self.user = user
		self.SSCallback = callback
		
		self.setConstants()
		self.setVariables()
		
		self.itemData = parse(SSData.ItemsFile.value)
		
		self.ItemQuery = ItemQueryFunctions(
			self.descFromBarcode,
			self.priceFromBarcode,
			self.qtyFromBarcode,
			self.totalPriceFromBarcode,
			)
		
	def descFromBarcode(self, barcode):
		
		[desc] = [item.description for item in self.items if item.barcode == barcode]
		return desc
	
	def priceFromBarcode(self, barcode):
		
		price = 0
		for item in self.items:
			if item.barcode == barcode:
				price = item.priceinpence
				break
		return price
	
	def qtyFromBarcode(self, barcode):
		
		qty = 0
		for item in self.items:
			if item.barcode == barcode:
				qty = item.count
				break
		return qty
	
	def totalPriceFromBarcode(self, barcode):
		qty = 0
		priceinpence = 0
		for item in self.items:
			if item.barcode == barcode:
				qty = item.count
				priceinpence = item.priceinpence
				break
		return qty * priceinpence
	
	def totalPrice(self):
		return sum([item.count * item.priceinpence for item in self.items])
	
	def requestRedraw(self):
		self.SSCallback(SSScreens.MAINSCREEN, SSRequests.MAIN, True)
		return self.states.IDLE
	
	def draw(self, window):
		debugPrint("Drawing self")
		self.gui.draw(window)
		self.SM.onStateEvent(self.events.REFRESHED)
	
	def clearAll(self):
		self.items = []
		self.gui.clearItems()
		self.user.forget()
			
	def onGuiEvent(self, pos):
	
		self.lastGuiPosition = pos
		self.SM.onStateEvent(self.events.GUIEVENT)

	def onScanEvent(self, barcode):
		
		self.lastScan = barcode
		self.SM.onStateEvent(self.events.SCAN)
	
	def onSwipeEvent(self, cardId):
		self.lastCardId = cardId
		self.SM.onStateEvent(self.events.SWIPE)
		
	def onUserEvent(self, user):
	
		if (user.isValid()):
			self.gui.setUser(user.getName(), user.getBalance())		
		else:
			self.gui.setUnknownUser()
		
		self.SM.onStateEvent(self.events.USERUPDATED)	
		
	def getItemFromBarcode(self, barcode):
		
		try:
			[item] = [item for item in self.items if item.barcode == barcode]
		except ValueError:
			item = None
			
		return item
		
	def isUserLogged(self):
		return self.user.isValid()
	
	def setVariables(self):
		self.items = []
		
		self.SM = SimpleStateMachine(self.states.READY,
		[
			SimpleStateMachineEntry(self.states.READY, self.events.USERUPDATED,		self.requestRedraw),
			SimpleStateMachineEntry(self.states.READY, self.events.SCAN,			self.onIdleScanEvent),
			SimpleStateMachineEntry(self.states.READY, self.events.REFRESHED,		lambda: self.states.IDLE),
			
			SimpleStateMachineEntry(self.states.IDLE, self.events.GUIEVENT,			self.onIdleGuiEvent),
			SimpleStateMachineEntry(self.states.IDLE, self.events.SCAN,				self.onIdleScanEvent),
			SimpleStateMachineEntry(self.states.IDLE, self.events.ITEMUPDATED,		self.requestRedraw),
			SimpleStateMachineEntry(self.states.IDLE, self.events.USERUPDATED,		self.requestRedraw),
			SimpleStateMachineEntry(self.states.IDLE, self.events.REFRESHED,		lambda: self.states.IDLE),
			
			SimpleStateMachineEntry(self.states.NUMERIC, self.events.USERUPDATED,	self.requestRedraw),
			SimpleStateMachineEntry(self.states.NUMERIC, self.events.REFRESHED,		lambda: self.states.IDLE),
			
			SimpleStateMachineEntry(self.states.PAYING, self.events.USERUPDATED,	self.returnToIntro),
		]
		)
		
	def setConstants(self):
		self.states = Enum(["READY", "IDLE", "NUMERIC", "PAYING"])
		self.events = Enum(["GUIEVENT","SCAN", "USERUPDATED", "ITEMUPDATED", "REFRESHED"])

	def onIdleGuiEvent(self):
		
		pos = self.lastGuiPosition
		button = self.gui.getObjectId( pos )
		nextState = self.SM.state
		
		if (button == self.gui.DONE):
			nextState = self.states.PAYING
			self.user.charge(self.totalPrice())
			
		if (button == self.gui.CANCEL):
			nextState = self.returnToIntro()
			
		if (button == self.gui.PAY):
			nextState = self.states.NUMERIC
			self.SSCallback(SSScreens.MAINSCREEN, SSRequests.PAYMENT, False)
		
		if (button == self.gui.DOWN):
			self.gui.moveDown()
			self.requestRedraw()
			
		if (button == self.gui.UP):
			self.gui.moveUp()
			self.requestRedraw()
			
		if (button == self.gui.REMOVE):
			barcode = self.gui.getItemBarcodeAtPosition(pos)
						
			item = self.getItemFromBarcode(barcode)
			
			if item.count == 1:
				debugPrint("Removing item %s" % item.barcode)
				self.items.remove(item)
				self.gui.removeItemAtPosition(pos)
				
			else:
				debugPrint("Decrementing item %s" % item.barcode)
				item.count -= 1
				
			self.requestRedraw()
			
		return nextState
	
	def onIdleScanEvent(self):
		
		debugPrint("Got barcode %s" % self.lastScan)
		try:
			[item] = [item for item in self.items if self.lastScan == item.barcode ]
		except ValueError:
			item = None #Barcode does not exist
			
		## If there is already an item with this barcode, increment count
		if item is not None:
			item.increment()
		else:				
			#New item
			newItem = SSItem(self.itemData, self.lastScan)
			
			if newItem.isValid():
				self.items.append(newItem)
				self.gui.addItem(newItem.barcode)
		
		self.lastScan = 0
		self.requestRedraw()	
		
		return self.states.IDLE
	
	def returnToIntro(self):
		self.clearAll()
		self.SSCallback(SSScreens.MAINSCREEN, SSRequests.INTRO, False)
		return self.states.READY
			