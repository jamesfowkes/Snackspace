import socket
import logging

import signal

from ssxml import SSMessage, SSAction

from xml.dom.minidom import parseString

class TimeoutException(Exception): 
	pass 

class SSDbRemote:

	def __init__(self, local):
		
		self.__setVariables(local)
		self.__testConnection()
		
	##
	## Public Functions
	##
	
	#def Send(self, message, callback):
		
	#	reply, received = self.__send(message, callback)
	#	callback(reply, received, self.__connected)
	
	def GetItem(self, barcode):
		action = SSAction("getitem", {"barcode":barcode})
		message = SSMessage(action).GetXML()
		try:
			reply, _recvd = self.__send(message)
			reply = SSMessage.ParseXML(reply)
			reply = reply[0]
			
			if reply.Action == "itemdata":
				desc = reply.Data['description']
				priceinpence = reply.Data['priceinpence']
				return (barcode, desc, priceinpence)
			else:
				return None
				
			
		
		except:
			return None
		
	def GetUserData(self, rfid):
		action = SSAction("getuser", {"rfid":rfid})
		message = SSMessage(action).GetXML()
		try:
			reply, _recvd = self.__send(message)
			reply = SSMessage.ParseXML(reply)
			reply = reply[0]
			
			if reply.Action == "userdata":
				username = reply.Data['username']
				balance = reply.Data['balance']
				limit = reply.Data['limit']
				memberID = reply.Data['memberid']
				self.logger.info("Got user %s" % username)
				return (memberID, username, balance, limit)
			
			else:
				self.logger.info("Unrecognised rfid %s" % rfid)
				return None
			

		except:
			pass
		
	def SendTransactions(self, itemdata, memberID):
		
		self.logger.info("Sending transactions")
		
		message = SSMessage()
		
		for (barcode, count) in itemdata:
			action = SSAction("transaction", {"barcode":barcode,"memberid":memberID, "count":count})
			message.AddAction(action)
		
		try:
			reply, _recvd = self.__send(message.GetXML())
			reply = SSMessage.ParseXML(reply)
			print reply
			return self.__transactionsSuccessful(reply)
		except:
			raise
		
	def AddItem(self, barcode, description, priceinpence):
		action = SSAction("additem", {"barcode":barcode, "description":description, "priceinpence":priceinpence})
		message = SSMessage(action).GetXML()
		try:
			reply, _recvd = self.__send(message)
			reply = SSMessage.ParseXML(reply)
		except:
			return None
		
	def AddCredit(self, memberID, amountinpence):
		action = SSAction("addcredit", {"memberID":memberID, "amountinpence":amountinpence})
		message = SSMessage(action).GetXML()
		try:
			reply, _recvd = self.__send(message)
			reply = SSMessage.ParseXML(reply)
		except:
			pass
		
	##
	## Private Functions
	##
	
	def __setVariables(self,local):
		
		self.__local = local
		
		self.__foundServer = False
		self.__callback = None

		if self.__local:
			self.server_address = ('localhost', 10000)
		else:
			self.server_address = ''
		
		logging.basicConfig(level=logging.DEBUG)
		self.logger = logging.getLogger("RemoteDB")
		
	def __testConnection(self):
		## Assume we are connected initially
		## to let __send method work
		self.__foundServer = True
		message = SSMessage("ping")
		reply, received = self.__send(message.GetXML())
		
		if received > 0:
			actions = SSMessage.ParseXML(reply)
			
			if actions[0].Action == 'pingreply':
				self.logger.info("Connected to remote server")
				self.__foundServer = True
			else:
				self.logger.info("Unexpected reply from remote server")
				self.__foundServer = False
		else:
			self.logger.info("No reply to ping received!")
			self.__foundServer = False
			
	def __send(self, message):
		
		received = 0
		data = ''
		
		if self.__foundServer:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			
			signal.signal(signal.SIGALRM, self.__timeoutHandler) 
			signal.alarm(10)
			
			try:
				self.sock.connect(self.server_address)
				
				self.logger.info("Sending %s" % message)
				
				length = len(message)
				message = "%5s%s" % (length, message)
				
				self.sock.sendall(message)
	
				length = int(self.sock.recv(5))
				data = self.sock.recv(length)
				
				signal.alarm(0)
				received = len(data)
				
			except TimeoutException:
				received = 0
				data = ''

			except socket.error as e:
				self.logger.info("Socket open failed with '%s'" % e.strerror)
				signal.alarm(0)
				received = 0
				data = ''

			finally:
				self.sock.close()

		return data, received
		
	def __timeoutHandler(self, signum, frame):
		self.__foundServer = False;
		raise TimeoutException
		
	def __parseReply(self, message):
		dom = parseString(message)
	
		actions = dom.getElementsByTagName('action')
		
		for action in actions:
			actiontype = action.attributes.getNamedItem("type").value
				
			if actiontype == "ping":
				return SSMessage("pingreply")
	
	def __transactionsSuccessful(self, reply):
		
		for action in reply:
			if action.Action == "transaction":
				print action.Data['result']
			
		return True
		
	##
	## Property getters
	##
	@property
	def isConnected(self): 
		return self.__foundServer