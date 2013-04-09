import socket
import logging

import signal

from messaging import Message, Packet

from xml.dom.minidom import parseString

class TimeoutException(Exception): 
	pass 

class DbClient:

	def __init__(self, local):
		
		self.__setVariables(local)
		self.__testConnection()
		
	##
	## Public Functions
	##
	
	#def Send(self, message, callback):
		
	#	reply, received = self.__send(message, callback)
	#	callback(reply, received, self.__connected)
	
	def GetProduct(self, barcode):
		packet = Packet("getproduct", {"barcode":barcode})
		message = Message(packet).GetXML()
		try:
			reply, _recvd = self.__send(message)
			reply = Message.ParseXML(reply)
			reply = reply[0]
			
			if reply.Type == "productdata":
				desc = reply.Data['description']
				priceinpence = reply.Data['priceinpence']
				return (barcode, desc, priceinpence)
			else:
				return None
				
			
		
		except:
			return None
		
	def GetUserData(self, rfid):
		packet = Packet("getuser", {"rfid":rfid})
		message = Message(packet).GetXML()
		try:
			reply, _recvd = self.__send(message)
			reply = Message.ParseXML(reply)
			reply = reply[0]
			
			if reply.Type == "userdata":
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
		
	def SendTransactions(self, productdata, memberID):
		
		self.logger.info("Sending transactions")
		
		message = Message()
		
		for (barcode, count) in productdata:
			packet = Packet("transaction", {"barcode":barcode,"memberid":memberID, "count":count})
			message.AddPacket(packet)
		
		try:
			reply, _recvd = self.__send(message.GetXML())
			reply = Message.ParseXML(reply)
			return self.__transactionsSuccessful(reply)
		except:
			raise
		
	def AddProduct(self, barcode, description, priceinpence):
		packet = Packet("addproduct", {"barcode":barcode, "description":description, "priceinpence":priceinpence})
		message = Message(packet).GetXML()
		try:
			reply, _recvd = self.__send(message)
			reply = Message.ParseXML(reply)
		except:
			return None
		
	def AddCredit(self, memberID, amountinpence):
		packet = Packet("addcredit", {"memberid":memberID, "amountinpence":amountinpence})
		message = Message(packet).GetXML()
		try:
			reply, _recvd = self.__send(message)
			reply = Message.ParseXML(reply)
			return self.__addCreditSuccessful(reply)
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
		self.logger = logging.getLogger("DBClient")
		
	def __testConnection(self):
		## Assume we are connected initially
		## to let __send method work
		self.__foundServer = True
		message = Message("ping")
		reply, received = self.__send(message.GetXML())
		
		if received > 0:
			packets = Message.ParseXML(reply)
			
			if packets[0].Type == 'pingreply':
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
	
		packets = dom.getElementsByTagName('packet')
		
		for packet in packets:
			packettype = packet.attributes.getNamedItem("type").value
				
			if packettype == "ping":
				return Message("pingreply")
	
	def __transactionsSuccessful(self, reply):

		success = True
				
		for packet in reply:
			if packet.Type == "result" and packet.Data['action'] == "transaction":
				success = success and (packet.Data['result'] == "Success")
		
		return success
	
	def __addCreditSuccessful(self, reply):

		if reply.Type == "result" and reply.Data['action'] == "addcredit":
			success = (reply.Data['result'] == "Success")
		return success
	##
	## Property getters
	##
	@property
	def isConnected(self): 
		return self.__foundServer