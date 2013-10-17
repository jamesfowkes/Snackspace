""" dbclient.py

Implements low-level functionality to communicate with 
the database server
"""
 
import socket
import logging

from messaging import Message, Packet, PacketTypes, InputException

from xml.dom.minidom import parseString

import threading
import Queue

class BadReplyException(Exception):
    """ Exception raised when a message to the server does not receive the expected reply """
    pass

class TimeoutException(Exception):
    """ Exception raised when socket fails to receive response """
    pass

class MessagingQueueItem: #pylint: disable=R0903
    
    """ An item to be placed on the send queue for the database """
    
    def __init__(self, msg_type, message, queue):
        """ Init the message queue item """
        self.type = msg_type
        self.message = message
        self.queue = queue
    
class DbClient(threading.Thread):

    """ Implementation of DbClient class """
    def __init__(self, host_ip, task_handler, callback):

        """ Initialise the database client thread """
        
        threading.Thread.__init__(self)
        
        self.server_host = str(host_ip)
        self.callbacks = []
        self.send_queue = Queue.Queue()
        
        self.sock = None
        
        self.found_server = False
        self.state_callback = callback
        self.test_port = 10000
        self.first_update = True
        
        self.stopReq = threading.Event()
        self.stopped = False
        
        self.server_address = ()
        
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger("DBClient")
        
        self.task_handler = task_handler
        self.test_connection_task = self.task_handler.add_function(self.test_connection, 2000, True)
        
    def run(self):
        
        self.reset_and_begin_search()
        
        while (not self.stopReq.isSet()):
            
            try:
                item = self.send_queue.get(False)
                self.process_item(item)
                
            except Queue.Empty:
                pass
    
        self.stopped = True
        
    def stop(self):
        self.stopReq.set()
        
    def process_item(self, item):
    
        reply, recvd = self.send(item.message)
            
        if recvd > 0:
            try:
                packets = Message.parse_xml(reply)
            
                for packet in packets:
                   
                    if packet.type in (PacketTypes.UserData, PacketTypes.UnknownUser):
                        item.queue.put(packet)
                    elif packet.type == PacketTypes.PingReply:
                        self.got_ping_reply(packet, recvd)
                    elif packet.type in (PacketTypes.ProductData, PacketTypes.UnknownProduct):
                        item.queue.put(packet)
                    elif packet.type == PacketTypes.Result:
                        if packet.data['action'] == PacketTypes.Transaction:
                            item.queue.put(packet)
                        if packet.data['action'] == PacketTypes.AddProduct:
                            item.queue.put(packet)
                        if packet.data['action'] == PacketTypes.AddCredit:
                            item.queue.put(packet)

            except InputException:
                pass ## Let the ping task deal with finding the server has gone
        else:
            if (item.type == PacketTypes.Ping):
                self.got_ping_reply(None, 0)
                                    
    def test_connection(self):
        """ Periodic task to ping the server and check it's still there """
        if self.found_server == False:
            # The server hasn't been found yet, so keep testing
            self.server_address = (self.server_host, self.test_port)
            self.ping_server()
        else:
            # There should still be a server there, so ping it
            self.ping_server()

                    
    def reset_and_begin_search(self):
        """ Resets local server information and begins searching for it again """
        self.found_server = False
        self.test_port = 10000
        self.test_connection_task.set_period(2000)
        self.test_connection_task.trigger_now()

    def get_product(self, barcode, queue):
        """ Get the product data associated with the barcode """
        packet = Packet(PacketTypes.GetProduct, {"barcode":barcode})
        message = Message(packet).get_xml()
    
        self.send_queue.put( MessagingQueueItem(PacketTypes.GetProduct, message, queue))
        
    def get_user_data(self, rfid, queue):
        """ Get the user data associated with the rfid """
        packet = Packet(PacketTypes.GetUser, {"rfid":rfid})
        message = Message(packet).get_xml()

        self.send_queue.put( MessagingQueueItem(PacketTypes.GetUser, message, queue) )

        
    def send_transactions(self, productdata, member_id, queue):
        """ Send transaction requests to the server """
        self.logger.info("Sending transactions")

        message = Message()

        for (barcode, count) in productdata:
            packet = Packet(PacketTypes.Transaction, {"barcode":barcode, "memberid":member_id, "count":count})
            message.add_packet(packet)

        self.send_queue.put( MessagingQueueItem(PacketTypes.Transaction, message.get_xml(), queue) )

    def add_product(self, barcode, description, price_in_pence, queue):
        """ Add a new product to the database """
        packet = Packet(PacketTypes.AddProduct, {"barcode":barcode, "description":description, "price_in_pence":price_in_pence})
        message = Message(packet).get_xml()

        self.send_queue.put( MessagingQueueItem(PacketTypes.AddProduct, message, queue))
        
    def add_credit(self, member_id, amountinpence, queue):
        """ Add credit to a user account """
        packet = Packet(PacketTypes.AddCredit, {"memberid":member_id, "amountinpence":amountinpence})
        message = Message(packet).get_xml()

        self.send_queue.put( MessagingQueueItem(PacketTypes.AddCredit, message, queue))
        
    def get_random_product(self, callback):
        """ Pull the data for a random product - useful for testing """
        packet = Packet(PacketTypes.RandomProduct, {})
        message = Message(packet).get_xml()
        
        reply, _recvd = self.send(message)
        reply = Message.parse_xml(reply)
        reply = reply[0]
        
        data = None
        
        if reply.type == "productdata":
            barcode = reply.data['barcode']
            desc = reply.data['description']
            priceinpence = reply.data['priceinpence']
            data = (barcode, desc, priceinpence)
        else:
            raise BadReplyException
    
        callback(data)
        
    def ping_server(self):
        """ Ping the server to test it's still there """    
        self.logger.info("Testing connection on %s port %d" % self.server_address)
        
        message = Message(PacketTypes.Ping).get_xml()
        
        self.send_queue.put( MessagingQueueItem(PacketTypes.Ping, message, None ))
    
    def got_ping_reply(self, reply, received):
        
        old_connection_state = self.found_server
        
        if received > 0:
            if reply.type == PacketTypes.PingReply:
                self.logger.info("Connected to remote server")
                self.found_server = True
            else:
                self.logger.info("Unexpected reply from remote server")
                self.found_server = False
        else:
            self.logger.info("No reply to ping received!")
            self.found_server = False
        
        if not old_connection_state:
            if not self.found_server:
                #Keep looking for the server
                self.test_port = (self.test_port + 1) if (self.test_port < 10010) else 10000
            else:
                #Found the server, reduce ping rate
                self.test_connection_task.set_period(10000)
        else:
            if not self.found_server:
                # Lost the current server, so start search again
                self.reset_and_begin_search()
                
        self.state_callback(old_connection_state, self.found_server, self.first_update)
        self.first_update = False
        
    def send(self, message):
        """ Sends message on current socket and waits for response """
        received = 0
        data = ''

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.test_connection_task.active = False
        
        try:
            self.sock.connect(self.server_address)

            self.logger.info("Sending %s" % message)

            length = len(message)
            message = "%5s%s" % (length, message)

            self.sock.settimeout(5)
            self.sock.sendall(message)
            try:
                length = int(self.sock.recv(5))
                data = self.sock.recv(length)
            except ValueError:
                pass
            
            received = len(data)

        except socket.timeout:
            received = 0
            data = ''
        except socket.error as err:
            self.logger.info("Socket open failed with '%s'" % err.strerror)
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

        if packettype == PacketTypes.Ping:
            return Message(PacketTypes.PingReply)

