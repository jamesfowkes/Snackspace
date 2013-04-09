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

class InputException(Exception): 
	pass 

class Packet:
	
	def __init__(self, packettype, data_dict = None):
		self.Type = packettype
		self.Data = data_dict
	
	def addToDOM(self, dom):

		## Create a new packet DOM element at the root of the DOM
		## with the specified packet type and return the packet DOM node
		packet_element = dom.createElement('packet')
		packet_element.setAttribute('type', self.Type)
		
		
		try:
			for datatype, data in self.Data.iteritems():
		
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
	def fromDOMPacketElement(cls, ele):
			
		packettype = ele.attributes.getNamedItem("type").value
		data_dict = {}
			
		for node in ele.childNodes:
			data_dict[node.localName] = node.firstChild.nodeValue
			
		return cls(packettype, data_dict)
		
class Message:

	def __init__(self, packet = None, debugme = False):
		self.debugme = debugme
		self.Clear()
		self.__packets = []
		
		if isinstance(packet, list):
			self.__packets = packet
		elif isinstance(packet, Packet):
			self.__packets = [packet]
		elif isinstance(packet, str):
			self.__packets = [Packet(packet)]
		
	def AddPacket(self, packet):
		self.__packets.append(packet)
			
	def GetXML(self):
		self.__buildXML()
		return self.doc.toxml()
			
	def __buildXML(self):
		impl = getDOMImplementation()
		self.doc = impl.createDocument(None, "xml", None)
		
		## Let each packet add itself to the DOM tree
		for packet in self.__packets:
			packet.addToDOM(self.doc)
			
	def Clear(self):
		self.__packets = {}
		self.doc = None
			
	@staticmethod
	def ParseXML(xml, debugme = False):
		
		packetlist = []
		
		if len(xml):
			try:
				if debugme:
					print "Parsing %s" % xml
				
				dom = parseString(xml)
				packets = dom.getElementsByTagName('packet')
				
				for packet in packets:
					packetlist.append( Packet.fromDOMPacketElement(packet) )

			except:
				raise
		else:
			raise InputException

		return packetlist