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
		
		self.pendingActions = []
		
		self.db = db(self.useTestDb)

	def ProcessActions(self, actions):
		
		reply = Message()
		
		for action in actions:
			
			self.logger.info("Handling '%s' action..." % action.Action)
			
			if action.Action == "ping":
				reply.AddAction( Packet("pingreply") )
			elif action.Action == "getproduct":
				reply.AddAction( self.GetProduct(action.Data) )
			elif action.Action == "getuser":
				reply.AddAction( self.GetUser(action.Data) )
			elif action.Action == "transaction":
				reply.AddAction( self.ApplyTransaction(action.Data) )
			elif action.Action == "addproduct":
				reply.AddAction ( self.AddProduct(action.Data) )
			elif action.Action == "addcredit":
				reply.AddAction( self.AddCredit(action.Data) )
			elif action.Action == "pingreply":
				pass # No action required for ping reply
			else:
				self.logger.warning("Unknown action '%s'" % action.Action)
		
		self.actions = []
		
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

	
	def AddCredit(self, memberID, amount):
		self.logger.info("Adding %s credit to user %s" % (amount, memberID))
	
	def __productFromBarcode(self, barcode):
		
		datatype = 'productdata'
		data = 	{'barcode': '0', 'description': '', 'priceinpence':'0'}

		result = self.db.GetProduct(barcode)
		
		if result is not None:
			data['barcode'] = result['barcode']
			data['description'] = result['shortdesc']
			data['priceinpence'] = result['price']
		
		action = Packet(datatype, data)
	
		return action
	
	
	def __userFromRFID(self, rfid):
		
		datatype = 'userdata'
		data = 	{'memberid': '0', 'username': '', 'balance':'0','limit':'0'}

		result = self.db.GetUser(rfid)
		
		if result is not None:
			data['memberid'] = result['memberid']
			data['username'] = result['username']
			data['balance'] = result['balance']
			data['limit'] = result['limit']
		
		action = Packet(datatype, data)
			
		return action
	

	def ApplyTransaction(self, data):
		
		memberid = data['memberid']
		barcode = data['barcode']
		count = int(data['count'])
		
		result = self.db.Transaction(memberid, barcode, count)
		
		action = Packet("transaction", {"barcode":barcode, "result": "Success" if result else "Fail", "memberid":memberid})
			
		return action

