from ssxml import SSMessage

from xml.dom.minidom import parse

import logging

class SSDbLocal:

	def __init__(self):
		
		self.__setVariables()

	def __setVariables(self):
		logging.basicConfig(level=logging.DEBUG)
		self.logger = logging.getLogger("LocalDB")
		
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

	
	def AddCredit(self, rfid, amount):
		self.logger.info("Adding %s credit to user %s" % (amount, rfid))
	
	def __itemFromBarcode(self, barcode):
		
		###########################################################
		### FAKE DB ACCESS										###
		###########################################################
		datatype = 'itemdata'
		data = 	[
					{'barcode': '0'},
					{'description': ''},
					{'priceinpence':'0'}
				]

		dom = parse("data/data.xml")
	
		items = dom.getElementsByTagName('item')
		
		for item in items:
			if item.getElementsByTagName('barcode')[0].childNodes[0].nodeValue == barcode:
				data[0]['barcode'] = barcode
				data[1]['description'] = item.getElementsByTagName('description')[0].childNodes[0].nodeValue
				data[2]['priceinpence'] = item.getElementsByTagName('priceinpence')[0].childNodes[0].nodeValue
				
		###########################################################
		### END FAKE DB ACCESS									###
		###########################################################
		xml = SSMessage(datatype, data).GetXML()
		
		return xml
	
	
	def __userFromRFID(self, rfid):
		
		###########################################################
		### FAKE DB ACCESS										###
		###########################################################
		datatype = 'userdata'
		data = 	[
					{'rfid': '0'},
					{'username': ''},
					{'balance':'0'},
					{'limit':'0'}
				]

		dom = parse("data/data.xml")
	
		users = dom.getElementsByTagName('user')
		
		for user in users:
			if user.getElementsByTagName('rfid')[0].childNodes[0].nodeValue == rfid:
				data[0]['rfid'] = rfid
				data[1]['username'] = user.getElementsByTagName('username')[0].childNodes[0].nodeValue
				data[2]['balance'] = user.getElementsByTagName('balance')[0].childNodes[0].nodeValue
				data[3]['limit'] = user.getElementsByTagName('limit')[0].childNodes[0].nodeValue
				
		###########################################################
		### END FAKE DB ACCESS									###
		###########################################################
		xml = SSMessage(datatype, data).GetXML()
		
		return xml
	

	def __ApplyTransactions(self, rfids, barcodes):
		
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
	
	
	
	
	
	
