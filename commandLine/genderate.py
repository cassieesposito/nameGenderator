#!/usr/bin/python3

#####################################################################################
#                                                                                   #
# 	Baby Name Genderator                                                            #
# 	Version 1.1                                                                     #
# 	"Playing with Python 3"                                                         #
#                                                                                   #
#   Future development ideas:                                                       #
#           * Data sanity checking and human readable errors in the case of         #
#             malformed data in ./data                                              #
#           * Script to automatically update with new data from the SSA             #
#             including sanity checking the new data in case of a format change     #
#             or malicious actor.                                                   #
#           * Writing a proper README.md in place of this header.                   #
#           * Learn the csv module by replacing my brute force text processing      #
#                                                                                   #
#   Changelog:                                                                      #
#       1.1:                                                                        #
#           * Implemented command line flags for optional arguments                 #
#           * Updated to use csv module                                             #
#       1.0:                                                                        #
#           * Updated codebase to Python 3.                                         #
#           * Default start and end years are now based on the data available       #
#             instead of hard coding them.                                          #
#           * Removed the need to mass rename files when updating the data set      #
#           * Excluded files whose filenames aren't in line with the schema SSA     #
#             data is released in. This allows the data set to be updated by        #
#             extracting the SSA archive directly to the data folder, as the        #
#             included readme will be ignored. It also prevents crashes caused      #
#             by random files being accidentally added to the data folder.          #
#                                                                                   #
#       0.9:                                                                        #
#           * First release!                                                        #
#                                                                                   #
#####################################################################################

import sys, getopt, os, textwrap, re, csv

# Usage information


###### MAIN FUNCTION ######
def main():
    initialize()

    gatherNameStatistics()  # Read data into nameData Dictionary

    print(
        "US Baby name statistics for the name %s from %d through %d"
        % (name, startYear, endYear)
    )

    # Select output mode
    if outputType == "d":
        outputDecades()
    elif outputType == "y":
        outputAnnual()
    else:  # print usage and quit if output mode is invalid
        printUsage()
        sys.exit()


def initialize():
    # Reading command line input and initializing global variables
    global nameData, name, startYear, endYear, outputType

    # setDefaults
    nameData = {}
    startYear = 0
    endYear = 0
    outputType = 0

    opts, args = getopt.getopt(sys.argv[1:], "yds:e:", ["start-year=", "end-year="])

    if len(args) != 1:
        printUsage()
    else:
        name = args[0]

    for opt, arg in opts:
        if opt == "-y":
            outputType += 1
        if opt == "-d":
            outputType += 10
        if opt in ("-s", "--start-year"):
            startYear = int(arg)
        if opt in ("-e", "--end-year"):
            endYear = int(arg)

    if startYear > endYear:
        printUsage

    if 0 <= outputType <= 1:
        outputType = "y"
    elif outputType == 10:
        outputType = "d"
    else:
        printUsage()


def printUsage():
    B, b = "\033[1m", "\033[0m"
    U, u = "\033[4m", "\033[0m"

    print (os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # print(
    #     textwrap.dedent(
    #         f"""
    #         Outputs gender statistics about US baby names over time based on Social Security
    #         Administration data.

    #         Usage:       ./genderate.py [options] {U}name{u}
    #         {U}name{u}   The name you would like statistical information about. Case sensitive.
    #         {B}-y{b}     Output data on an annual basis. Mutually exclusive with -d
    #         {B}-d{b}     Output data on a decade basis. Mutually exclusive with -y. Default behavior

    #         {B}-s{b} {U}year{u}, {B}--start_year={b}{U}year{u}
    #             The first year you would like data counted. Default: Earliest available year.

    #         {B}-e{b} {U}year{u}, {B}--end_year={b}{U}year{u}
    #             The last year you would like data counted. Default: Latest available year.

    #         This was written primarily for the author's own benefit and the benefit of their growing family.

    #         SSA data can be found at: https://www.ssa.gov/oact/babynames/names.zip
    #         To update, or if you've recieved the script withou accompanying data, unpack the archive to ./data
    #         """
    #     )
    # )
    sys.exit()


def gatherNameStatistics():
    global nameData
    firstYear, lastYear = 9999, 0

    # Read in data files. Each year's data is in a separate file named according to its year. Every name that was given to at least
    # five babies who were assigned the same sex will have an entry in the following format:
    # Name,[M/F],Number\r\n
    dataDir=os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/data/"
    for year in os.listdir(dataDir):
        # Ignore NationalReadMe.pdf and any other files that aren't named appropriately
        dataFileNames = re.compile(r"yob[0-9]{4}\.txt")
        if dataFileNames.match(year):
            with open(dataDir + year, "r", newline="") as f:
                year = int(year.removeprefix("yob").removesuffix(".txt"))

                # Get the first and last years that data is available for
                if year < firstYear:
                    firstYear = year
                if year > lastYear:
                    lastYear = year

                reader = csv.reader(f)
                for line in reader:
                    # If we are looking at a line for the name that was inputted, try to update the dictionary for that year with a subdictionary entry in the format Sex:Number.
                    # If there is not already an entry for that year, it will raise an exception, in which case, create the subdictionary. Strip the newline data off and typecast
                    # data appropriately in the process.
                    if line[0] == name:
                        try:
                            nameData[int(year)].update(
                                {line[1]: int(line[2].rstrip("\r\n"))}
                            )
                        except:
                            nameData[int(year)] = {line[1]: int(line[2].rstrip("\r\n"))}
                f.close()

        # If startYear or endYear is unspecified, set it according to the data that is available
    global startYear, endYear
    if not startYear:
        startYear = firstYear
    if not endYear:
        endYear = lastYear
    return nameData


def outputDecades():
    # Initialize local variables to avoid exceptions in cases when the name does not appear
    boys, girls, boyTotal, girlTotal, decadeBoys, decadeGirls = (0,) * 6

    # The bases for our tabular output
    print("Timeframe               Girls             Boys")

    # Set our initial working year
    year = startYear

    # If we are starting with a partial decade, handle that time period separately
    if (year % 10) or (endYear - startYear < 9):
        # Add this year's babies into our running total until we enter a new decade or get to the last year.
        while (decade(year) < decade(startYear + 10)) and (year <= endYear):
            decadeBoys, decadeGirls = addYear(year, decadeBoys, decadeGirls)
            year += 1

        # Calculate the blank space necessary to make our tables pretty
        boySpace = " " * (15 - len(str(boys)))
        girlSpace = " " * (18 - len(str(girls)))
        print(
            "%d-%d%s%d%s%d "
            % (startYear, year - 1, girlSpace, decadeGirls, boySpace, decadeBoys)
        )

        # Add current decade to totals and reinitialize decade counter
        boyTotal, girlTotal = decadeBoys, decadeGirls
        decadeBoys, decadeGirls = 0, 0

    # If we've already finished, don't bother with printing totals or anything else. We're done.
    if year > endYear:
        return

    thisDecade = decade(year)
    while year <= endYear:
        # When we enter a new decade, print the last decade's stats, add them to the running totals, and reinitialize for the new decade.
        if thisDecade != decade(year):
            boySpace = " " * (17 - len(str(decadeBoys)))
            girlSpace = " " * (24 - len(str(decadeGirls)))
            print(
                "%ds%s%d%s%d"
                % (decade(year - 1), girlSpace, decadeGirls, boySpace, decadeBoys)
            )
            boyTotal += decadeBoys
            girlTotal += decadeGirls
            thisDecade = decade(year)
            decadeBoys, decadeGirls = 0, 0
        decadeBoys, decadeGirls = addYear(year, decadeBoys, decadeGirls)
        year += 1

    # Add the final decade we're working with to the total
    boyTotal += decadeBoys
    girlTotal += decadeGirls

    # If we finished at the end of a decade, print the decade as a whole. Otherwise break out the years.
    if endYear % 10 == 9:
        boySpace = " " * (17 - len(str(decadeBoys)))
        girlSpace = " " * (24 - len(str(decadeGirls)))
        print(
            "%ds%s%d%s%d"
            % (decade(year - 1), girlSpace, decadeGirls, boySpace, decadeBoys)
        )
    else:
        boySpace = " " * (15 - len(str(boys)))
        girlSpace = " " * (19 - len(str(girls)))
        print(
            "%d-%d%s%d%s%d "
            % (decade(year), year - 1, girlSpace, decadeGirls, boySpace, decadeBoys)
        )

    # Print the totals
    boySpace = " " * (17 - len(str(boyTotal)))
    girlSpace = " " * (24 - len(str(girlTotal)))
    print("Total%s%d%s%d" % (girlSpace, girlTotal, boySpace, boyTotal))


# Separately, try to add the girls to the girls total and the boys to the boys total.
def addYear(year, boys=0, girls=0):
    try:
        boys += nameData[year]["M"]
    except:
        pass
    try:
        girls += nameData[year]["F"]
    except:
        pass
    return (boys, girls)


# Subtract the ones digit of the year from the year in order to determine the decade.
def decade(year):
    return year - (year % 10)


def outputAnnual():
    # These variables will be used to add up the total
    boyTotal = 0
    girlTotal = 0

    # The bases for our tabular output
    print("Year              Girls             Boys")

    # Loop through the years we want data for
    year = startYear
    while year <= endYear:
        # Unpack annual data and add it to the running total.
        boys, girls = addYear(year)
        boyTotal += boys
        girlTotal += girls

        # Calculate the blank space necessary to make our tables pretty
        boySpace = " " * (17 - len(str(boys)))
        girlSpace = " " * (19 - len(str(girls)))

        print(
            "%d%s%d%s%d" % (year, girlSpace, girls, boySpace, boys)
        )  # Print a table line! Hooray!
        year += 1

    # This is very similar to what we did above, but for the totals.
    boySpace = " " * (17 - len(str(boyTotal)))
    girlSpace = " " * (18 - len(str(girlTotal)))
    print("Total%s%d%s%d" % (girlSpace, girlTotal, boySpace, boyTotal))


main()
