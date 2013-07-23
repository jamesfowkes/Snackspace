'''
SimpleStateMachine.py

Implements a basic state machine.

States are defined as integers.
Each state can have events associated with it.
Each state-event pair has a function handler that returns the next state.

'''

import logging
from collections import namedtuple

class SimpleStateMachine:

    """ Implementation of the state machine """
      
    class StateNotFoundException(Exception):
        """Exception to be issued when a state cannot be found"""
        pass

    class EventNotFoundException(Exception):
        """Exception to be issued when an event cannot be found"""
        pass

    class BadHandlerException(Exception):
        """Exception to be issued when a handler does not return a new state """
        pass

    def __init__(self, startstate, entries):
        self.state = startstate
    
        #Make each entry a named tuple. This aids in writing the event handler.
        SimpleStateMachineEntry = namedtuple('Entry', ['state', 'event', 'handler']) #pylint: disable=C0103    
        self.entries = [SimpleStateMachineEntry(entry[0], entry[1], entry[2]) for entry in entries]
        
        self.event_queue = []
        self.executing = False
        self.logger = logging.getLogger("SimpleStateMachine")

    def on_state_event(self, event):
        """ Queues an event for execution """
        self.event_queue.append(event)

        if not self.executing:
            self.handle_event_queue()

    def handle_event_queue(self):
        """ Handles transition from state->state based on event and handler function """ 
        self.executing = True
        while len(self.event_queue) > 0:

            event = self.event_queue[0]
            self.event_queue = self.event_queue[1:]

            old_state = self.state

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

            self.logger.info("Got event %s in state %s, new state %s" % (event, old_state, self.state))

        self.executing = False
