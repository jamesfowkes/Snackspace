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
    def __init__(self, local, task_handler, callback):

        """ Add a new product to the database """
        self.local = local
        self.sock = None
        
        self.found_server = False
        self.state_callback = callback
        self.test_port = 10000
        self.first_update = True
        
        if self.local:
            self.server_host = 'localhost'
        else:
            self.server_host = ''

        self.server_address = ()
        
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger("DBClient")
        
        self.task_handler = task_handler
        self.test_connection_task = self.task_handler.add_function(self.test_connection, 2000, True)
        
        self.reset_and_begin_search()
        
    def test_connection(self):
        """ Periodic task to ping the server and check it's still there """
        if self.found_server == False:
            # The server hasn't been found yet, so keep testing
            self.server_address = (self.server_host, self.test_port)
            self.ping_server()
            
            if not self.found_server:
                self.test_port = (self.test_port + 1) if (self.test_port < 10010) else 10000
            else:
                self.test_connection_task.set_period(10000)
        else:
            # There should still be a server there, so ping it
            self.ping_server()
            if not self.found_server:
                self.reset_and_begin_search()
                    
    def reset_and_begin_search(self):
        """ Resets local server information and begins searching for it again """
        self.found_server = False
        self.test_port = 10000
        self.test_connection_task.set_period(2000)
        self.test_connection_task.trigger_now()

    def get_product(self, barcode, callback):
        """ Get the product data associated with the barcode """
        packet = Packet("getproduct", {"barcode":barcode})
        message = Message(packet).get_xml()

        data = None
        
        reply, _recvd = self.send(message)
        reply = Message.parse_xml(reply)
        reply = reply[0]

        if reply.type == "productdata":
            desc = reply.data['description']
            priceinpence = reply.data['priceinpence']
            data = (barcode, desc, priceinpence)
        elif reply.type == 'unknownproduct':
            data = None
        else:
            raise BadReplyException

        callback(barcode, data)
        
    def get_user_data(self, rfid, callback):
        """ Get the user data associated with the rfid """
        packet = Packet("getuser", {"rfid":rfid})
        message = Message(packet).get_xml()

        reply, _recvd = self.send(message)
        reply = Message.parse_xml(reply)
        reply = reply[0]

        data = None
        
        if reply.type == "userdata":
            rfid = reply.data['rfid']
            username = reply.data['username']
            balance = reply.data['balance']
            limit = reply.data['limit']
            member_id = reply.data['memberid']
            self.logger.info("Got user %s" % username)
            data = (member_id, username, balance, limit)
        else:
            self.logger.info("Unrecognised rfid %s" % rfid)

        callback(rfid, data)
        
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

    def add_product(self, barcode, description, price_in_pence, callback):
        """ Add a new product to the database """
        packet = Packet("addproduct", {"barcode":barcode, "description":description, "price_in_pence":price_in_pence})
        message = Message(packet).get_xml()

        reply, _recvd = self.send(message)
        reply = Message.parse_xml(reply)
        
        packet = reply[0]
        
        callback(packet.data['barcode'], packet.data['description'], add_product_successful(reply))
        
    def add_credit(self, member_id, amountinpence):
        """ Add credit to a user account """
        packet = Packet("addcredit", {"memberid":member_id, "amountinpence":amountinpence})
        message = Message(packet).get_xml()

        reply, _recvd = self.send(message)
        reply = Message.parse_xml(reply)
        return add_credit_successful(reply)

    def get_random_product(self):
        """ Pull the data for a random product - useful for testing """
        packet = Packet("randomproduct", {})
        message = Message(packet).get_xml()
        
        reply, _recvd = self.send(message)
        reply = Message.parse_xml(reply)
        reply = reply[0]
        
        if reply.type == "productdata":
            barcode = reply.data['barcode']
            desc = reply.data['description']
            priceinpence = reply.data['priceinpence']
            return (barcode, desc, priceinpence)
        else:
            raise BadReplyException
    
    def ping_server(self):
        """ Ping the server to test it's still there """
        
        ## Assume we are connected initially
        ## to let send method work
        old_connection_state = self.found_server 
        self.found_server = True
        
        self.logger.info("Testing connection on %s port %d" % self.server_address)
        
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
        
        self.state_callback(old_connection_state, self.found_server, self.first_update)
        self.first_update = False
        
    def send(self, message):
        """ Sends message on current socket and waits for response """
        received = 0
        data = ''

        if self.found_server:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            self.test_connection_task.active = False
            
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
                self.test_connection_task.active = True

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
