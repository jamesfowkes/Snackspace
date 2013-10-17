'''
messaging.py

Creates or decodes XML for communicating between
client and server

The structure of the XML to be transferred is:
<xml>
        <packet type="packettype">
                <datatype>data</datatype>
        </packet>
        <packet type="packettype">
                <datatype>data</datatype>
        </packet>
        ...
</xml>

Where packettype is the context of the packet data("transaction", "getuser", "ping" etc.)
and datatype is the context of the individual data items enclosed, e.g <barcode>12345</barcode>

This file is responsible for pushing data to/from Python data structures and XML
DOM objects.

'''

from xml.dom.minidom import parseString
from xml.dom.minidom import getDOMImplementation

from const import Const

## Constants defining packet types

PacketTypes = Const()
PacketTypes.Ping = "ping"
PacketTypes.PingReply = "pingreply"
PacketTypes.GetRandomProduct = "randomproduct"
PacketTypes.AddCredit = "addcredit"
PacketTypes.AddProduct = "addproduct"
PacketTypes.Transaction = "transaction"
PacketTypes.GetUser = "getuser"
PacketTypes.GetProduct = "getproduct"
PacketTypes.ProductData = "productdata"
PacketTypes.UserData = "userdata"
PacketTypes.UnknownProduct = "unknownproduct"
PacketTypes.UnknownUser = "unknownuser"
PacketTypes.RandomProduct = "randomproduct"
PacketTypes.Result = "result"

class InputException(Exception):
    """ To be raised when a packet could not be created due to bad input """
    pass

class Packet:
    """ Implements a single command, data or request for passing 
    between client and server"""
    def __init__(self, packettype, data_dict = None):
        self.type = packettype
        self.data = data_dict
        self.doc = None
        
    def add_to_dom(self, dom):

        """ Create a new packet DOM element at the root of the DOM
        with the specified packet type and return the packet DOM node """
        
        packet_element = dom.createElement('packet')
        packet_element.setAttribute('type', self.type)

        try:
            for datatype, data in self.data.iteritems():

                ## Add these dictionary items to the DOM node.
                ## For example, a {'barcode':12345} dictionary entry
                ## becomes <barcode>12345</barcode>
                data_element = dom.createElement(datatype)
                text_node = dom.createTextNode(str(data))
                data_element.appendChild(text_node)
                packet_element.appendChild(data_element)
        except AttributeError:
            pass #data might be None - this is fine

        dom.childNodes[0].appendChild(packet_element)

    @classmethod
    def from_dom_packet_element(cls, ele):
        """ Creates Packet object from an XML packet """
        packet_type = ele.attributes.getNamedItem("type").value
        data_dict = {}

        for node in ele.childNodes:
            try:
                data_dict[node.localName] = node.firstChild.nodeValue
            except AttributeError:
                pass

        return cls(packet_type, data_dict)

class Message:
    """ Implements a collection of packets as an XML document """
    def __init__(self, packet = None, debugme = False):
        self.debugme = debugme
        self.doc = None
        self.clear()
        self.packets = []

        if isinstance(packet, list):
            self.packets = packet
        elif isinstance(packet, Packet):
            self.packets = [packet]
        elif isinstance(packet, str):
            self.packets = [Packet(packet)]

    def add_packet(self, packet):
        """ Adds a new packet to the message """
        self.packets.append(packet)

    def get_xml(self):
        """ Returns an XML representation of the message """
        self.build_xml()
        return self.doc.toxml()

    def build_xml(self):
        """ Builds an XML representation of the message """
        impl = getDOMImplementation()
        self.doc = impl.createDocument(None, "xml", None)

        ## Let each packet add itself to the DOM tree
        for packet in self.packets:
            packet.add_to_dom(self.doc)

    def clear(self):
        """ Delete all packets and associated XML """
        self.packets = {}
        self.doc = None

    @staticmethod
    def parse_xml(xml):
        """ Parses an XML tree for packets and returns a list Packet objects """
        packetlist = []

        if len(xml):
            try:
                dom = parseString(xml)
                packets = dom.getElementsByTagName('packet')

                for packet in packets:
                    packetlist.append( Packet.from_dom_packet_element(packet) )

            except:
                raise
        else:
            raise InputException

        return packetlist
