import win32com.client

class Macros():

	def __init__(self):
		self.ExcelMarcoFilePath = 'C:\\DATAQUEST\\OtherProjects\\DFTPP\\Excel2013_WkBk.xlsm'
		self.Macro_Prefix = "Excel2013_WkBk.xlsm!vbamodule."
		self.xl = win32com.client.Dispatch("Excel.Application")
		self.xl.Visible = False
	
	def AddPassFailStats(self, ExcelDataFilePath):
		Macro_Name = self.Macro_Prefix + "dftpppassfailstats"
		self.xl.Workbooks.Open(Filename=self.ExcelMarcoFilePath)
		self.xl.Application.Run(Macro_Name, ExcelDataFilePath)
		self.xl.Quit()
		