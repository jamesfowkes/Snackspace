import socket

import argparse #@UnresolvedImport

import logging

from dblocal import DbLocal
from messaging import Message

class Server:
	
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
	
		actions = Message.ParseXML(message)
		
		reply = db.ProcessActions(actions)
		
		return reply
		
			
def main(argv = None):
	
	parser = argparse.ArgumentParser(description='Snackspace Server')
	parser.add_argument('-L', dest='localmode', nargs='?',default='n', const='y')
		
	args = parser.parse_args()

	db = DbLocal(args.localmode == 'y');
	__server = Server(args.localmode == 'y', db)

	
if __name__ == "__main__":
	main()
	
	
