#!/usr/bin/python

import sys
import os

#Usage information
def printUsage():
	print "This script reads in data produced by the Social Security Administration about baby names and runs very simple gender statistics on it."
	print "Usage:       ./namestat.py name [outputType] [startYear] [endYear]"
	print "name         The name you would like statistical information about. Case sensitive."
	print "outputType   y(ear) or d(ecade). Default d."
	print "startYear    The year you would like data reporting to begin. Default 1880."
	print "endYear      The year you would like data reporting to end. Default 2018."
	print
	print "This was written primarily for the author's own benefit and the benefit of their growing family. It was designed to get the job"
	print "done quick and dirty. It does very little sanity checking. If you want to use a command line argument, you must use all of the"
	print "previous optional arguments. If you put any files in the data directory that are not in the appropriate format, it will break. If"
	print "you have any files in the data directory whose names are not integers, it will break. Malformed input might show this message. Or"
	print "it just might break."
	print
	print "As of 10/24/19, The data the SSA produces can be found at https://www.ssa.gov/oact/babynames/names.zip"
	print "The data files in that archive must be mass renamed so that their file names are just the year they contain data for. The author"
	print "accomplished this by unzipping the archive, deleting the readme, and running:"
	print "    $ rename 's/yob//' * && rename 's/.txt//' *"

# Reading command line input and initializing global variables
nameData={}

# Print usage information and quit if no name input
try:
	name=sys.argv[1]
except:
	printUsage()
	sys.exit()

#Read in command line options or set defaults
try:
	startYear=int(sys.argv[3])
except:
	startYear=1880
try:
	endYear=int(sys.argv[4])
except:
	endYear=2018
try:
	outputType=sys.argv[2]
except:
	outputType="d"

###### MAIN FUNCTION ######
def main ():
	print "US Baby name statistics for the name %s from %d through %d" % (name,startYear,endYear)
	gatherNameStatistics() #Read data into nameData Dictionary

	#Select output mode
	if outputType == "d":
		outputDecades()
	elif outputType== "y":
		outputAnnual()
	else: # print usage and quit if output mode is invalid
		printUsage()
		sys.exit()

#Read in Social Security Administration name data CSV files and create a dictionary of dictionaries 
def gatherNameStatistics():
	#Read in data files. Each year's data is in a separate file named according to its year. Every name that was given to at least
	#five babies who were assigned the same sex will have an entry in the following format:
	#     Name,[M/F],Number\r\n
	for year in os.listdir(os.getcwd()+"/data"):
		f=open("./data/" + year, "r")
		lines=f.readlines()
		for line in lines:
			# Split CSV to lists
			lineList=line.split(",")	
			# If we are looking at a line for the name that was inputted, try to update the dictionary for that year with a subdictionary entry in the format Sex:Number.
			# If there is not already an entry for that year, it will raise an exception, in which case, create the subdictionary. Strip the newline data off and typecast
			# data appropriately in the process.
			if lineList[0] == name:
				try:
					nameData[int(year)].update({lineList[1]:int(lineList[2].rstrip("\r\n"))})
				except:
					nameData[int(year)]={lineList[1]:int(lineList[2].rstrip("\r\n"))}
		f.close()

def outputDecades():
	#Initialize local variables to avoid exceptions in cases when the name does not appear
	boys,girls,boyTotal,girlTotal,decadeBoys,decadeGirls=(0,)*6

	# The bases for our tabular output
	print "Timeframe               Girls             Boys"

	# Set our initial working year
	year=startYear

	# If we are starting with a partial decade, handle that time period separately
	if (year % 10) or (endYear-startYear < 9):
		# Add this year's babies into our running total until we enter a new decade or get to the last year.
		while (decade (year) < decade(startYear+10)) and (year <= endYear):
			decadeBoys,decadeGirls=addYear(year,decadeBoys,decadeGirls)
			year +=1

		# Calculate the blank space necessary to make our tables pretty
		boySpace=" " * (15-len(str(boys)))
		girlSpace=" " * (18-len(str(girls)))
		print "%d-%d%s%d%s%d " % (startYear,year-1,girlSpace,decadeGirls,boySpace,decadeBoys)

		# Add current decade to totals and reinitialize decade counter
		boyTotal,girlTotal=decadeBoys,decadeGirls	
		decadeBoys, decadeGirls=0,0

	# If we've already finished, don't bother with printing totals or anything else. We're done. 
	if year > endYear:
		return

	thisDecade=decade(year)
	while year <= endYear:
		# When we enter a new decade, print the last decade's stats, add them to the running totals, and reinitialize for the new decade.
		if thisDecade != decade(year):
			boySpace=" " * (17-len(str(decadeBoys)))
			girlSpace=" " * (24-len(str(decadeGirls)))
			print "%ds%s%d%s%d" % (decade(year-1),girlSpace,decadeGirls,boySpace,decadeBoys)
			boyTotal += decadeBoys
			girlTotal += decadeGirls			
			thisDecade = decade(year)
			decadeBoys,decadeGirls=0,0
		decadeBoys,decadeGirls=addYear(year,decadeBoys,decadeGirls)
		year +=1

	#Add the final decade we're working with to the total
	boyTotal += decadeBoys
	girlTotal += decadeGirls			
			

	#If we finished at the end of a decade, print the decade as a whole. Otherwise break out the years. 
	if endYear % 10 == 9:
		boySpace=" " * (17-len(str(decadeBoys)))
		girlSpace=" " * (24-len(str(decadeGirls)))
		print "%ds%s%d%s%d" % (decade(year-1),girlSpace,decadeGirls,boySpace,decadeBoys)
	else:
		boySpace=" " * (15-len(str(boys)))
		girlSpace=" " * (19-len(str(girls)))
		print "%d-%d%s%d%s%d " % (decade(year),year-1,girlSpace,decadeGirls,boySpace,decadeBoys)
		
	#Print the totals
	boySpace=" " * (17-len(str(boyTotal)))
	girlSpace=" " * (24-len(str(girlTotal)))
	print ("Total%s%d%s%d" % (girlSpace,girlTotal,boySpace,boyTotal))

# Separately try to add the girls to the girls total and the boys to the boys total.
def addYear(year,boys=0,girls=0):
	try:		
		boys += nameData[year]["M"]
	except:
		pass
	try:
		girls += nameData[year]["F"]
	except:
		pass
	return (boys,girls)
	
# Subtract the ones digit of the year from the year in order to determine the decade.
def decade(year):
	return year - (year % 10)

def outputAnnual():
	# These variables will be used to add up the total
	boyTotal=0
	girlTotal=0

	# The bases for our tabular output
	print "Year              Girls             Boys"

	#Loop through the years we want data for
	year=startYear
	while year <= endYear:
		# Unpack annual data and add it to the running total.
		boys,girls = addYear(year)
		boyTotal += boys
		girlTotal += girls

		# Calculate the blank space necessary to make our tables pretty
		boySpace=" " * (17-len(str(boys)))
		girlSpace=" " * (19-len(str(girls)))

		print ("%d%s%d%s%d" % (year,girlSpace,girls,boySpace,boys))	# Print a table line! Hooray!
		year += 1 #Avoid infinite loops.

	# This is very similar to what we did above, but for the totals.
	boySpace=" " * (17-len(str(boyTotal)))
	girlSpace=" " * (18-len(str(girlTotal)))
	print ("Total%s%d%s%d" % (girlSpace,girlTotal,boySpace,boyTotal))

main()