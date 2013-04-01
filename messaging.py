'''
messaging.py

Creates or decodes XML for communicating between
client and server

The structure of the XML to be transferred is:
<xml>
	<action type="actiontype">
		<datatype>data</datatype>
	</action>
	<action type="actiontype">
		<datatype>data</datatype>
	</action>
	...
</xml>

Where actiontype is the action to carry out ("transaction", "getuser", "ping etc.)
and datatype is the context of the data enclosed, e.g <barcode>12345</barcode>

This file is responsible for pushing data to/from Python data structures and XML
DOM objects.

'''

from xml.dom.minidom import parseString
from xml.dom.minidom import getDOMImplementation

class InputException(Exception): 
	pass 

class Packet:
	
	def __init__(self, action, data_dict = None):
		self.Action = action
		self.Data = data_dict
	
	def addToDOM(self, dom):

		## Create a new action DOM element at the root of the DOM
		## with the specified action type and return the action DOM node
		action_element = dom.createElement('action')
		action_element.setAttribute('type', self.Action)
		
		
		try:
			for datatype, data in self.Data.iteritems():
		
				## Add these dictionary items to the DOM node.
				## For example, a {'barcode':12345} dictionary entry
				## becomes <barcode>12345</barcode>
				data_element = dom.createElement(datatype)
				text_node = dom.createTextNode(str(data))
				data_element.appendChild(text_node)
				action_element.appendChild(data_element)
		except AttributeError:
			pass #data might be None - this is fine
		
		dom.childNodes[0].appendChild(action_element)
	
	@classmethod
	def fromDOMActionElement(cls, ele):
			
		actiontype = ele.attributes.getNamedItem("type").value
		data_dict = {}
			
		for node in ele.childNodes:
			data_dict[node.localName] = node.firstChild.nodeValue
			
		return cls(actiontype, data_dict)
		
class Message:

	def __init__(self, action = None, debugme = False):
		self.debugme = debugme
		self.Clear()
		self.__actions = []
		
		if isinstance(action, list):
			self.__actions = action
		elif isinstance(action, Packet):
			self.__actions = [action]
		elif isinstance(action, str):
			self.__actions = [Packet(action)]
		
	def AddAction(self, action):
		self.__actions.append(action)
			
	def GetXML(self):
		self.__buildXML()
		return self.doc.toxml()
			
	def __buildXML(self):
		impl = getDOMImplementation()
		self.doc = impl.createDocument(None, "xml", None)
		
		## data_list is list of dictionaries representing each
		## instance of the action
		for action in self.__actions:
			action.addToDOM(self.doc)
			
	def Clear(self):
		self.__actions = {}
		self.doc = None
			
	@staticmethod
	def ParseXML(xml, debugme = False):
		
		actionlist = []
		
		if len(xml):
			try:
				if debugme:
					print "Parsing %s" % xml
				
				dom = parseString(xml)
				actions = dom.getElementsByTagName('action')
				
				for action in actions:
					actionlist.append( Packet.fromDOMActionElement(action) )

			except:
				raise
		else:
			raise InputException

		return actionlist