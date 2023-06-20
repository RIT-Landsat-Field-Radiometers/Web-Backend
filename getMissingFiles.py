#!/usr/bin/env python

# Script to check for missing data files
# If missing files from radiometer, write
# a txt file with the missing paths

# Authors: Austin Martinez

import sys, os, re
import datetime as datetime

from os import walk
from os import path


# find missing hour files
# hour list SHOULD have from hour 0 to hour 23
def find_missing_hours(lst):
    return sorted(set(range(0, 24)) - set(lst))

# find missing day folders
# day list starts at first day found and ends with last day found
    # this means that if nothing has been uploaded since a certain day, 
    # the device is assumed to be powered off
def find_missing_days(lst):
    return sorted(set(range(lst[0], lst[-1])) - set(lst))

def main():
    dataRoot = "./data"

    radiometers = os.listdir(dataRoot)
    # print(radiometers)

    for radiometer in radiometers:
        missingFilePathList = [] # create new missing list for each radiometer
        print(radiometer)
        years = os.listdir(dataRoot + "/" + radiometer)
        # print(years)
        for year in years:
            print("|-- " + year)
            months = os.listdir(dataRoot + "/" + radiometer + "/" + year)
            # print(months)
            for month in months:
                print("    |-- " + month)
                days = os.listdir(dataRoot + "/" + radiometer + "/" + year + "/" + month)
                # print(days)
                presentDayFolders = []  # create these two lists for each month
                missingDayPathList = []
                for day in days:
                    print("       |-- " + day)
                    hours = os.listdir(dataRoot + "/" + radiometer + "/" + year + "/" + month + "/" + day)

                    presentDayFolders.append(int(day))

                    presentHourFiles = []
                    for hour in hours:
                        hourFile = re.search("\.json$", hour)
                        if hourFile:
                            x = hour.split('.')    # extract the hour number
                            hourNum = x[0]
                            Num = hourNum[1:]
                            print("          |-- " + Num)
                            presentHourFiles.append(int(Num))
                    # check present hour files for any missing hours
                    missingHourFiles = find_missing_hours(presentHourFiles)
                    print("Present Files: " + str(presentHourFiles))
                    if missingHourFiles:
                        print("Missing Files: " + str(missingHourFiles))
                        # get the radiometer paths to missing hour files
                        for hour in missingHourFiles:
                            missingFilePath = str("/data/" + year + "/" + str(int(month)) + "/" + str(int(day)) + "/" + year + "_" + str(int(month)) + "_" + str(int(day)) + "_" + str(hour) + ".gz")
                            print(missingFilePath)
                            missingFilePathList.append(missingFilePath)
                    else:
                        print("No missing files")

                print("Days found: " + str(presentDayFolders))
                # check days found list for any missing days
                missingDayFolders = find_missing_days(presentDayFolders)
                if missingDayFolders:
                    print("Missing Days :" + str(missingDayFolders))
                    # add missing day folders to the missing txt file
                    for day in missingDayFolders:
                        missingDayPath = str("/data/" + year + "/" + str(int(month)) + "/" + str(day))
                        missingDayPathList.append(missingDayPath)

        print(missingFilePathList)
        # create a text file with the list of missing hour file paths
        MISSING_HOUR_FILES = open(radiometer + "_missingHours.txt", "w") # overwrite the whole file after each check
        print("Writing to " + radiometer + "_missingHours.txt")
        for file in missingFilePathList:
            MISSING_HOUR_FILES.write(file + "\n")
        MISSING_HOUR_FILES.close()
        print("Closing " + radiometer + "_missingHours.txt")

        # create a text file with the list of missing day folder paths
        MISSING_DAY_FILES = open(radiometer + "_missingDays.txt", "w") # overwrite the whole file after each check
        print("Writing to " + radiometer + "_missingDays.txt")
        for file in missingDayPathList:
            MISSING_DAY_FILES.write(file + "\n")
        MISSING_DAY_FILES.close()
        print("Closing " + radiometer + "_missingDays.txt")

                    


if __name__ == "__main__":
    main()