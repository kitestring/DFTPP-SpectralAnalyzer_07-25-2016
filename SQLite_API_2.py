import sqlite3
import os

class Database():
	
	def __init__(self, filepath, tables):
		FilePath_Exists = os.path.exists(filepath)
		self.filepath = filepath
		self.conn = sqlite3.connect(self.filepath)
		self.cur = self.conn.cursor()
		self.table_list = tables
		
		if not(FilePath_Exists):
			for table in self.table_list:
				create_table_statement = '''
				CREATE TABLE %s(
				date_time TEXT PRIMARY KEY,
				file_name TEXT,
				conc_lvl TEXT,
				analysis_stage TEXT,
				det_voltage TEXT,
				Intensity_51 Double,
				Intensity_68 Double,
				Intensity_69 Double,
				Intensity_70 Double,
				Intensity_127 Double,
				Intensity_197 Double,
				Intensity_198 Double,
				Intensity_199 Double,
				Intensity_275 Double,
				Intensity_365 Double,
				Intensity_441 Double,
				Intensity_442 Double,
				Intensity_443 Double,
				CriteriaValue_51 Double,
				Result_51 TEXT,
				CriteriaValue_68 Double,
				Result_68 TEXT,
				CriteriaValue_70 Double,
				Result_70 TEXT,
				CriteriaValue_127 Double,
				Result_127 TEXT,
				CriteriaValue_197 Double,
				Result_197 TEXT,
				CriteriaValue_198 Double,
				Result_198 TEXT,
				CriteriaValue_199 Double,
				Result_199 TEXT,
				CriteriaValue_275 Double,
				Result_275 TEXT,
				CriteriaValue_365 Double,
				Result_365 TEXT,
				CriteriaValue_441 Double,
				Result_441 TEXT,
				CriteriaValue_442 Double,
				Result_442 TEXT,
				CriteriaValue_443 Double,
				Result_443 TEXT,
				Result_Overall TEXT)
				''' % table
				self.conn.execute(create_table_statement)
	
	def Get_Columns(self, table):
		#returns a tuple list with all the column names from a given db connection
		column_query = self.conn.execute('SELECT * from %s' % table)
		return [description[0] for description in column_query.description]
	
	def Insert_Query_No_Conditions(self, table, columns, values):
		self.conn.execute("INSERT INTO %s %s VALUES %s" % (table, tuple(columns), tuple(values)))
		#self.conn.commit()
		
	def Update_Query(self, table, columns, values, condition):
		query_statement = "UPDATE %s" % table
		
		#create SET portion of query statement including column = value pairs
		col_val = " SET"
		for index, column in enumerate(columns):
			col_val += " %s = '%s'," % (column, values[index])
		col_val = col_val[:-1]
		
		#Define condition
		cond = " WHERE %s" % condition
		
		query_statement += col_val + cond
		
		#print query_statement
		
		self.conn.execute(query_statement)
		#self.conn.commit()
			
			
	
	def Select_Query(self, keyword, table, columns, condition, sort):
	
		if keyword == None:
			query_statement = "SELECT"
		else:
			query_statement = "SELECT %s" % keyword
		
		#create columns portion of query statement (column1, column2,...)
		col = ""
		for column in columns:
			col += " %s," % column
		col = col[:-1]
		
		query_statement += "%s FROM %s" % (col, table)
		
		if condition != None:
			query_statement += " WHERE %s" % condition

		if sort != None:
			query_statement += " ORDER BY %s" % sort
		
		#print 'query_statement', query_statement
		
		cursor = self.conn.execute(query_statement)
		query_lst = cursor.fetchall()
		
		if query_lst == []:
			Null_Query = True
		else:
			Null_Query = False
			
		return query_lst, Null_Query
	
	