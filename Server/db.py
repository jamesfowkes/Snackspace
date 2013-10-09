"""
dbase.py

Server-side database connection layer
"""

import os
import sqlsoup #@UnresolvedImport
import sqlalchemy
import urllib
import re
from sqlsoup import Session

import random

TEST_DB_PATH = "Server/data/test.dbase"
TEST_DATA_PATH = "Server/data/test_data.sql"

REAL_DB_PATH = "snackspace:%s@rommie/instrumentation"

ONLINE_SQL_URL = 'https://nottinghack-instrumentation.googlecode.com/svn/db/'

#List of TABLES that the Snackspace application needs
TABLES = ['rfid_tags', 'members', 'transaction', 'products']

def get_password():
    """
    This system is not particularly secure.
    The database password is stored in plaintext
    in a file (".sspwd") that should be in the same directory
    as this file.
    The password only grants MySQL access to the 'snackspace'
    MySQL user, so access is restricted to CRU anyway.
    Any further security improvements are left as an exercise for the reader.
    """

    try:
        pwd = open(".sspwd")
        pwd = pwd.readline()
    except IOError:
        return False

    return pwd

class Database:
    """ Implementation of Database class """
    def __init__(self, use_test_db):

        if use_test_db:

            self.dbase = sqlsoup.SQLSoup("sqlite:///%s" % TEST_DB_PATH)

            if not os.path.exists(TEST_DB_PATH):
                self.create_test_db()

        else:
            real_db_path = REAL_DB_PATH % get_password()

            self.dbase = sqlsoup.SQLSoup("mysql://%s" % real_db_path)

    random.seed()
    
    def get_user(self, rfid):
        """ Query database for user based on rfid """
        result = {}

        try:
            labelled_rfid = self.dbase.with_labels(self.dbase.rfid_tags)
            labelled_members = self.dbase.with_labels(self.dbase.members)
            user_data = self.dbase.join(labelled_rfid, labelled_members, labelled_members.members_member_id== labelled_rfid.rfid_tags_member_id)
            user_data = user_data.filter(labelled_rfid.rfid_tags_rfid_serial==rfid).one()

            result['rfid'] = user_data.rfid_tags_rfid_serial
            result['username'] = user_data.members_name
            result['balance'] = user_data.members_balance
            result['limit'] = user_data.members_credit_limit
            result['memberid'] = user_data.members_member_id

        except SQLError:
            result = None

        return result

    def get_random_product(self):
        """ Get a random product """
        result = {}
        product_count = self.dbase.products.count() - 1

        session = Session()
        random_index = random.randint(0, product_count)
        
        product_data = session.query(self.dbase.products)[random_index]
        result['barcode'] = product_data.barcode
        result['shortdesc'] = product_data.shortdesc
        result['price'] = product_data.price
        
        return result
        
    def get_product(self, barcode):
        """ Query database for product based on barcode """
        result = {}

        try:
            product_data = self.dbase.products.filter(self.dbase.products.barcode==barcode).one()
            result['barcode'] = product_data.barcode
            result['shortdesc'] = product_data.shortdesc
            result['price'] = product_data.price

        except (SQLError, sqlalchemy.orm.exc.NoResultFound):
            result = None

        return result

    def transaction(self, memberid, barcode, count):
        """ Update member records based on purchased product """
        product_data = self.dbase.products.filter(self.dbase.products.barcode==barcode).one()
        member_data = self.dbase.members.filter(self.dbase.members.member_id==memberid).one()

        try:
            for __count in range(0, count):
                self.dbase.transactions.insert(
                                                                member_id = memberid,
                                                                amount = -product_data.price,
                                                                transaction_type = "SNACKSPACE",
                                                                transaction_status = "COMPLETE",
                                                                transaction_desc = product_data.shortdesc,
                                                                product_id = product_data.product_id)

                member_data.balance -= product_data.price

            self.dbase.commit()

            result = True, product_data.price * count

        except SQLError:
            result = False, 0

        return result

    def add_credit(self, memberid, amountinpence):
        """ Update member record with additional credit """
        member_data = self.dbase.members.filter(self.dbase.members.member_id==memberid).one()

        try:
            member_data.balance += amountinpence
            self.dbase.commit()
            result = True

        except SQLError:
            result = False

        return result

    def add_product(self, _barcode, _description, _priceinpence):
        """ Add a new product to the database """
        try:
            self.dbase.products.insert(barcode = _barcode, shortdesc = _description, price = _priceinpence)
            self.dbase.commit()
            result = True

        except SQLError:
            result = False

        return result

    def create_test_db(self):

        """
        Takes MySQL create table queries and botches them to work with SQLite
        """

        for table in TABLES:
            filename = "tb_%s.sql" % table
            localpath = "data/%s" % filename
            if not os.path.exists(localpath):
                urllib.urlretrieve(ONLINE_SQL_URL + filename, localpath)

            sql = open(localpath).readlines()
            new_sql = []

            if table == 'transaction':
                table = 'transactions' ## Special case, filename != table name

            drop_sql = "drop table if exists %s;" % table

            has_primary_key = False
            primary_keys = None

            for line in sql:

                ## Remove the "drop table" line
                line = line.replace(drop_sql, '')

                #Remove any engine specifier
                line = re.sub(r'ENGINE = \w*', '', line)

                ## Remove any "primary key" lines, but save for later
                if 'primary key' in line:
                    primary_keys = line
                    line = ""

                ## Replace MySQL auto_increment with PRIMARY KEY AUTOINCREMENT for SQLite
                if 'auto_increment' in line:
                    line = line.replace('auto_increment', 'INTEGER PRIMARY KEY AUTOINCREMENT')
                    line = line.replace('int', '')
                    line = line.replace('not null', '')
                    line = line.replace('NOT NULL', '')
                    has_primary_key = True

                new_sql.append(line)

            ## If we didn't find an auto-increment integer key,make sure the original key is created
            if not has_primary_key and primary_keys is not None:
                new_sql.insert(-1, primary_keys)

            new_sql = "".join(new_sql)

            #The last statement shouldn't have a comma after it
            #which is same as not having a closing paren following a comma
            new_sql = re.sub(r",\s*\)", ")", new_sql)

            # Execute the drop table line, then the create statement
            self.dbase.execute(drop_sql)
            self.dbase.commit()


            self.dbase.execute(new_sql)
            self.dbase.commit()

        # Insert test data
        sql = open(TEST_DATA_PATH).readlines()
        for line in sql:
            self.dbase.execute(line)
        self.dbase.commit()
