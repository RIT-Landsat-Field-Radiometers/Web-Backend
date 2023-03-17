import datetime
from datetime import date
import re
import os
from os import path
import pathlib
import logging
import shutil
import boto3
from botocore.exceptions import ClientError
import data2csv

dataRoot = "./data"

def processDay(year, month, day, final_filename):
    #zero-pad month
    if int(month) < 10:
        month = "0" + month

    if int(day) < 10:
        day = "0" + day

    print("Year: " + year)
    print("Month: " + month)
    print("Day: " + day)

    found = False
    radiometers = os.listdir(dataRoot)
    for radiometer in radiometers:
        print(radiometer)
        years = os.listdir(dataRoot + "/" + radiometer)
        if year in years:
            print("|-- " + year)
            months = os.listdir(dataRoot + "/" + radiometer + "/" + year)
            if month in months:
                print("    |-- " + month)
                days = os.listdir(dataRoot + "/" + radiometer + "/" + year + "/" + month)
                if day in days:
                    print("       |-- " + day)
                    hours = os.listdir(dataRoot + "/" + radiometer + "/" + year + "/" + month + "/" + day)
                    for hour in hours:
                        match = re.search("\.json$", hour)
                        if match:
                            found = True
                            print("            |-- " + hour)
                            original_loc = str(dataRoot + "/" + radiometer + "/" + year + "/" + month + "/" + day + "/" + hour)
                            target_loc = "./json_daily/" + hour
                            shutil.copyfile(original_loc, target_loc)
        if found:
            os.system("python3 data2csv.py json_daily/")
            os.rename("./output.csv", ("./" + final_filename))
            shutil.rmtree("./json_daily/")
            os.makedirs("./json_daily")

            s3 = boto3.client('s3')
            bucket_name = "radiometer-data"
            object_name = radiometer + "/" + year + "/" + month + "/" + day + "/" + final_filename
            s3.upload_file(final_filename, bucket_name, object_name)

            os.remove("./" + final_filename)

            found = False

if __name__ == "__main__":
    print("------------------------------")
    print("------------------------------")
    year = input("Enter year: ")
    month = input("Enter month: ")
    day = input("Enter day: ")
    today_string = str(year) + "_" + str(month) + "_" + str(day)
    final_filename = today_string + ".csv"
    print("Today's file: " + str(final_filename))
    processDay(str(year), str(month), str(day), final_filename)
    print("------------------------------")
    print("------------------------------")
