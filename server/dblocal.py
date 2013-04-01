from messaging import Message, Packet

import logging

from db import db

class DbLocal:

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
			elif action.Action == "getitem":
				reply.AddAction( self.GetItem(action.Data) )
			elif action.Action == "getuser":
				reply.AddAction( self.GetUser(action.Data) )
			elif action.Action == "transaction":
				reply.AddAction( self.ApplyTransaction(action.Data) )
			elif action.Action == "additem":
				reply.AddAction ( self.AddItem(action.Data) )
			elif action.Action == "addcredit":
				reply.AddAction( self.AddCredit(action.Data) )
			elif action.Action == "pingreply":
				pass # No action required for ping reply
			else:
				self.logger.warning("Unknown action '%s'" % action.Action)
		
		self.actions = []
		
		return reply.GetXML()
		
	def GetItem(self, data):
		barcode = data['barcode']
		
		self.logger.info("Getting item %s" % barcode)
		
		return self.__itemFromBarcode(barcode)
	
	def GetUser(self, data):
		rfid = data['rfid']
		
		self.logger.info("Getting user %s" % rfid)
		
		return self.__userFromRFID(rfid) 
	
	def AddItem(self, barcode):
		self.logger.info("Adding new item %s" % barcode)

	
	def AddCredit(self, memberID, amount):
		self.logger.info("Adding %s credit to user %s" % (amount, memberID))
	
	def __itemFromBarcode(self, barcode):
		
		datatype = 'itemdata'
		data = 	{'barcode': '0', 'description': '', 'priceinpence':'0'}

		result = self.db.GetItem(barcode)
		
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
		count = data['count']
		
		result = self.db.Transaction(memberid, barcode, count)
		
		action = Packet("transaction", {"barcode":barcode, "result":"YES!", "memberid":memberid})
			
		return action

