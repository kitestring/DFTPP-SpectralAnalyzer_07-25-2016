import wx
import time
from sqliteapi import Database 
from excelwriter import ExcelFile
import sqlite3
from subprocess import call
import datetime
import os

class DFTPP_eval_Frame(wx.Frame):
	def __init__(self, parent, title):
		frame_width = 550
		frame_height = 410
		wx.Frame.__init__(self, parent, title=title, size=(frame_width,frame_height))
		
		#Bind events
		self.Bind(wx.EVT_CLOSE, self.OnExit)
		
	def OnExit(self, event):
		panel.EventLogger('Saving & Disconnecting from databases.\n\t\tPlease Wait...')
		panel.dftppDB.conn.close()
		self.Destroy()
		
		
class DFTPP_eval_Panel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		
		#Set global values
		self.DFTPP_Evaluated_Masses = [51,68,69,70,127,197,198,199,275,365,441,442,443]
		self.DFTPP_Criteria_Masses = [51,68,70,127,197,198,199,275,365,441,442,443]
		self.InstSN = ''
		
		self.limits_headers = ['max/min dates', '51 lower limit', '51 upper limit', '68 upper limit', '70 upper limit', '127 lower limit', '127 upper limit',
								'197 upper limit', '198 lower limit', '199 lower limit', '199 upper limit', '275 lower limit', '275 upper limit',
								'365 upper limit','441 lower limit', '441 upper limit', '442 lower limit', '443 lower limit', '443 upper limit']
		
		self.limits = [[0.1, 0.8, 0.02, 0.02, 0.1, 0.8, 0.02, 0.5, 0.05, 0.09, 0.1, 0.6, 0.01, 0.0, 0.24, 0.5, 0.15, 0.24],
						[0.1, 0.8, 0.02, 0.02, 0.1, 0.8, 0.02, 0.5, 0.05, 0.09, 0.1, 0.6, 0.01, 0.0, 0.24, 0.5, 0.15, 0.24]]
						
		self.GraphMetaDataDict = {'CriteriaValue_51': ['m/z = 51: 10-80% of Base Peak', '51/Base Peak',16,[42,43]],
								'CriteriaValue_68': ['m/z = 68: < 2% of Mass 69', '68/69',18,[44]],
								'CriteriaValue_70': ['m/z = 70: < 2% of Mass 69', '70/69',20,[45]],
								'CriteriaValue_127': ['m/z = 127: 10-80% of Base Peak', '127/Base Peak',22,[46,47]],
								'CriteriaValue_197': ['m/z = 197: < 2% of 198', '197/198',24,[48]],
								'CriteriaValue_198': ['m/z = 198: Base Peak, or > 50% of Mass 442', '198/442',26,[49]],
								'CriteriaValue_199': ['m/z = 199: 5-9% of Mass 198', '199/198',28,[50,51]],
								'CriteriaValue_275': ['m/z = 275: 10-60% of Base Peak', '275/Base Peak',30,[52,53]],
								'CriteriaValue_365': ['m/z = 365: < 1% of Mass 198', '365/198',32,[54]],
								'CriteriaValue_441': ['m/z = 441: present but < 24% of mass 442', '441/442',34,[55,56]],
								'CriteriaValue_442': ['m/z = 442: Base Peak, or > 50% of Mass 198', '442/198',36,[57]],
								'CriteriaValue_443': ['m/z = 443: 15-24% of Mass 442', '443/442',38,[58,59]]}
								
		self.LevelConcentrations = {'1': 'DFTPP 100 fg\n', '2': 'DFTPP 1 pg\n', '3': 'DFTPP 10 pg\n', '4': 'DFTPP 50 pg\n'}
		
		self.EvaluationDict =  {51: [[0.1,0.8], 'base_peak_intensity', '>= and <='],
								68: [[0.02], 69, '<='],
								70: [[0.02], 69, '<='],
								127: [[0.1,0.8], 'base_peak_intensity', '>= and <='],
								197: [[0.02], 198, '<='],
								198: [[0.5], 442, '>='],
								199: [[0.05,0.09], 198, '>= and <='],
								275: [[0.1,0.6], 'base_peak_intensity', '>= and <='],
								365: [[0.01], 'base_peak_intensity', '<='],
								441: [[0.0,0.24], 442, '>= and <='],
								442: [[0.5], 198, '>='],
								443: [[0.15,0.24], 442, '>= and <=']}
		
		
		
		#Connect to database
		fp = 'S:\\005_Saturn\\Analyses\\P01-T060_D2D Stability - II\\DFTPP_Automated_Processing\\dftpp.db'
		#fp = 'C:\\DFTPP_v1.0\\dftpp.db'
		self.dftppDB = Database(fp)
		self.dftppDB_columns = self.dftppDB.Get_Columns('dftpp')
		
		#Set spreadsheet column starting values
		self.start_row = 1
		self.start_column = 16
		self.limits_column = self.start_column + len(self.dftppDB_columns) - 4
	
		#create sizers
		main_VertSizer = wx.BoxSizer(wx.VERTICAL)
		buttons_HorzSizer = wx.BoxSizer(wx.HORIZONTAL)
		buttons_VertSizer = wx.BoxSizer(wx.VERTICAL)
		controls_HorzSizer = wx.BoxSizer(wx.HORIZONTAL)
		
		#create status output text control
		self.lbl_status_logger = wx.StaticText(self, label=" Status Output: ")
		main_VertSizer.Add(self.lbl_status_logger, wx.ALIGN_LEFT)
		self.status_logger = wx.TextCtrl(self, size=(530,300), style=wx.TE_MULTILINE | wx.TE_READONLY)
		main_VertSizer.Add(self.status_logger, wx.ALIGN_LEFT)
		
		#create radio buttons
		radioList = ['VP1', 'VP2', 'GS']
		self.instrument_SN_radiobut = wx.RadioBox(self, label="Instrument",  
			choices=radioList, style=wx.RA_SPECIFY_COLS)
		# self.Bind(wx.EVT_RADIOBOX, self.EvtInstrumentSNRadiobut, self.instrument_SN_radiobut)
		
		#create buttons
		self.mine_data_btn = wx.Button(self, label = "Mine Data")
		self.display_data_btn = wx.Button(self, label = "Display Data")
		
		buttons_HorzSizer.Add(self.mine_data_btn, wx.ALIGN_BOTTOM)
		buttons_HorzSizer.Add(self.display_data_btn, wx.ALIGN_BOTTOM)
		buttons_VertSizer.Add((10,25))
		buttons_VertSizer.Add(buttons_HorzSizer)
		controls_HorzSizer.Add(self.instrument_SN_radiobut)
		controls_HorzSizer.Add(buttons_VertSizer)
		
		
		self.Bind(wx.EVT_BUTTON, self.OnMineData, self.mine_data_btn)
		self.Bind(wx.EVT_BUTTON, self.OnDisplayData, self.display_data_btn)
		
		
		
		
		main_VertSizer.Add(controls_HorzSizer)
		self.SetSizerAndFit(main_VertSizer)
	
	# def EvtInstrumentSNRadiobut(self, event):
		# print 'You clicked the radio button'
		# print 'self.instrument_SN_radiobut.GetStringSelection(): ', self.instrument_SN_radiobut.GetStringSelection()
		# print 'self.instrument_SN_radiobut.GetSelection(): ', self.instrument_SN_radiobut.GetSelection()
	
	def OnMineData(self, event):
		#jump
		self.InstSN = str("%s" % self.instrument_SN_radiobut.GetStringSelection())
		self.dirname = ''
		
		#Get DFTPP txt raw data files
		dlg = wx.FileDialog(self, "Select the DFTPP txt raw data files to import", self.dirname, "", "*.txt", wx.FD_MULTIPLE)
		if dlg.ShowModal() == wx.ID_OK:
		
			#get the txt full paths and file names from dialogue objects
			txt_fullpaths_lst = dlg.GetPaths()
			txt_filenames_lst = dlg.GetFilenames()
			
			#define the DFTPP Spectral dictionary
			DFTPP_Spectral_dict = {}
			
			#Iterate through each txt file defined
			#and mine DFTPP intensities to populate raw_spectrum
			for txtfile_index, txt_file in enumerate(txt_fullpaths_lst):
			
				#dump the file contents into txt_file_contents
				txt_file_contents = open(txt_file, 'r')
			
				#Set / reset boolean values
				DFTPP_Found = False
				Name_Header_Found = False
				Spectrum_Header_Found = False
				All_Headers_Found = True
				
				#Set / reset dftpp database values list
				dftpp_database_values_lst = []
				
				#Iterate through each line of the given file
				for line_index, line in enumerate(txt_file_contents):
					
					#parce the header line into a list & remove the "\n" from the last list element
					line_parced = line.split("\t")
					line_parced[-1] = line_parced[-1].replace("\n","")

					if line_index == 0:
						#reformat input datetime (mm/dd/yyyy hh:mm:ss 12 hour clock) into yyyy-mm-dd hh:mm:ss 24 hour clock
						#then append to dftpp_database_values_lst
						#also append text file name to dftpp_database_values_lst
						
						datetime_parced  =  line_parced[0].split(" ")
						
						try:
							reformatted_date = str(datetime.datetime.strptime(datetime_parced[0], '%m/%d/%Y').strftime('%Y-%m-%d'))
							time_parced = datetime_parced[1].split(":")
							if datetime_parced[2] == "PM" and int(time_parced[0]) < 12:
								time_parced[0] = str(int(time_parced[0]) + 12)
							elif datetime_parced[2] == "AM" and int(time_parced[0]) == 12:
								time_parced[0] = str(int(time_parced[0]) - 12)
							reformatted_time = '%s:%s:%s' % (time_parced[0], time_parced[1], time_parced[2])
							reformatted_datetime = "%s %s" % (reformatted_date, reformatted_time)


							dftpp_database_values_lst.append(reformatted_datetime)
							dftpp_database_values_lst.append(str(txt_filenames_lst[txtfile_index]))
						
						except ValueError:
							#This is an imporperly formatted source data file; skip file and move on
							All_Headers_Found = False
							dftpp_database_values_lst.append('PlaceHolder')
							dftpp_database_values_lst.append(str(txt_filenames_lst[txtfile_index]))
							break
						
					elif line_index == 1:
						#append conc_lvl, analysis_stage, & det_voltage to dftpp_database_values_lst
						sample_attributes_parced  =  line_parced[0].split(" ")
						dftpp_database_values_lst.append(sample_attributes_parced[0])
						dftpp_database_values_lst.append(sample_attributes_parced[1])
						dftpp_database_values_lst.append(sample_attributes_parced[2])
						
					elif line_index == 2:
						#Find the 'Name' & 'Spectrum' header index numbers
						for header_index, header in enumerate (line_parced):
							if header == 'Name':
								Name_Header_Found = True
								Name_Header_Index = header_index
							elif header == 'Spectrum':
								Spectrum_Header_Found = True
								Spectrum_Header_Index = header_index
								
						if Name_Header_Found == False or Spectrum_Header_Found == False:
							#This is an imporperly formatted source data file; skip file and move on
							All_Headers_Found = False
							break
						
					elif line_index >= 3:
						#Find the 'DFTPP' line and grab the corresponding spectrum
						#Note 'Bis(pentafluorophenyl)phenyl phosphine' is synonym for DFTPP
						if line_parced[Name_Header_Index] == 'Bis(pentafluorophenyl)phenyl phosphine':
							spectrum = line_parced[Spectrum_Header_Index]
							DFTPP_Found = True
							break
					
				if DFTPP_Found == True and All_Headers_Found == True:
					#Spectrum mined, parce it out and add it to the database
					
					#1)Seperate spectral data from single string and parce into database values list
					#2)Calculate criteria value for each respective mass and add to database values list
					#3)Determine criteria result (pass/fail) and add result to database values list
					#4)Insert DFTPP data into database
					
					''' 1) Parce spectral data currently stored in a single string then add to DFTPP Spectral dictionary'''
					#Clear spectral dict then
					#Create dictionary (key = mass : value = intensity) from given spectrum
					DFTPP_Spectral_dict.clear()
					DFTPP_Spectral_dict = self.generate_spectral_dict(spectrum)
					
					#iterate through evaluated masses adding each 
					#corresponing intensity to the database values list
					for mass in self.DFTPP_Evaluated_Masses:
						dftpp_database_values_lst.append(DFTPP_Spectral_dict.get(mass,0))
						
					''' 2) Calculate criteria value for each respective mass and add to database values list'''
					''' and '''
					''' 3) Determine criteria result (pass/fail) and add result to database values list'''

					
					# set / reset fail counter
					fail_count = 0
				
					#deterine base peak
					base_peak_intensity = max(dftpp_database_values_lst[5:])
					
					for mz in self.DFTPP_Criteria_Masses:
						
						#calculate the criteria value
						try:
							if self.EvaluationDict[mz][1] == 'base_peak_intensity':
								criteria_value = DFTPP_Spectral_dict.get(mz,0) / base_peak_intensity
							else:
								criteria_value = DFTPP_Spectral_dict.get(mz,0) / DFTPP_Spectral_dict.get(self.EvaluationDict[mz][1],0)
								
						except	ZeroDivisionError:
							criteria_value = 0
						
						
						#determine if criteria_value gives a passing or failing result
						if self.EvaluationDict[mz][2] == '>= and <=':
							if criteria_value >= self.EvaluationDict[mz][0][0] and criteria_value <= self.EvaluationDict[mz][0][1]:				
								dftpp_result = "Pass"
							else:
								dftpp_result = "Fail"
								fail_count += 1
								
						elif self.EvaluationDict[mz][2] == '<=':
							if criteria_value <= self.EvaluationDict[mz][0][0]:				
								dftpp_result = "Pass"
							else:
								dftpp_result = "Fail"
								fail_count += 1
								
						elif self.EvaluationDict[mz][2] == '>=':
							if criteria_value >= self.EvaluationDict[mz][0][0]:				
								dftpp_result = "Pass"
							else:
								dftpp_result = "Fail"
								fail_count += 1
						
						elif self.EvaluationDict[mz][2] == '> and <=':
							if criteria_value > self.EvaluationDict[mz][0][0] and criteria_value <= self.EvaluationDict[mz][0][1]:				
								dftpp_result = "Pass"
							else:
								dftpp_result = "Fail"
								fail_count += 1
						
						#append results to respective lists
						dftpp_database_values_lst.append(criteria_value)
						dftpp_database_values_lst.append(dftpp_result)
					
					 
					#Overall DFTPP result
					if fail_count == 0:
						dftpp_database_values_lst.append("Pass")
					else:
						dftpp_database_values_lst.append("Fail")
						
					#Append Instrument serial number (Instrument_SN)
					dftpp_database_values_lst.append(self.InstSN)
					
					#Append with unique identifier for record: primary key = Instrument_SN_date_time
					dftpp_database_values_lst.append("%s_%s" % (self.InstSN, reformatted_datetime))
						
					#Prompt status message & attempt insert query
					message = "DFTPP found in sample. Spectral data successully mined.\n\t\tSource File: %s\n\t\tDFTPP Tuning Result: %s" % (dftpp_database_values_lst[1], dftpp_database_values_lst[-3])
					self.EventLogger(message)
					self.insert_query('dftpp', self.dftppDB_columns, dftpp_database_values_lst)
					
				elif DFTPP_Found == False and All_Headers_Found == True:
					#DFTPP not found, it is assumed that in was in the sample but not detected
					#0's and fails will be filled into the intensities, criteria values, and results
					
					#Set all intensities = 0
					dftpp_database_values_lst[5:] = [0 for x in range(13)]
					
					#Set criteria values and results = 0 & Fail respectively
					for x in range(12):
						dftpp_database_values_lst.append(0)
						dftpp_database_values_lst.append("Fail")
					
					#Set Overall Result to Fail
					dftpp_database_values_lst.append("Fail")
					
					#Append Instrument serial number (Instrument_SN)
					dftpp_database_values_lst.append(self.InstSN)
					
					#Append with unique identifier for record: primary key = Instrument_SN_date_time
					dftpp_database_values_lst.append("%s_%s" % (self.InstSN, reformatted_datetime))
					
					message = "DFTPP not found in sample.  Setting all values to 0's or Fail.\n\t\tSource File: %s\n\t\tDFTPP Tuning Result: %s" % (dftpp_database_values_lst[1], dftpp_database_values_lst[-3])
					self.EventLogger(message)
					
					self.insert_query('dftpp', self.dftppDB_columns, dftpp_database_values_lst)
					
				elif All_Headers_Found == False:
					#The Name & Spectrum headers were not found or the file is imporperly formatted, therefor it will be skipped
					message = "Invalid Formatting - This text file is not properly formatted.\n\t\tSource File: %s\n" % dftpp_database_values_lst[1]
					self.EventLogger(message) 
		
		self.EventLogger('Action Complete\n')
		dlg.Destroy()
		
	def OnDisplayData(self, event):
	
		self.InstSN = str("%s" % self.instrument_SN_radiobut.GetStringSelection())
	
		#Get list of every distinct analytical stage found in the database
		
		keyword = 'DISTINCT'
		table = 'dftpp'
		columns = ['analysis_stage']
		condition = "Instrument_SN = '%s'" % self.InstSN
		sort = 'analysis_stage ASC'
		anal_stg_lst, null_anal_stg = self.dftppDB.Select_Query(keyword, table, columns, condition, sort)
		anal_stg_lst = [str("%s" % x) for x in anal_stg_lst]
		
		if null_anal_stg == False:
		
			userhome = os.path.expanduser('~')
			userhome += '\\Desktop\\'
		
			#Iterate through analysis stage
			for stage in anal_stg_lst:
			
				#Get list of every distinct concentration level witin the given analytical stage found in the database
				keyword = 'DISTINCT'
				table = 'dftpp'
				columns = ['conc_lvl']
				condition = "analysis_stage = '%s' AND Instrument_SN = '%s'" % (stage, self.InstSN)
				sort = 'conc_lvl ASC'
				conc_lvl_lst, null_conc_lvl = self.dftppDB.Select_Query(keyword, table, columns, condition, sort)
				conc_lvl_lst = [str("%s" % x) for x in conc_lvl_lst]
			
				excel_file_namepath = '%s%s_DFTPP_Tuning_Stage_%s.xlsx' % (userhome, self.InstSN, stage)
				
				xlsx = ExcelFile(excel_file_namepath)
				
				
				#Iterate through concentration level list
				for lvl in conc_lvl_lst:
					
					sheet_name = 'Level %s' % lvl
					xlsx.add_sheet(sheet_name)
					
					
					
					keyword = None
					columns = [x for x in self.dftppDB_columns]
					columns.remove('conc_lvl')
					columns.remove('analysis_stage')
					columns.remove('Instrument_SN')
					columns.remove('Instrument_SN_date_time')
					condition = "analysis_stage = '%s' AND conc_lvl = '%s' AND Instrument_SN = '%s'" % (stage, lvl, self.InstSN)
					sort = 'date_time ASC'
					dftpp_record_lst, null_dftpp_record = self.dftppDB.Select_Query(keyword, table, columns, condition, sort)
					
					#drop headers
					xlsx.add_list_of_lists(self.start_row, self.start_column, [columns], 'headers')
					#drop data
					xlsx.add_list_of_lists(self.start_row + 1, self.start_column, dftpp_record_lst, 'data')
					
					last_row = len(dftpp_record_lst) + self.start_row + 1
					
					#drop limits headers
					xlsx.add_list_of_lists(self.start_row, self.limits_column, [self.limits_headers], 'limitsheaders')
					xlsx.add_list_of_lists(self.start_row + 1, self.limits_column + 1, self.limits,'limits')
					xlsx.max_min_date_formulas(self.start_row + 1, self.limits_column, self.start_column)
					
					#get the keys for the self.GraphMetaDataDict
					GraphMetaDataDict_keys = []
					for col in columns:
						if col[:13] == 'CriteriaValue':
							GraphMetaDataDict_keys.append(col)
							
					#jump
					
					for graph_count, key in enumerate(GraphMetaDataDict_keys):
					
						#Add graphs
						chart_title_prefix = 'Pegasus BT %s - %s' % (self.InstSN, self.LevelConcentrations[lvl])
						starting_graph_row = self.start_row + 2
						xlsx.scatter_plots(sheet_name, self.start_column, starting_graph_row, last_row, self.limits_column, 
											graph_count, chart_title_prefix, self.GraphMetaDataDict[key])
					
					
					
				xlsx.disconnect()
				xlsx = None

			message = "Data Report Generated"
					
		else:
			message = "Insufficent database records to query."
			
		self.EventLogger(message)
		self.EventLogger('Action Complete\n')
				
		
	def EventLogger(self, message):
		current_time = str(time.strftime("%H:%M:%S"))
		current_date = str(time.strftime("%m/%d/%Y"))
		status_message = "%s %s - %s\n" % (current_date, current_time, message) 
		self.status_logger.AppendText(status_message)
		
	def parce_spectral_data_float(self, spectrum):
		''' spectral data input: "mass_1:intensity_1 mass_2:intensity_2..." 
			spectral data output: 
				mass_list[mass_1, mass_2] & intensity_list[intenstiy_1, intensity_2]
				each output list is formatted as float values '''
			
		mass_list = []
		intensity_list = []
		
		#parce spectral data into mass:intensity elements
		mass_intensity = spectrum.split(" ")
		
		#parce each mass:intensity element into their own independent lists
		for m_i_pair in mass_intensity:
		
			m_i_list = m_i_pair.split(":")
			
			#convert mass & intensities from a string to a float
			mass_list.append(float(m_i_list[0]))
			intensity_list.append(float(m_i_list[1]))
			
		return mass_list, intensity_list
		
	def generate_spectral_dict(self, spectrum):
		
		mass_list = []
		intensity_list = []
		DFTPP_dict = {}
		
		mass_list, intensity_list = self.parce_spectral_data_float(spectrum)
		mass_list, intensity_list = self.remove_false_duplicates(mass_list, intensity_list)
		
		for index, mass in enumerate(mass_list):	
			DFTPP_dict[mass] = intensity_list[index]
			
		return DFTPP_dict	
		
	def remove_false_duplicates(self, mass_list, intensity_list):
		''' After converting the exact masses to nominal there may be some duplicate masses.
			This logic will discard duplicate masses with lesser intensities '''
			
		nominal_mass_list = [int(round(x)) for x in mass_list]
		
		continue_loop = True
		
		while continue_loop:
			continue_loop = False
		
			for index, mass in enumerate(nominal_mass_list[:-1]):
			
				if mass == nominal_mass_list[index+1]:
				
					continue_loop = True
					
					if intensity_list[index] >= intensity_list[index+1]:
						clear_index = index+1
					else:
						clear_index = index
			
					del nominal_mass_list[clear_index]
					del mass_list[clear_index]
					del intensity_list[clear_index]
					break

		return nominal_mass_list, intensity_list
	
	def insert_query(self, table, columns, values):
		
		try:
			self.dftppDB.Insert_Query_No_Conditions(table, columns, values)
			message = 'Success - DFTPP data added to database. - %s\n' % values[1]
			self.EventLogger(message)
		except sqlite3.IntegrityError:
			display_datetime = self.display_datetime(values[0])
			#yes = True and no = False
			question = '''There is already DFTPP data within the database
						matching the dates found in this text file:
						
						File Name: %s
						Time Stamp: %s
						
						Do you wish to replace the existing database records 
						with the new information found within this text file?''' % (values[1], display_datetime)
			caption = "OVERWRITE WARNING - %s" % values[1]
			dlg = wx.MessageDialog(self, question, caption, wx.YES_NO | wx.ICON_QUESTION)
			overwrite_data = dlg.ShowModal() == wx.ID_YES
			dlg.Destroy()
			message = "OVERWRITE WARNING - User overwrite data = %s\n\t\tSource File: %s" % (str(overwrite_data), values[1])
			self.EventLogger(message)
			
			if overwrite_data == True:
				condition = "date_time = '%s'" % values[0]
				self.dftppDB.Update_Query('dftpp', self.dftppDB_columns, values, condition)
				message = 'DFTPP record updated. - %s\n' % values[1]
			elif overwrite_data == False:
				message = 'Omitted - The DFTPP data within this file has been omitted. - %s\n' % values[1]
				
			self.EventLogger(message)		
	
	def display_datetime(self, database_datetime):
		return datetime.datetime.strptime(database_datetime, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y %H:%M:%S')

		
app = wx.App(False)
frame = DFTPP_eval_Frame(None, title="DFTPP Evaluator 1.3")
panel = DFTPP_eval_Panel(frame)
frame.Show(True)
app.MainLoop()
