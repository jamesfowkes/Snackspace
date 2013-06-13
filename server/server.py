import socket

import argparse #@UnresolvedImport

import ConfigParser

import logging

from dbserver import DbServer
from messaging import Message

class Server:
	
	def __init__(self, localmode, db):
		
		logging.basicConfig(level=logging.DEBUG)
		self.logger = logging.getLogger("SSServer")
		
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.db = db
		
		if localmode:
			server_host = 'localhost'
			
		else:
			server_host = socket.gethostname()
		
		server_port = 10000
		
		started = False
		
		while (not started) and (server_port < 11000):
			server_address = (server_host, server_port)
			try:
				self.logger.info('Trying server start on %s port %s' % server_address)
				self.sock.bind(server_address)
				started = True
			except:
				server_port = server_port + 1 
						
		if started:
			self.ServerLoop()
		else:
			self.logger.error("Could not start server on any port on %s!" % server_host)
	
	def ServerLoop(self):
		
		self.sock.listen(1)
			
		#Wait for connection from client
		while(True):
			
			self.logger.info("Waiting for client to connect...")
			
			connection, client_address = self.sock.accept()
			data = ""
			
			self.logger.info("Waiting for client at %s port %s" % client_address)
			try:
				length = int(connection.recv(5))
				self.logger.info("Receiving %d bytes" % length)
				data = connection.recv(length)
				returndata = self.HandleMessage(data, self.db)
				if (returndata is not None):
					
					self.logger.info("Sending %s" % returndata)
					
					length = len(returndata)
					returndata = "%5s%s" % (length, returndata)
					
					connection.sendall(returndata)
			finally:
				connection.close()

	def HandleMessage(self, message, db):
	
		packets = Message.ParseXML(message)
		
		reply = db.ProcessPackets(packets)
		
		return reply
				
def main(argv = None):
	
	## Read arguments from command line
	argparser = argparse.ArgumentParser(description='Snackspace Server')
	argparser.add_argument('--file', dest='conffile', nargs='?',default='')
	argparser.add_argument('-L', dest='localmode', nargs='?',default='n', const='y')
	
	args = argparser.parse_args()
	
	## Read arguments from configuration file
	try:
		confparser = ConfigParser.ConfigParser()
		confparser.readfp(open(args.conffile))
		
	except IOError:
		## Configuration file does not exist, or no filename supplied
		confparser = None
		pass
	
	if confparser is None:
		## Use command line options
		localmode = args.localmode == 'y'
	else:
		## Use configuration file options:
		localmode = confparser.get('ServerConfig','localmode') == 'y'
		
	db = DbServer(localmode);
	__server = Server(localmode, db)

	
if __name__ == "__main__":
	main()
	
	
