import xlsxwriter
import datetime

class ExcelFile():
	
	def __init__(self, filepath):
		self.wkbk = xlsxwriter.Workbook(filepath)
		self.ColumnLetter = ['A','B','C','D','E','F','G','H','I','J','K','L','M',
							'N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
							'AA','AB','AC','AD','AE','AF','AG','AH','AI','AJ','AK','AL','AM',
							'AN','AO','AP','AQ','AR','AS','AT','AU','AV','AW','AX','AY','AZ',
							'BA','BB','BC','BD','BE','BF','BG','BH','BI','BJ','BK','BL','BM',
							'BN','BO','BP','BQ','BR','BS','BT','BU','BV','BW','BX','BY','BZ',
							'CA','CB','CC','CD','CE','CF','CG','CH','CI','CJ','CK','CL','CM',
							'CN','CO','CP','CQ','CR','CS','CT','CU','CV','CW','CX','CY','CZ',
							'DA','DB','DC','DD','DE','DF','DG','DH','DI','DJ','DK','DL','DM',
							'DN','DO','DP','DQ','DR','DS','DT','DU','DV','DW','DX','DY','DZ',
							'EA','EB','EC','ED','EE','EF','EG','EH','EI','EJ','EK','EL','EM',
							'EN','EO','EP','EQ','ER','ES','ET','EU','EV','EW','EX','EY','EZ',
							'FA','FB','FC','FD','FE','FF','FG','FH','FI','FJ','FK','FL','FM',
							'FN','FO','FP','FQ','FR','FS','FT','FU','FV','FW','FX','FY','FZ',
							'GA','GB','GC','GD','GE','GF','GG','GH','GI','GJ','GK','GL','GM',
							'GN','GO','GP','GQ','GR','GS','GT','GU','GV','GW','GX','GY','GZ']

	def add_sheet(self, sheet_name):
		self.sheet = self.wkbk.add_worksheet(sheet_name)
		self.sheet.set_column('A:A', 2.5)
		
	def add_list_of_lists(self, start_row, start_column, list_of_lists, data_type):
		#will iterate through a list of lists adding each list element as 
		#a new row of data.  If the start_row and start_column are both 0
		#then the data dump will begin in cell A1. 
		
		for row_num, data_row in enumerate(list_of_lists):
			row = row_num + start_row
			for col_num, data_value in enumerate(data_row):
				col = col_num + start_column
				
				if col_num == 0 and data_type == 'data':
					cell_number_format = self.wkbk.add_format({'num_format': 'm/d/yyyy h:mm:ss'})
					datetime_object = datetime.datetime.strptime(data_value, '%Y-%m-%d %H:%M:%S')
					self.sheet.write_datetime(row, col, datetime_object, cell_number_format)
				elif ((col_num == 1 or data_value == 'Pass' or data_value == 'Fail') and data_type == 'data') or data_type == 'headers' or data_type == 'limitsheaders' :
					self.sheet.write_string(row, col, data_value)
				else:
					self.sheet.write_number(row, col, float(data_value))
					
	def max_min_date_formulas(self, row, column, formula_column_index):
		cell_number_format = self.wkbk.add_format({'num_format': 'm/d/yyyy h:mm:ss'})
		
		letter = self.ColumnLetter[formula_column_index]
		
		formula = "=MIN(%s:%s)" % (letter, letter)
		self.sheet.write_formula(row, column, formula, cell_number_format)
		
		formula = "=MAX(%s:%s)" % (letter, letter)
		self.sheet.write_formula(row+1, column, formula, cell_number_format)
	
	def add_scatter_plot(self, cat_range, val_range_ser1, name_ser1, x_label, y_label, chart_name):
		chart = self.wkbk.add_chart({'type': 'scatter'})
		
		chart.add_series({
			'categories': cat_range,
			'values': val_range_ser1,
			'name': name_ser1,
			'marker': {
				'type': 'circle',
				'size,': 7,
				'border': {'color': 'black'},
				'fill':   {'color': 'yellow'}}
			})
			
		chart.set_x_axis({'num_format': 'm/d', 'name': x_label})
		chart.set_y_axis({'name': y_label})
		chart.set_size({'width': 950, 'height': 550})
		chart.set_title({'name': chart_name})
		chart.set_legend({'none': True})
		
		self.sheet.insert_chart(1,1, chart)
		
	def scatter_plots(self, sheet_name, start_col, start_row, last_row, limits_column, chart_index, 
						chart_title_prefix, meta_data_lst):

		letter = self.ColumnLetter[start_col]
		x_axis_range =  "='%s'!%s%s:%s%s" % (sheet_name, letter, start_row, letter, last_row)
		
		index = meta_data_lst[2] + start_col
		letter = self.ColumnLetter[index]
		y_axis_range = "='%s'!%s%s:%s%s" % (sheet_name, letter, start_row, letter, last_row)
	
		chart = self.wkbk.add_chart({'type': 'scatter'})
		
		chart.add_series({
			'categories': x_axis_range,
			'values': y_axis_range,
			'name': meta_data_lst[1],
			'marker': {
				'type': 'circle',
				'size,': 5,
				'border': {'color': 'black'},
				'fill':   {'color': 'yellow'}}
			})
			
		letter = self.ColumnLetter[limits_column]
		last_row = start_row + 1
		x_axis_range =  "='%s'!%s%s:%s%s" % (sheet_name, letter, start_row, letter, last_row)
		
		for col_offset in meta_data_lst[3]:
			
			index = col_offset + start_col
			letter = self.ColumnLetter[index]
			y_axis_range = "='%s'!%s%s:%s%s" % (sheet_name, letter, start_row, letter, last_row)
			series_name = "%s-limits" % meta_data_lst[1]
			
			chart.add_series({
				'categories': x_axis_range,
				'values': y_axis_range,
				'name': series_name,
				'line': {
					'color': 'red',
					'dash_type': 'dash'},
				'marker': {
					'type': 'square',
					'size,': 5,
					'border': {'color': 'black'},
					'fill':   {'color': 'red'}}
				})
				
				
			
		chart.set_x_axis({'num_format': 'm/d', 'name': 'Date'})
		chart.set_y_axis({'name': meta_data_lst[1]})
		chart.set_size({'width': 950, 'height': 550})
		chart_title = "%s%s" % (chart_title_prefix, meta_data_lst[0])
		chart.set_title({'name': chart_title})
		chart.set_legend({'none': True})
		
		chart_row = 1 + (chart_index * 28)
		
		self.sheet.insert_chart(chart_row,1, chart)

	
	def disconnect(self):
		self.wkbk.close()