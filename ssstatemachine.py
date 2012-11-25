from fysom import Fysom

def SSStateMachine(callbacks):

	self.fsm = Fysom({
	'initial' : 'intro',
	'events' : [
		{'src':'intro',		'name':'swipe',		'dst':'qryuser'},
		{'src':'intro',		'name':'scan',		'dst':'qryitem'},
		 
		{'src':'main',		'name':'swipe',		'dst':'qryuser'},
		{'src':'main',		'name':'scan',		'dst':'qryitem'},
		 
		{'src':'qryitem',	'name':'gotitem',	'dst':'main'},
		{'src':'qryuser',	'name':'gotuser',	'dst':'main'},
		 
		{'src':'main',		'name':'done',		'dst':'updating'},
		{'src':'main',		'name':'cancel',	'dst':'intro'},
		{'src':'main',		'name':'pay',		'dst':'paying'},
		
		{'src':'paying',	'name':'gotvalue',	'dst':'main'},
		
		{'src':'updating',	'name':'updated',	'dst':'intro'},
		
		],
	 'callbacks': callbacks
	})

def GUIEvent(self, screen, eventid):
	pass
