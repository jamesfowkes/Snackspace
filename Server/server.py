"""
server.py

Server-side TCP comms layer

"""

import socket

import argparse #@UnresolvedImport

import ConfigParser

import logging

from dbserver import DbServer
from messaging import Message

class Server:
    """ Implementation of the Server """
    
    def __init__(self, local_mode, database):

        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger("SSServer")

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dbase = database

        if local_mode:
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
            except socket.error:
                server_port = server_port + 1

        if started:
            self.server_loop()
        else:
            self.logger.error("Could not start server on any port on %s!" % server_host)

    def server_loop(self):

        """ Server loops here listening for connections """
        
        self.sock.listen(1)

        #Wait for connection from client
        while(True):

            self.logger.info("Waiting for client to connect...")

            connection, client_address = self.sock.accept()
            data = ""

            self.logger.info("Waiting for client at %s port %s" % client_address)
            try:
                ## The recv and sendall methods are dynamically bound
                ## to the socket object, so pylint complains about them
                ## not existing. E1101 is disabled for these lines
                length = int(connection.recv(5)) #pylint: disable=E1101
                self.logger.info("Receiving %d bytes" % length)
                data = connection.recv(length) #pylint: disable=E1101
                returndata = self.handle_message(data)
                if (returndata is not None):

                    self.logger.info("Sending %s" % returndata)

                    length = len(returndata)
                    returndata = "%5s%s" % (length, returndata)

                    connection.sendall(returndata) #pylint: disable=E1101
            finally:
                connection.close()

    def handle_message(self, message):
        """ Pass message to database layer and get reply """ 
        packets = Message.parse_xml(message)

        reply = self.dbase.process_packets(packets)

        return reply

def main(_argv = None):
    
    """ The entry point for the snackspace server """
    
    ## Read arguments from command line
    argparser = argparse.ArgumentParser(description='Snackspace Server')
    argparser.add_argument('--file', dest='conffile', nargs='?', default='')
    argparser.add_argument('-L', dest='localmode', nargs='?', default='n', const='y')

    args = argparser.parse_args()

    ## Read arguments from configuration file
    try:
        confparser = ConfigParser.ConfigParser()
        confparser.readfp(open(args.conffile))
    except IOError:
        ## Configuration file does not exist, or no filename supplied
        confparser = None
        
    if confparser is None:
        ## Use command line options
        localmode = args.localmode == 'y'
    else:
        ## Use configuration file options:
        localmode = confparser.get('ServerConfig','localmode') == 'y'

    database = DbServer(localmode)
    __server = Server(localmode, database)


if __name__ == "__main__":
    main()
