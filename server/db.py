import os
import sqlsoup #@UnresolvedImport
import urllib
import re

testDbPath = "server/data/test.db"
testDataPath = "server/data/test_data.sql"

onlineSqlUrl = 'https://nottinghack-instrumentation.googlecode.com/svn/db/'

#List of tables that the Snackspace application needs
tables = ['members', 'rfid_tags', 'transaction', 'products']

class db:
	
	def __init__(self, useTestDb):
		
		if useTestDb:
			self.db = sqlsoup.SQLSoup("sqlite:///%s" % testDbPath)
			
			if not os.path.exists(testDbPath):
				self.__createTestDb()
					
		else:
			#TODO: Implement access to MySQL DB on Holly
			pass
	
	def GetUser(self, rfid):
		
		result = {}
		
		try:
			labelled_rfid = self.db.with_labels(self.db.rfid_tags)
			labelled_members = self.db.with_labels(self.db.members)
			user_data = self.db.join(labelled_rfid, labelled_members, labelled_members.members_member_id== labelled_rfid.rfid_tags_member_id)
			user_data = user_data.filter(labelled_rfid.rfid_tags_rfid_serial==rfid).one()
		
			result['rfid'] = user_data.rfid_tags_rfid_serial
			result['username'] = user_data.members_name
			result['balance'] = user_data.members_balance
			result['limit'] = user_data.members_credit_limit
			result['memberid'] = user_data.members_member_id
			
		except:
			result = None
		
		return result
	
	def GetIProduct(self, barcode):
		
		result = {}
		
		try:
			product_data = self.db.products.filter(self.db.products.barcode==barcode).one()
			result['barcode'] = product_data.barcode
			result['shortdesc'] = product_data.shortdesc
			result['price'] = product_data.price
					
		except:
			result = None
	
		return result
	
	def Transaction(self, memberid, barcode, count):
		
		result = {}
		
		try:
			product_data = self.db.products.filter(self.db.products.barcode==barcode).one()
			member_data = self.db.members.filter(self.db.members.member_id==memberid).one()
			
			self.db.transactions.insert(
									amount = -product_data.price,
									transaction_type = "SNACKSPACE",
									transaction_status = "COMPLETE",
									transaction_desc = product_data.shortdesc,
									product_id = product_data.product_id)
			
			member_data.balance -= product_data.price
			self.db.commit()

		except:
			result = None
		
		return result
		
	def __createTestDb(self):
		for table in tables:
			filename = "tb_%s.sql" % table
			localpath = "server/data/" + filename
			if not os.path.exists(localpath):
				urllib.urlretrieve(onlineSqlUrl + filename, localpath)
				
			sql = open(localpath).read()
			
			if table == 'transaction':
				table = 'transactions' ## Special case, filename != table name
				
			## Remove the "drop table" line, any autoincrement keywords and the engine specifier
			dropSQL = "drop table if exists %s;" % table
			sql = sql.replace(dropSQL, '')
			sql = sql.replace('auto_increment', '')
			sql = re.sub(r'ENGINE = \w*','',sql)
				
			# Execute the drop table line, then the create statement
			self.db.execute(dropSQL)
			self.db.commit()
			self.db.execute(sql)
			self.db.commit()
			
		# Insert test data
		sql = open(testDataPath).readlines()
		for line in sql:
			self.db.execute(line)
		self.db.commit()
		