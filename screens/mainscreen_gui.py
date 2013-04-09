from __future__ import division

import pygame
import logging

# # Safe wild import: all constants
from displayconstants import *  # @UnusedWildImport

from LCARSGui import LCARSCappedBar, CapLocation

from border import Border
from screen_gui import ScreenGUI

class MainScreenLayout:
	def __init__(self, width, height, border):
		
		self.productrowh = 100
		self.buttonw = 100
		self.largebuttonw = (self.buttonw * 2)
		self.buttonh = 50
		
		# # Spread buttons out between sweep and edge
		self.donebuttonx	 = border.innerX() + BORDER_W
		self.cancelbuttonx	 = width - BORDER_W - self.largebuttonw
		self.paybuttonx		 = (self.donebuttonx + self.cancelbuttonx) / 2
		
		self.buttonsy = height - BORDER_W - self.buttonh  # Put buttons at bottom of screen
		
		self.topbarx = border.innerX() + BORDER_W
		self.topbary = border.innerY() + BORDER_W
		
		self.innerWidth = width - self.topbarx - BORDER_W
		
		self.amounty = self.topbary
		self.amountw = 2 * self.buttonw
		self.amountx = width - BORDER_W - self.amountw 
		
		self.topbarwidth = self.innerWidth - self.amountw - BORDER_W
		
		self.producttopy = self.topbary + self.buttonh + BORDER_W
		self.productx = self.topbarx
		
		self.scrollbuttonh = (self.buttonsy - self.producttopy) / 2
		self.scrollbuttonh -= BORDER_W
		
		self.scrollbuttonw = self.buttonh 
		self.scrollx = width - BORDER_W - self.scrollbuttonw 
		self.upy = self.producttopy
		self.downy = self.upy + self.scrollbuttonh + BORDER_W
	
		self.setProductConstants()
		
	def setProductConstants(self):
		# Position constants for product objects
		self.descx = self.productx
		self.descw = self.largebuttonw * 1.8
		self.pricex = self.descx + self.descw + BORDER_W
		self.pricew = self.largebuttonw / 2
		self.removex = self.pricex + self.pricew + BORDER_W
	
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
		
class ProductDisplay():
	
	def __init__(self, product, visible=True):
		
		self.SnackspaceProduct = product
		
		self.descFormatPence = "%s (%dp)"
		self.descFormatPounds = u"%s (\xA3%.2f)"

		self.priceFormatPence = "%dp"
		self.priceFormatPounds = "\xA3%.2f"

		self.logger = logging.getLogger("MainScreen.GUI.Product")
		self.LCARSObjects = [None] * 3
	
	def collideOnRemove(self, pos):
		
		collide = False
		
		if self.__visible:
			try:
				collide = self.LCARSObjects[2].collidePoint(pos)
			except AttributeError:
				# Off-screen products might not have GUI objects.
				# This is OK.
				pass

		return collide
	
	def setVisible(self, visible):
		self.logger.info("Setting product %s visibility to '%s'" % 
			(self.SnackspaceProduct.Description, "visible" if visible else "invisible"))
		self.__visible = visible

	def getVisible(self):
		return self.__visible
	
	def updateStrings(self):
		description = self.SnackspaceProduct.Description
		priceinpence = self.SnackspaceProduct.PriceEach
		totalprice = self.SnackspaceProduct.TotalPrice
		
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
			CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, self.description, RGB_FG, RGB_BG, self.__visible)
		
		self.LCARSObjects[0].draw(window)
		
		# Redraw total price bar
		self.LCARSObjects[1] = LCARSCappedBar(
			pygame.Rect(Layout.pricex, yPosition, Layout.pricew, Layout.buttonh),
			CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, self.priceString, RGB_FG, RGB_BG, self.__visible)
	
		self.LCARSObjects[1].draw(window)
	
		# Redraw remove button
		self.LCARSObjects[2] = LCARSCappedBar(
			pygame.Rect(Layout.removex, yPosition, removeWidth, Layout.buttonh),
			CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "Remove", RGB_FG, RGB_BG, self.__visible)
		
		self.LCARSObjects[2].draw(window)
				
class MainScreenGUI(ScreenGUI):

	def __init__(self, width, height, owner):
		
		ScreenGUI.__init__(self, width, height, owner)
		self.border = Border(width, height)
		
		self.setConstants()
		
		self.setVariables()
		
		# Array of ProductDisplays
		self.productDisplays = []
				
		# #
		# # Fixed position objects
		# #
		self.Layout = MainScreenLayout(width, height, self.border)
		
		self.objects = {
			self.DONE : LCARSCappedBar(self.Layout.getDoneRect(), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "Done", RGB_FG, RGB_BG, False),
			self.PAY : LCARSCappedBar(self.Layout.getPayRect(), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "Pay debt", RGB_FG, RGB_BG, False),
			self.CANCEL : LCARSCappedBar(self.Layout.getCancelRect(), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "Cancel", RGB_FG, RGB_BG, True),
			self.TOPBAR : LCARSCappedBar(self.Layout.getTopBarRect(), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "User: <No user scanned>", RGB_FG, RGB_BG, True),

			self.UP :	LCARSCappedBar(self.Layout.getUpScrollRect(), CapLocation.CAP_TOP, "UP", RGB_FG, RGB_BG, False),
			self.DOWN :	LCARSCappedBar(self.Layout.getDownScrollRect(), CapLocation.CAP_BOTTOM, "DN", RGB_FG, RGB_BG, False),
		
			self.AMOUNT: LCARSCappedBar(self.Layout.getAmountRect(), CapLocation.CAP_LEFT + CapLocation.CAP_RIGHT, "Total Spend: \xA30.00", RGB_FG, RGB_BG, True)
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
		self.PRODUCT = 7
		self.REMOVE = 8
		
		self.maxScreenProducts = 5
		self.objectsPerProductRow = 3
	
	def setVariables(self):
		self.logger = logging.getLogger("MainScreen.GUI")
		self.topProductIndex = 0
		
	def addToProductDisplay(self, product):
		
		if product not in [displayproduct.SnackspaceProduct for displayproduct in self.productDisplays]:
			self.productDisplays.append(ProductDisplay(product, True))	
	
	def updateTotal(self):
		self.objects[self.AMOUNT].setText("Total Spend: \xA3%.2f" % (self.owner.TotalPrice() / 100))
		
	def getProductAtPosition(self, pos):
		product = next((product.SnackspaceProduct for product in self.productDisplays if product.collideOnRemove(pos)), None)
		return product
	
	def removeProduct(self, productToRemove):
		self.logger.debug("Removing product %s" % productToRemove.Barcode)
		self.productDisplays = [product for product in self.productDisplays if productToRemove != product.SnackspaceProduct]
		
		if self.topProductIndex > 0:
			self.topProductIndex -= 1
			
	def moveUp(self):
		self.logger.debug("UP button pressed")
		if self.topProductIndex > 0:
			self.topProductIndex -= 1
			
	def moveDown(self):
		self.logger.debug("DOWN button pressed")
		if (self.topProductIndex + self.maxScreenProducts) < len(self.productDisplays):
			self.topProductIndex += 1
	
	def removeButtonWidth(self):
		removew = self.w - self.Layout.removex - BORDER_W
	
		if self.testDisplayDownButton() or self.testDisplayUpButton():
			removew -= (self.Layout.scrollbuttonw + BORDER_W)
		
		return removew
	
	def getObjectId(self, pos):
		
		objectId = ScreenGUI.getObjectId(self, pos) 
		
		if objectId == -1:
			# Try searching remove buttons
			for product in self.productDisplays:
				if product.collideOnRemove(pos):
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
		return (self.topProductIndex > 0)
	
	def testDisplayDownButton(self):
		return (self.topProductIndex + self.maxScreenProducts) < len(self.productDisplays)
	
	def clearProducts(self):
		self.productDisplays = []
		self.topProductIndex = 0
		
	def draw(self, window):
		window.fill(RGB_BG)
	
		self.setShowHideProducts()
		self.drawProducts(window)
		self.drawStaticObjects(window)
		
		pygame.display.flip()

	def setShowHideProducts(self):
		
		visibleCount = 0
		
		for (counter, product) in enumerate(self.productDisplays):
		
			if (counter < self.topProductIndex):
				# Hide all the products above the list product top
				product.setVisible(False)
			elif visibleCount < self.maxScreenProducts:
				# Show screen products based on their quantity
				product.setVisible(True)
				visibleCount += 1
			else:
				# Hide products below list bottom
				product.setVisible(False)
				
	def drawProducts(self, window):
	
		yPosition = self.Layout.producttopy
		
		# Iterate over all products in list
		for product in self.productDisplays:
			if product.getVisible():
				product.draw(self.Layout, yPosition, self.removeButtonWidth(), window)
				yPosition += self.Layout.buttonh + BORDER_W
		
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
		self.objects[self.PAY].visible = self.owner.UserLogged() and self.owner.UserAllowCredit()
		self.objects[self.DONE].visible = (len(self.productDisplays) > 0) and self.owner.UserLogged()
		self.objects[self.UP].visible = self.testDisplayUpButton()
		self.objects[self.DOWN].visible = self.testDisplayDownButton()
		
		for staticObj in staticObjs:
			staticObj.draw(window)
		
		if self.banner is not None:
			self.banner.draw(window)
