import logging

class SimpleStateMachine:
    
    class StateNotFoundException(Exception):
        pass
    
    class EventNotFoundException(Exception):
        pass
    
    class BadHandlerException(Exception):
        pass
    
    def __init__(self, startstate, entries):
        self.state = startstate
        self.entries = entries
        self.eventQueue = []
        self.executing = False
        self.logger = logging.getLogger("SimpleStateMachine")
        
    def onStateEvent(self, event):
        
        self.eventQueue.append(event)
        
        if not self.executing:
            self.handleEventQueue()
        
    def handleEventQueue(self):
        
        self.executing = True
        while len(self.eventQueue) > 0:
            
            event = self.eventQueue[0]
            self.eventQueue = self.eventQueue[1:]
            
            oldState = self.state
            
            # Find entries for this state
            entries = [entry for entry in self.entries if entry.state == self.state]
            
            if len(entries) == 0:
                raise self.StateNotFoundException("State %s not found" % self.state)
            
            # Find the handler for this event
            try:
                [handler] = [entry.handler for entry in entries if entry.event == event]
            except ValueError:
                raise self.EventNotFoundException("Event %s in state %s" % (event, self.state))
    
            self.state = handler()
                
            if self.state is None:
                raise self.BadHandlerException("Handler did not return next state")
            
            self.logger.info("Got event %s in state %s, new state %s" % (event, oldState, self.state))
            
        self.executing = False

class SimpleStateMachineEntry:
    def __init__(self, state, event, handler):
        self.state = state
        self.event = event
        self.handler = handler