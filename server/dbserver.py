from messaging import Message, Packet

import logging

from db import db

class DbServer:

	def __init__(self, useTestDb):
		
		self.useTestDb = useTestDb
		self.__setVariables()

	def __setVariables(self):
		logging.basicConfig(level=logging.DEBUG)
		self.logger = logging.getLogger("LocalDB")
		
		self.db = db(self.useTestDb)

	def ProcessPackets(self, packets):
		
		reply = Message()
		
		for packet in packets:
			
			self.logger.info("Handling '%s' packet..." % packet.Type)
			
			if packet.Type == "ping":
				reply.AddPacket( Packet("pingreply") )
			elif packet.Type == "getproduct":
				reply.AddPacket( self.GetProduct(packet.Data) )
			elif packet.Type == "getuser":
				reply.AddPacket( self.GetUser(packet.Data) )
			elif packet.Type == "transaction":
				reply.AddPacket( self.ApplyTransaction(packet.Data) )
			elif packet.Type == "addproduct":
				reply.AddPacket ( self.AddProduct(packet.Data) )
			elif packet.Type == "addcredit":
				reply.AddPacket( self.AddCredit(packet.Data) )
			elif packet.Type == "pingreply":
				pass # No action required for ping reply
			else:
				self.logger.warning("Unknown packet '%s'" % packet.Type)
		
		self.packets = []
		
		return reply.GetXML()
		
	def GetProduct(self, data):
		barcode = data['barcode']
		
		self.logger.info("Getting product %s" % barcode)
		
		return self.__productFromBarcode(barcode)
	
	def GetUser(self, data):
		rfid = data['rfid']
		
		self.logger.info("Getting user %s" % rfid)
		
		return self.__userFromRFID(rfid) 
	
	def AddProduct(self, barcode):
		self.logger.info("Adding new product %s" % barcode)

	
	def AddCredit(self, data):
		memberid = data['memberid']
		amountinpence = int(data['amountinpence'])
		
		self.logger.info("Adding %s credit to member %s" % (amountinpence, memberid))
		
		result = self.db.AddCredit(memberid, amountinpence)
	
		packet = Packet("result", {"action":"addcredit", "result": "Success" if result else "Fail", "memberid":memberid})
		
		return packet
	
	def ApplyTransaction(self, data):
		
		memberid = data['memberid']
		barcode = data['barcode']
		count = int(data['count'])
		
		result = self.db.Transaction(memberid, barcode, count)
		
		packet = Packet("result", {"action":"transaction", "barcode":barcode, "result": "Success" if result else "Fail", "memberid":memberid})
			
		return packet
	
	def __productFromBarcode(self, barcode):
		
		datatype = 'productdata'
		data = 	{'barcode': '0', 'description': '', 'priceinpence':'0'}

		result = self.db.GetProduct(barcode)
		
		if result is not None:
			data['barcode'] = result['barcode']
			data['description'] = result['shortdesc']
			data['priceinpence'] = result['price']
		
		packet = Packet(datatype, data)
	
		return packet
	
	
	def __userFromRFID(self, rfid):
		
		datatype = 'userdata'
		data = 	{'memberid': '0', 'username': '', 'balance':'0','limit':'0'}

		result = self.db.GetUser(rfid)
		
		if result is not None:
			data['memberid'] = result['memberid']
			data['username'] = result['username']
			data['balance'] = result['balance']
			data['limit'] = result['limit']
		
		packet = Packet(datatype, data)
			
		return packet
	