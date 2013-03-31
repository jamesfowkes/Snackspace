from ssxml import SSMessage

from xml.dom.minidom import parse

import logging

from db import db

class SSDbLocal:

	def __init__(self, useTestDb):
		
		self.useTestDb = useTestDb
		self.__setVariables()

	def __setVariables(self):
		logging.basicConfig(level=logging.DEBUG)
		self.logger = logging.getLogger("LocalDB")
		
		self.db = db(self.useTestDb)

		
	def GetItem(self, data):
		barcode = data['barcode']
		
		self.logger.info("Getting item %s" % barcode)
		
		return self.__itemFromBarcode(barcode)
	
	def GetUser(self, data):
		rfid = data['rfid']
		
		self.logger.info("Getting user %s" % rfid)
		
		return self.__userFromRFID(rfid) 
	
	def ApplyTransactions(self, data):
		rfids = data['rfid']
		barcodes = data['barcode']
		
		self.logger.info("Applying transactions")
		
		return self.__ApplyTransactions(rfids, barcodes)
	
	def AddItem(self, barcode):
		self.logger.info("Adding new item %s" % barcode)

	
	def AddCredit(self, memberID, amount):
		self.logger.info("Adding %s credit to user %s" % (amount, memberID))
	
	def __itemFromBarcode(self, barcode):
		
		datatype = 'itemdata'
		data = 	[
					{'barcode': '0'},
					{'description': ''},
					{'priceinpence':'0'}
				]

		result = self.db.GetItem(barcode)
		
		if result is not None:
			data[0]['barcode'] = result['barcode']
			data[1]['description'] = result['shortdesc']
			data[2]['priceinpence'] = result['price']
				
		xml = SSMessage(datatype, data).GetXML()
		
		return xml
	
	
	def __userFromRFID(self, rfid):
		
		datatype = 'userdata'
		data = 	[
					{'memberid': '0'},
					{'username': ''},
					{'balance':'0'},
					{'limit':'0'}
				]

		result = self.db.GetUser(rfid)
		
		if result is not None:
			data[0]['memberid'] = result['memberid']
			data[1]['username'] = result['username']
			data[2]['balance'] = result['balance']
			data[3]['limit'] = result['limit']
				
		xml = SSMessage(datatype, data).GetXML()
		
		return xml
	

	def __ApplyTransactions(self, memberid, barcodes):
		
		###########################################################
		### FAKE DB ACCESS										###
		###########################################################

		###########################################################
		### END FAKE DB ACCESS									###
		###########################################################	
		
		reply = SSMessage()
		
		for barcode in barcodes:
			reply.AddAction("transaction", {"barcode":barcode, "result":"1"})
		
		return reply.GetXML()

