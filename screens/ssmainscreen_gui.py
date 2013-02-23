from __future__ import division

import pygame
import logging

# # Safe wild import: all constants, all start with SS_
from ssdisplayconstants import *  # @UnusedWildImport

from lcarscappedbar import LCARSCappedBar, CapLocation

from ssborder import SSBorder
from ssscreen_gui import SSScreenGUI

class MainScreenLayout:
	def __init__(self, width, height, border):
		
		self.itemrowh = 100
		self.buttonw = 100
		self.largebuttonw = (self.buttonw * 2)
		self.buttonh = 50
		
		# # Spread buttons out between sweep and edge
		self.donebuttonx	 = border.innerX() + SS_BORDER
		self.cancelbuttonx	 = width - SS_BORDER - self.largebuttonw
		self.paybuttonx		 = (self.donebuttonx + self.cancelbuttonx) / 2
		
		self.buttonsy = height - SS_BORDER - self.buttonh  # Put buttons at bottom of screen
		
		self.topbarx = border.innerX() + SS_BORDER
		self.topbary = border.innerY() + SS_BORDER
		
		self.innerWidth = width - self.topbarx - SS_BORDER
		
		self.amounty = self.topbary
		self.amountw = 2 * self.buttonw
		self.amountx = width - SS_BORDER - self.amountw 
		
		self.topbarwidth = self.innerWidth - self.amountw - SS_BORDER
		
		self.itemtopy = self.topbary + self.buttonh + SS_BORDER
		self.itemx = self.topbarx
		
		self.scrollbuttonh = (self.buttonsy - self.itemtopy) / 2
		self.scrollbuttonh -= SS_BORDER
		
		self.scrollbuttonw = self.buttonh 
		self.scrollx = width - SS_BORDER - self.scrollbuttonw 
		self.upy = self.itemtopy
		self.downy = self.upy + self.scrollbuttonh + SS_BORDER
	
		self.setItemConstants()
		
	def setItemConstants(self):
		# Position constants for item objects
		self.descx = self.itemx
		self.descw = self.largebuttonw * 1.8
		self.pricex = self.descx + self.descw + SS_BORDER
		self.pricew = self.largebuttonw / 2
		self.removex = self.pricex + self.pricew + SS_BORDER
	
	def getDoneRect(self):
		return pygame.Rect(self.donebuttonx, self.buttonsy, self.largebuttonw, self.buttonh)
	
	def getPayRect(self):
		return pygame.Rect(self.paybuttonx, self.buttonsy, self.largebuttonw, self.buttonh)
		
	def getCancelRect(self):
		return pygame.Rect(self.cancelbuttonx, self.buttonsy, self.largebuttonw, self.buttonh)
	
	def getTopBarRect(self):
		return pygame.Rect(self.topbarx, self.topbary, self.topbarwidth, self.buttonh)

	def getAmountRect(self):
		return pygame.Rect(self.amountx, self.amounty, self.amountw, self.buttonh)
		
	def getUpScrollRect(self):
		return pygame.Rect(self.scrollx, self.upy, self.scrollbuttonw, self.scrollbuttonh)
	
	def getDownScrollRect(self):
		return pygame.Rect(self.scrollx, self.downy, self.scrollbuttonw, self.scrollbuttonh)
		
class SSDisplayItem():
	
	def __init__(self, ssitem, visible=True):
		
		self.SnackspaceItem = ssitem
		
		self.descFormatPence = "%s (%dp)"
		self.descFormatPounds = u"%s (\xA3%.2f)"

		self.priceFormatPence = "%dp"
		self.priceFormatPounds = "\xA3%.2f"

		self.logger = logging.getLogger("MainScreen.GUI.Item")
		self.LCARSObjects = [None] * 3
	
	def collideOnRemove(self, pos):
		
		collide = False
		
		if self.__visible:
			try:
				collide = self.LCARSObjects[2].collidePoint(pos)
			except AttributeError:
				# Off-screen items might not have GUI objects.
				# This is OK.
				pass

		return collide
	
	def setVisible(self, visible):
		self.logger.info("Setting item %s visibility to '%s'" % 
			(self.SnackspaceItem.Description, "visible" if visible else "invisible"))
		self.__visible = visible

	def getVisible(self):
		return self.__visible
	
	def updateStrings(self):
		description = self.SnackspaceItem.Description
		priceinpence = self.SnackspaceItem.PriceEach
		totalprice = self.SnackspaceItem.TotalPrice
		
		self.description = self.formatDesciption(description, priceinpence)
		self.priceString = self.formatPrice(totalprice)
		
	def formatDesciption(self, description, priceinpence):
		if (priceinpence < 100):	
			description = self.descFormatPence % (description, priceinpence)
		else:
			description = self.descFormatPounds % (description, int(priceinpence) / 100)
		
		return description
	
	def formatPrice(self, priceinpence):
		if (priceinpence < 100):
			priceString = self.priceFormatPence % priceinpence
		else:
			priceString = self.priceFormatPounds % (int(priceinpence) / 100)
	
		return priceString

	def draw(self, Layout, yPosition, removeWidth, window):
	
		self.updateStrings()
		
		# Redraw description bar
		self.LCARSObjects[0] = LCARSCappedBar(
			pygame.Rect(Layout.descx, yPosition, Layout.descw, Layout.buttonh),
			CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, self.description, SS_FG, SS_BG, self.__visible)
		
		self.LCARSObjects[0].draw(window)
		
		# Redraw total price bar
		self.LCARSObjects[1] = LCARSCappedBar(
			pygame.Rect(Layout.pricex, yPosition, Layout.pricew, Layout.buttonh),
			CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, self.priceString, SS_FG, SS_BG, self.__visible)
	
		self.LCARSObjects[1].draw(window)
	
		# Redraw remove button
		self.LCARSObjects[2] = LCARSCappedBar(
			pygame.Rect(Layout.removex, yPosition, removeWidth, Layout.buttonh),
			CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "Remove", SS_FG, SS_BG, self.__visible)
		
		self.LCARSObjects[2].draw(window)
				
class SSMainScreenGUI(SSScreenGUI):

	def __init__(self, width, height, owner):
		
		SSScreenGUI.__init__(self, width, height, owner)
		self.border = SSBorder(width, height)
		
		self.setConstants()
		
		self.setVariables()
		
		# Array of SSDisplayItems
		self.displayitems = []
				
		# #
		# # Fixed position objects
		# #
		self.Layout = MainScreenLayout(width, height, self.border)
		
		self.objects = {
			self.DONE : LCARSCappedBar(self.Layout.getDoneRect(), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "Done", SS_FG, SS_BG, False),
			self.PAY : LCARSCappedBar(self.Layout.getPayRect(), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "Pay debt", SS_FG, SS_BG, False),
			self.CANCEL : LCARSCappedBar(self.Layout.getCancelRect(), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "Cancel", SS_FG, SS_BG, True),
			self.TOPBAR : LCARSCappedBar(self.Layout.getTopBarRect(), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "User: <No user scanned>", SS_FG, SS_BG, True),

			self.UP :	LCARSCappedBar(self.Layout.getUpScrollRect(), CapLocation.CAP_TOP, "UP", SS_FG, SS_BG, False),
			self.DOWN :	LCARSCappedBar(self.Layout.getDownScrollRect(), CapLocation.CAP_BOTTOM, "DN", SS_FG, SS_BG, False),
		
			self.AMOUNT: LCARSCappedBar(self.Layout.getAmountRect(), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "Total Spend: \xA30.00", SS_FG, SS_BG, True)
		}
	
		# #
		# # Import standard objects
		# #
		self.objects.update(self.border.getBorder());
	
	def setConstants(self):
		# Object constant definitions 
		# Reverse draw order - 0 drawn last
		self.DONE = 0
		self.CANCEL = 1
		self.PAY = 2
		self.TOPBAR = 3
		self.AMOUNT = 4
		self.UP = 5
		self.DOWN = 6
		self.ITEM = 7
		self.REMOVE = 8
		
		self.maxScreenItems = 5
		self.objectsPerItemRow = 3
	
	def setVariables(self):
		self.logger = logging.getLogger("MainScreen.GUI")
		self.topItemIndex = 0
		
	def addDisplayItem(self, item):
		
		if item not in [displayitem.SnackspaceItem for displayitem in self.displayitems]:
			self.displayitems.append(SSDisplayItem(item, True))	
	
	def updateTotal(self):
		self.objects[self.AMOUNT].setText("Total Spend: \xA3%.2f" % (self.owner.TotalPrice() / 100))
		
	def getItemAtPosition(self, pos):
		item = next((item.SnackspaceItem for item in self.displayitems if item.collideOnRemove(pos)), None)
		return item
	
	def removeItem(self, itemToRemove):
		self.logger.debug("Removing item %s" % itemToRemove.Barcode)
		self.displayitems = [item for item in self.displayitems if itemToRemove != item.SnackspaceItem]
		
		if self.topItemIndex > 0:
			self.topItemIndex -= 1
			
	def moveUp(self):
		self.logger.debug("UP button pressed")
		if self.topItemIndex > 0:
			self.topItemIndex -= 1
			
	def moveDown(self):
		self.logger.debug("DOWN button pressed")
		if (self.topItemIndex + self.maxScreenItems) < len(self.displayitems):
			self.topItemIndex += 1
	
	def removeButtonWidth(self):
		removew = self.w - self.Layout.removex - SS_BORDER
	
		if self.testDisplayDownButton() or self.testDisplayUpButton():
			removew -= (self.Layout.scrollbuttonw + SS_BORDER)
		
		return removew
	
	def getObjectId(self, pos):
		
		objectId = SSScreenGUI.getObjectId(self, pos) 
		
		if objectId == -1:
			# Try searching remove buttons
			for item in self.displayitems:
				if item.collideOnRemove(pos):
					objectId = self.REMOVE
							
		return objectId
	
	def setUnknownUser(self):
		self.objects[self.TOPBAR].setText("Username: <Unknown card>")
		
	def setUser(self, name, balance):
		if balance >= 0:
			self.objects[self.TOPBAR].setText(u"Username: %s (Balance: \xA3%.2f)" % (name, balance / 100))
		else:
			self.objects[self.TOPBAR].setText(u"Username: %s (Balance: -\xA3%.2f)" % (name, -balance / 100))
				
	def testDisplayUpButton(self):
		return (self.topItemIndex > 0)
	
	def testDisplayDownButton(self):
		return (self.topItemIndex + self.maxScreenItems) < len(self.displayitems)
	
	def clearItems(self):
		self.displayitems = []
		self.topItemIndex = 0
		
	def draw(self, window):
		window.fill(SS_BG)
	
		self.setShowHideItems()
		self.drawItems(window)
		self.drawStaticObjects(window)
		
		pygame.display.flip()

	def setShowHideItems(self):
		
		visibleCount = 0
		
		for (counter, item) in enumerate(self.displayitems):
		
			if (counter < self.topItemIndex):
				# Hide all the items above the list item top
				item.setVisible(False)
			elif visibleCount < self.maxScreenItems:
				# Show screen items based on their quantity
				item.setVisible(True)
				visibleCount += 1
			else:
				# Hide items below list bottom
				item.setVisible(False)
				
	def drawItems(self, window):
	
		yPosition = self.Layout.itemtopy
		
		# Iterate over all items in list
		for item in self.displayitems:
			if item.getVisible():
				item.draw(self.Layout, yPosition, self.removeButtonWidth(), window)
				yPosition += self.Layout.buttonh + SS_BORDER
		
	def drawStaticObjects(self, window):
		
		self.updateTotal()
		
		# # Draw border
		for drawObject in self.border.getBorder().values():		
			drawObject.draw(window)
		
		# Draw the fixed objects
		staticObjs = [
			self.objects[self.TOPBAR],
			self.objects[self.PAY],
			self.objects[self.CANCEL],
			self.objects[self.DONE],
			self.objects[self.AMOUNT],
			self.objects[self.UP],
			self.objects[self.DOWN]
		]
		
		# Decide which objects should be shown
		self.objects[self.PAY].visible = self.owner.UserLogged() and self.owner.UserInDebt()
		self.objects[self.DONE].visible = (len(self.displayitems) > 0) and self.owner.UserLogged()
		self.objects[self.UP].visible = self.testDisplayUpButton()
		self.objects[self.DOWN].visible = self.testDisplayDownButton()
		
		for staticObj in staticObjs:
			staticObj.draw(window)
		
		if self.banner is not None:
			self.banner.draw(window)
