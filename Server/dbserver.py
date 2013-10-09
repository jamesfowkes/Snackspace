"""
dbase.py

Server-side message and packet handling layer

"""

from messaging import Message, Packet, PacketTypes

import logging

from db import Database

class DbServer(Database):
    """ Implementation of database server class """
    def __init__(self, use_test_db):

        Database.__init__(self, use_test_db)
                
        self.packets = []
        
        logging.basicConfig(level=logging.DEBUG)
        
        self.logger = logging.getLogger("LocalDB")
            
    def process_packets(self, packets):
        """ Process a list of packets """
        
        reply = Message() ## The reply starts as an empty message

        for packet in packets:

            self.logger.info("Handling '%s' packet..." % packet.type)

            if packet.type == PacketTypes.Ping:
                reply.add_packet( Packet(PacketTypes.PingReply) )
            elif packet.type == PacketTypes.GetProduct:
                reply.add_packet( self.get_product_from_data(packet.data) )
            elif packet.type == PacketTypes.GetUser:
                reply.add_packet( self.get_user_from_data(packet.data) )
            elif packet.type == PacketTypes.Transaction:
                reply.add_packet( self.apply_transaction_from_data(packet.data) )
            elif packet.type == PacketTypes.AddProduct:
                reply.add_packet ( self.add_product_from_data(packet.data) )
            elif packet.type == PacketTypes.AddCredit:
                reply.add_packet( self.add_credit_from_data(packet.data) )
            elif packet.type == PacketTypes.RandomProduct:
                reply.add_packet( self.get_random_product_packet() )
            elif packet.type == PacketTypes.PingReply:
                pass # No action required for ping reply
            else:
                self.logger.warning("Unknown packet '%s'" % packet.type)

        return reply.get_xml()
       
    def get_random_product_packet(self):
        """ Get a random product and make packet """
        result = self.get_random_product()
        
        datatype = PacketTypes.ProductData
        data =  {'barcode': '0', 'description': '', 'priceinpence':'0'} 
        data['barcode'] = result['barcode']
        data['description'] = result['shortdesc']
        data['priceinpence'] = result['price']
            
        packet = Packet(datatype, data)

        return packet
    
    def get_product_from_data(self, data):
        """ Get a product packet """
        barcode = data['barcode']

        self.logger.info("Getting product %s" % barcode)

        return self.product_from_barcode(barcode)

    def get_user_from_data(self, data):
        """ Get a user packet """
        rfid = data['rfid']

        self.logger.info("Getting user %s" % rfid)

        return self.user_from_rfid(rfid)

    def add_product_from_data(self, data):
        """ Add a product to the database """
        _barcode = data['barcode']
        _desc = data['description']
        _priceinpence = data['price_in_pence']

        self.logger.info("Adding new product %s" % _barcode)

        result = self.add_product(_barcode, _desc, _priceinpence)

        packet = Packet(PacketTypes.Result, {"action":PacketTypes.AddProduct, "barcode":_barcode, "description": _desc, "result": "Success" if result else "Fail"})

        return packet

    def add_credit_from_data(self, data):
        """ Add credit to a user """
        memberid = data['memberid']
        amountinpence = int(data['amountinpence'])

        self.logger.info("Adding %s credit to member %s" % (amountinpence, memberid))

        result = self.add_credit(memberid, amountinpence)

        packet = Packet(PacketTypes.Result, {"action":PacketTypes.AddCredit, "credit": amountinpence, "result": "Success" if result else "Fail", "memberid":memberid})

        return packet

    def apply_transaction_from_data(self, data):
        """ Add transaction to the database """
        memberid = data['memberid']
        barcode = data['barcode']
        count = int(data['count'])

        result, total = self.transaction(memberid, barcode, count)

        packet = Packet(PacketTypes.Result, {"action":PacketTypes.Transaction, "barcode":barcode, "total":total, "result": "Success" if result else "Fail", "memberid":memberid})

        return packet

    def product_from_barcode(self, barcode):
        """ Build a product packet from the database """
        result = self.get_product(barcode)

        if result is not None:
            datatype = PacketTypes.ProductData
            data =  {'barcode': '0', 'description': '', 'priceinpence':'0'} 
            data['barcode'] = result['barcode']
            data['description'] = result['shortdesc']
            data['priceinpence'] = result['price']
        else:
            datatype = PacketTypes.UnknownProduct
            data =  {'barcode': '0'} 
            data['barcode'] = barcode
            
        packet = Packet(datatype, data)

        return packet


    def user_from_rfid(self, rfid):
        """ Build a user packet from the database """
        datatype = PacketTypes.UserData
        data =  {'memberid': '0', 'username': '', 'balance':'0', 'limit':'0', 'rfid':rfid}

        result = self.get_user(rfid)

        if result is not None:
            data['rfid'] = result['rfid']
            data['memberid'] = result['memberid']
            data['username'] = result['username']
            data['balance'] = result['balance']
            data['limit'] = result['limit']
        else:
            datatype = PacketTypes.UnknownUser

        packet = Packet(datatype, data)

        return packet
