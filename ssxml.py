'''
ssxml.py

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

class SSMessage:

	def __init__(self, action = None, data = None, debugme = False):
		self.debugme = debugme
		self.Clear()
		self.__actions = {}
		
		if action is not None:
			self.__actions[action] = None
			if data is not None:
				if isinstance(data, dict):
					self.__actions[action] = [data.copy()]
				elif isinstance(data, list):
					self.__actions[action] = list(data)
		
	def AddAction(self, action, data_dict):
		try:
			self.__actions[action].append(data_dict.copy())
		except KeyError:
			self.__actions[action] = [data_dict.copy()]
	
	def GetXML(self):
		self.__buildXML()
		return self.doc.toxml()
			
	def __buildXML(self):
		impl = getDOMImplementation()
		self.doc = impl.createDocument(None, "xml", None)
		
		for action, data_dict in self.__actions.items():
			
			action_element = self.addActionToDOM(self.doc, action)
			self.addActionDataToDOM(action_element, data_dict)
			
			self.doc.childNodes[0].appendChild(action_element)
	
	def Clear(self):
		self.__actions = {}
		self.doc = None
		
		
	def addActionToDOM(self, dom, actiontype):

		## Create a new action DOM element at the root of the DOM
		## with the specified action type and return the action DOM node
		action_element = dom.createElement('action')
		action_element.setAttribute('type', actiontype)
		
		return action_element
	
	def addActionDataToDOM(self, action_node, datalist):

		## datalist is expected to be a list of dictionaries (key-value pairs)
		## e.g. [ {'barcode':12345}, {'barcode':67890} ]
	
		try:
			for datapoint in datalist:
				for datatype, data in datapoint.iteritems():
			
					## Add these dictionary items to the DOM node.
					## For example, a {'barcode':12345} dictionary entry
					## becomes <barcode>12345</barcode>
					data_element = self.doc.createElement(datatype)
					text_node = self.doc.createTextNode(str(data))
					data_element.appendChild(text_node)
					action_node.appendChild(data_element)
		except TypeError:
			pass #datalist might be None - this is fine
			
	@staticmethod
	def ParseXML(xml, debugme = False):
		if len(xml):
			try:
				if debugme:
					print "Parsing %s" % xml
				
				actiondict = {}
				
				dom = parseString(xml)
				actions = dom.getElementsByTagName('action')
				
				for action in actions:
					actiontype = action.attributes.getNamedItem("type").value
					actiondict[actiontype] = {}
					
					for node in action.childNodes:
						actiondict[actiontype][node.localName] = node.firstChild.nodeValue
							
				return actiondict
			except:
				raise
		else:
			raise InputException
