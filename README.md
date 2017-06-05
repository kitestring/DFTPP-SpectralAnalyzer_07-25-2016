# DFTPP-SpectralAnalyzer_07-25-2016

Date Written: 08/25/2016

Industry: Time of Flight Mass Spectrometer Developer & Manufacturer

Department: Validation (Late Stage R&D)

GUI: “GUI.png”

Experiment Description:

The purpose of this experiment was to determine the stability, spectral quality, and consistency of the molecular fragmentation via election impact over a 25 day period of time for our time of flight mass spectrometer.  This was quantified by monitoring the fragmentation behavior of Bis(pentafluorophenyl)phenyl phosphine (DFTPP) at 4 different concentration levels during the duration of the study.  Each concentration level was measured ten times each day for a total of 40 measurements each day.  This was done across three different instruments.  The intensity of a given molecular fragment (ion) is normalized against the most abundant ion (ion ratio).  After each measurement, the instrument would export a single tab delimited text file. 

Data Accumulation & Mining:

If you’ve been doing the math that’s 40 text files per day X 25 days X 3 instruments = 3,000 text files.  Taking it a step further, each text file contained between 70 & 120 chemicals that were detected in the chemical mixture, and only 1 (DFTPP) was relevant to the study.  Once the DFTPP chemical was found in the text file, the spectral data would be mined as a single string.  

A fair bit of data condition was necessary to parse this string into is quantifiable components.  The string is formatted as follows: “Mass of Ion Fragment-1:Intensity of Ion Fragment2 Mass of Ion Fragment-1:Intensity of Ion Fragment2…”  Typically there would be between 45 – 75 Ion Fragments and we were interested in 13 of them.  See the example below of what the string containing the spectral information which is mined from the text file looks like:

“48.03303:1871.89 48.30466:326.35 48.91353:293.19 49.07603:4052.76 49.12221:4147.20 49.37269:330.48 49.71332:760.07 50.03403:103661.37 50.35255:748.61 50.52097:1460.85 50.60743:965.30 50.64109:564.83 50.72978:775.13 50.82978:457.36 51.04194:384227.10 51.33918:5464.41 51.54390:332.72 51.61111:344.65 52.04463:22306.31 52.26301:392.93 52.35325:364.63 53.83059:467.15 55.99247:10740.97 57.00714:30375.54 61.02255:9076.88 62.03485:6937.05 63.04247:16029.40 64.04005:3091.41 65.04925:10496.24 66.46747:290.92 68.01608:10468.09 68.98340:462441.58 69.39821:1069.56 73.02182:3662.98 74.02468:36432.76 75.01227:67513.57 76.04117:20449.76 76.52775:764.88 77.04958:371560.70 77.50774:6934.69 78.05256:30935.80 79.01091:30248.72 79.12840:1332.41 80.00649:25348.92 80.29860:352.47 80.35454:426.02 80.43848:374.59 80.75978:678.09 80.85886:313.15 81.00506:29671.39 81.56193:266.63 82.01267:7073.97”
The challenge is that the exact Mass value of the same fragment varies to some degree from one measurement to the next.  So when adding this information to the SQL database you have to use a fairly robust algorithm to ensure you are grouping the correction ion fragments.

Sample Raw Data:

“Day 1 L-3 v-1.txt” Provides an example of a single tab delimited text file exported from one of our chemical analyzers.

Sample Output:

“SampleData_WellBehaved_IonRatio.png” & “SampleData_Problem_IonRatio.png”  These are examples of two different ion ratios plotted over a ten day duration of the investigation.  The acceptance criteria is overlaid on the graph as a dashed red line.  These plots makes visually assessing the instruments ability to consistently meeting the acceptance criteria very easy.
Additionally I’ve included a table showing the acceptance criteria of each ion ratio. “DFTPP_Pass-Fail_Criteria.png”.

Application Description:

This application has two basic functionalities: 

1) Mine the appropriate spectral data from the text files and load it into a SQL database.  
2) Create data visualizations in new excel file by utilizing the xlswriter python library. 

Having the ability to continually append the SQL database each day of the investigation, and subsequently, generate new excel files with the latest data, allowed me monitor the data during the course of the experiment.  This turned out to be a critical advantage as I was able to very quickly and easily identify and address any anomalous behavior that popped during the course of the investigation.
