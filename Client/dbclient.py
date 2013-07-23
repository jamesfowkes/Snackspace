""" dbclient.py

Implements low-level functionality to communicate with 
the database server
"""
 
import socket
import logging

import signal

from messaging import Message, Packet

from xml.dom.minidom import parseString

class BadReplyException(Exception):
    """ Exception raised when a message to the server does not receive the expected reply """
    pass

class TimeoutException(Exception):
    """ Exception raised when socket fails to receive response """
    pass

class DbClient:

    """ Implementation of DbClient class """
    def __init__(self, local):

        """ Add a new product to the database """
        self.local = local
        self.sock = None
        
        self.found_server = False
        self.callback = None

        if self.local:
            self.server_host = 'localhost'
        else:
            self.server_host = ''

        self.server_address = ()
        
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger("DBClient")

        self.find_server()

    def ping_server(self):
        """ If the server was there the last time, test the connection again.
        If not, try to find it. """
        if self.found_server:
            self.test_connection()
        else:
            self.find_server()

        return self.found_server

    def get_product(self, barcode):
        """ Get the product data associated with the barcode """
        packet = Packet("getproduct", {"barcode":barcode})
        message = Message(packet).get_xml()

        reply, _recvd = self.send(message)
        reply = Message.parse_xml(reply)
        reply = reply[0]

        if reply.type == "productdata":
            desc = reply.data['description']
            priceinpence = reply.data['priceinpence']
            return (barcode, desc, priceinpence)
        elif reply.type == 'unknownproduct':
            return None
        else:
            raise BadReplyException

    def get_user_data(self, rfid):
        """ Get the user data associated with the rfid """
        packet = Packet("getuser", {"rfid":rfid})
        message = Message(packet).get_xml()

        reply, _recvd = self.send(message)
        reply = Message.parse_xml(reply)
        reply = reply[0]

        if reply.type == "userdata":
            username = reply.data['username']
            balance = reply.data['balance']
            limit = reply.data['limit']
            member_id = reply.data['memberid']
            self.logger.info("Got user %s" % username)
            return (member_id, username, balance, limit)

        else:
            self.logger.info("Unrecognised rfid %s" % rfid)
            return None

    def send_transactions(self, productdata, member_id):
        """ Send transaction requests to the server """
        self.logger.info("Sending transactions")

        message = Message()

        for (barcode, count) in productdata:
            packet = Packet("transaction", {"barcode":barcode, "memberid":member_id, "count":count})
            message.add_packet(packet)

        reply, _recvd = self.send(message.get_xml())
        reply = Message.parse_xml(reply)
        return transactions_successful(reply)

    def add_product(self, barcode, description, price_in_pence):
        """ Add a new product to the database """
        packet = Packet("addproduct", {"barcode":barcode, "description":description, "price_in_pence":price_in_pence})
        message = Message(packet).get_xml()

        reply, _recvd = self.send(message)
        reply = Message.parse_xml(reply)
        return add_product_successful(reply)

    def add_credit(self, member_id, amountinpence):
        """ Add credit to a user account """
        packet = Packet("addcredit", {"memberid":member_id, "amountinpence":amountinpence})
        message = Message(packet).get_xml()

        reply, _recvd = self.send(message)
        reply = Message.parse_xml(reply)
        return add_credit_successful(reply)

    def find_server(self):
        """ Try TCP ports from 9999 to 11000 to find the server """
        server_port = 9999

        while (not self.found_server) and (server_port < 11000):
            server_port = server_port + 1
            self.server_address = (self.server_host, server_port)
            self.test_connection()

    def test_connection(self):
        """ Ping the server to test it's still there """
        
        ## Assume we are connected initially
        ## to let send method work
        self.found_server = True
        
        message = Message("ping")
        reply, received = self.send(message.get_xml())

        if received > 0:
            packets = Message.parse_xml(reply)

            if packets[0].type == 'pingreply':
                self.logger.info("Connected to remote server")
                self.found_server = True
            else:
                self.logger.info("Unexpected reply from remote server")
                self.found_server = False
        else:
            self.logger.info("No reply to ping received!")
            self.found_server = False

    def send(self, message):
        """ Sends message on current socket and waits for response """
        received = 0
        data = ''

        if self.found_server:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            signal.signal(signal.SIGALRM, self.timeout_handler)
            signal.alarm(10)

            try:
                self.sock.connect(self.server_address)

                self.logger.info("Sending %s" % message)

                length = len(message)
                message = "%5s%s" % (length, message)

                self.sock.sendall(message)
                try:
                    length = int(self.sock.recv(5))
                    data = self.sock.recv(length)
                except ValueError:
                    ## Nothing received or socket not initialised correctly
                    ## Wait until the timeout handler fires
                    while(1):
                        pass

                signal.alarm(0)
                received = len(data)

            except TimeoutException:
                received = 0
                data = ''

            except socket.error as err:
                self.logger.info("Socket open failed with '%s'" % err.strerror)
                signal.alarm(0)
                received = 0
                data = ''

            finally:
                self.sock.close()

        return data, received

    def timeout_handler(self, __signum, __frame):
        """ If no response is received before timeout, this is called """
        self.found_server = False
        raise TimeoutException

def parse_reply(message):
    """ Convert byte-level message into XML """
    dom = parseString(message)

    packets = dom.getElementsByTagName('packet')

    for packet in packets:
        packettype = packet.attributes.getNamedItem("type").value

        if packettype == "ping":
            return Message("pingreply")

def transactions_successful(reply):
    """ Parses reply for a successful set of transactions """
    success = True

    for packet in reply:
        if packet.type == "result" and packet.data['action'] == "transaction":
            success = success and (packet.data['result'] == "Success")

    return success

def add_credit_successful(reply):
    """ Parses reply for a successful addition of credit to user account """
    success = False
    reply = reply[0]

    if reply.type == "result" and reply.data['action'] == "addcredit":
        success = (reply.data['result'] == "Success")
    return success

def add_product_successful(reply):
    """ Parses reply for a successful addition of product to database """
    success = False
    reply = reply[0]

    if reply.type == "result" and reply.data['action'] == "addproduct":
        success = (reply.data['result'] == "Success")
    return success
