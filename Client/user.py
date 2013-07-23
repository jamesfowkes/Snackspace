""" 
user.py

Class representing a snackspace user
"""

class User:

    """ Definition of the user class """
    
    def __init__(self, member_id, username, balance, credit_limit, options): #pylint: disable=R0913
        """ Initialise the user object """
        self.name = username
        self.balance = int(balance)
        self.credit_limit = int(credit_limit)
        self.member_id = member_id
        self.limit_action = options.limit_action
        self.credit_action = options.credit_action

        ## Keep credit added recorded separately from balance.
        ## This way, balance will not be updated until payments have been processed,
        ## but the user can be prevented from adding too much credit (configuration dependent)
        self.credit = 0

    ## Transaction allowed return values
    XACTION_ALLOWED = 0
    XACTION_OVERLIMIT = 1
    XACTION_DENIED = 2

    def transaction_allowed(self, priceinpence):
        """ Determines if the user is allowed to debit their account by amount requested """
        over_limit = (self.balance - priceinpence < self.credit_limit)
        transaction_state = self.XACTION_ALLOWED

        if over_limit:
            if self.limit_action == 'warn':
                transaction_state = self.XACTION_OVERLIMIT
            elif self.limit_action == 'deny':
                transaction_state = self.XACTION_DENIED
            else:
                transaction_state = self.XACTION_DENIED

        return transaction_state

    def credit_allowed(self):
        """ Determines if user is allowed to credit their account """
        credit_allowed = False ## Assume that adding extra credit is not allowed

        if self.credit_action == 'always':
            credit_allowed = True
        elif self.credit_action == 'whenindebt':
            if (self.balance + self.credit) < 0:
                credit_allowed = True
            else:
                credit_allowed = False
        elif self.credit_action == 'disallow':
            credit_allowed = False

        return credit_allowed
    
    def has_added_credit(self):
        """ Returns true if the user has added some credit """
        return (self.credit > 0)
        
    def add_credit(self, amount):
        """ Increases amount of added credit """
        self.credit += int(amount)
