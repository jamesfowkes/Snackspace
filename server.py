import socket

import argparse

import logging

from ssdblocal import SSDbLocal
from ssxml import SSMessage

class SSServer:
	
	def __init__(self, localmode, db):
		
		logging.basicConfig(level=logging.DEBUG)
		self.logger = logging.getLogger("SSServer")
		
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
		if localmode:
			server_address = ('localhost', 10000)
		else:
			server_address = (socket.gethostname(),0)
		
		self.logger.info('Server starting up on %s port %s' % server_address)
		
		sock.bind(server_address)
		
		sock.listen(1)
		
		#Wait for connection from client
		while(True):
			
			self.logger.info("Waiting for client to connect...")
			
			connection, client_address = sock.accept()
			data = ""
			
			self.logger.info("Waiting for client at %s port %s" % client_address)
			try:
				length = int(connection.recv(5))
				self.logger.info("Receiving %d bytes" % length)
				data = connection.recv(length)
				returndata = self.HandleMessage(data, db)
				if (returndata is not None):
					
					self.logger.info("Sending %s" % returndata)
					
					length = len(returndata)
					returndata = "%5s%s" % (length, returndata)
					
					connection.sendall(returndata)
			finally:
				connection.close()

	def HandleMessage(self, message, db):
	
		reply = None
		actions = SSMessage.ParseXML(message)
		
		for action, data in actions.items():
			
			self.logger.info("Handling '%s' action..." % action)
			
			if action == "ping":
				reply = SSMessage("pingreply").GetXML()
			elif action == "getitem":
				reply = db.GetItem(data)
			elif action == "getuser":
				reply = db.GetUser(data)
			elif action == "transactions":
				reply = db.ApplyTransactions(data)
			elif action == "additem":
				reply = db.AddItem(data)
			elif action == "addcredit":
				reply = db.AddCredit(data)
			elif action == "pingreply":
				pass # No action required for ping reply
			else:
				self.logger.warning("Unknown action '%s'" % action)
				
		return reply
		
			
def main(argv = None):
	
	parser = argparse.ArgumentParser(description='Snackspace Server')
	parser.add_argument('-L', dest='localmode', nargs='?',default='n', const='y')
	
	args = parser.parse_args()
	
	db = SSDbLocal();
	
	if args.localmode == 'y':
		__server = SSServer(True, db)
	else:
		__server = SSServer(False, db)
		
	
if __name__ == "__main__":
	main()
	
	
