#!/usr/bin/env python

# Script to check the files for any
# empty data, indicating a disconnected
# sensor board or BME board.


# Error Definitions:
# 0  - No Errors
# 1  - Sensor Board data invalid, needs maintanence
# 2  - BME Board all data invalid, needs maintenance
# 2A - BME board humidity data invalid
# 2B - BME board pressure data invalid
# 2C - BME board rain data invalid
# 2D - BME board wind speed data invalid
# 2E - BME board wind direction data invalid
# 2F - BME board air temperature data invalid


# Authors: Austin Martinez, Zachary Steigerwald

import datetime
from datetime import date
import re
import os
from os import path
from os import walk
import numpy as np
import json



dataRoot = "./data"

# this function extracts the data from a given day and checks it for errors
def processDay(year, month, day):
    #zero-pad month
    if int(month) < 10:
        month = "0" + month
    if int(day) < 10:
        day = "0" + day

    print("Year: " + year)
    print("Month: " + month)
    print("Day: " + day)

    badChannels = 0
    badHum = 0
    badPres = 0
    badRain = 0
    badWindspd = 0
    badWinddir = 0
    badAirtemp = 0
    found = False
    
    # search through the data directory for the most recent day's data from each radiometer
    radiometers = os.listdir(dataRoot)
    for radiometer in radiometers:
        print(radiometer)

        # extract the radiometerID 
        x = re.search("radiometer([0-9]+([A-Za-z]+[0-9]+)+)", radiometer)
        if x:
            radiometerID = x.group(1)
        # create new empty lists for this radiometer's data
        hourFiles = []
        sensors = [[[] for _ in range(8)] for _ in range(2)]
        internalTemps = [[[] for _ in range(2)] for _ in range(2)]
        hum = []
        pres = []
        rain = []
        windspd = []
        winddir = []
        airTemp = []
        errors = []

        years = os.listdir(dataRoot + "/" + radiometer)
        if year in years:
            # print("|-- " + year)
            months = os.listdir(dataRoot + "/" + radiometer + "/" + year)
            if month in months:
                # print("    |-- " + month)
                days = os.listdir(dataRoot + "/" + radiometer + "/" + year + "/" + month)
                if day in days:
                    # print("       |-- " + day)
                    hours = os.listdir(dataRoot + "/" + radiometer + "/" + year + "/" + month + "/" + day)
                    for hour in hours:
                        match = re.search("\.json$", hour)
                        if match:
                            found = True
                            # print("            |-- " + hour)
                            filePath = dataRoot + "/" + radiometer + "/" + year + "/" + month + "/" + day
                            hourFiles.append(filePath + "/" + hour)

        # if the day's data is found for this radiometer, let's check its files                    
        if found:
            for fidx, fname in enumerate(hourFiles):
                with open(fname, 'r') as dfp:
                    data = json.loads(dfp.read())
                    # loop through the sensor channels and populate data arrays
                    for sidx, sen in enumerate(data['sensors']):
                        if not sen:
                            continue
                        # extract channel values from sensor data
                        ichans = sen['channels']
                        ichans = [x['values'] for x in ichans]
                        for cidx, i in enumerate(ichans):
                            sensors[sidx][cidx].extend(i)
                        # extract values from internal temp data
                        iTemps = sen['internalTemps']
                        iTemps = [x['values'] for x in iTemps]
                        for itidx, it in enumerate(iTemps):
                            internalTemps[sidx][itidx].extend(it)
                    # loop through populated arrays and check if they're empty
                    for sidx, sen in enumerate(data['sensors']):
                        if sidx != 0: # ignore sensor 2 since we never have more than one sensor board connected
                            continue
                        if not sen:
                            continue
                        # extract channel values from sensor data
                        ichans = sen['channels']
                        ichans = [x['values'] for x in ichans]
                        for cidx, i in enumerate(ichans):
                            # check to see if array is full of invalid data (all the data is the same value)
                            if(len(set(sensors[sidx][cidx])) == 1):
                                badChannels = badChannels + 1

                    # get BME data and populate arrays
                    hum.extend(data['bmeBoard']['humidity']['values'])
                    pres.extend(data['bmeBoard']['pressure']['values'])
                    rain.extend(data['bmeBoard']['rain'])
                    windspd.extend(data['bmeBoard']['windSpeed']['values'])
                    airTemp.extend(data['bmeBoard']['airTemperature']['values'])
                    tx = np.array(data['bmeBoard']['windSpeed']['values'])
                    tx = tx.astype(float)
                    tx = [x * (x < 50) for x in tx]
                    winddir.extend(data['bmeBoard']['windDirection']['values'])
                    # check each BME array to see if any are invalid data (all data is the same value)
                    if(len(set(hum)) == 1):
                        badHum = 1
                    if(len(set(pres)) == 1):
                        badPres = 1
                    if(len(set(rain)) == 1):
                        badRain = 1
                    if(len(set(windspd)) == 1):
                        badWindspd = 1
                    if(len(set(winddir)) == 1):
                        badWinddir = 1
                    if(len(set(airTemp)) == 1):
                        badAirtemp = 1

            sensorErr = badChannels
            bmeErr = badHum + badPres + badRain + badWinddir + badWindspd + badAirtemp

            # open the radiometer_info.json file and write the errors to the corresponding radiometer
            with open('./frontend/radiometer_info.json', 'r+') as f:
                json_file = json.load(f)
                for rad in json_file['radiometers']:
                    if rad['id'] == radiometerID:
                        if (sensorErr > 0) or (bmeErr > 0):
                            if sensorErr > 0:
                                msg = "1  - Sensor board data invalid, please check data in S3. Board may be disconnected."
                                print(msg)
                                errors.append(msg)
                            if bmeErr > 0:
                                if bmeErr == 6: # if all BMe data is bad
                                    msg = "2  - BME board data invalid, please check data in S3. Board may be disconnected."
                                    print(msg)
                                    errors.append(msg)
                                else: # otherwise write individual BME sensor errors
                                    if badHum > 0:
                                        msg = "2A - BME board humidity data invalid, please check data in S3. Sensor may be in error."
                                        print(msg)
                                        errors.append(msg) # humidity sensor error
                                    if badPres > 0:
                                        msg = "2B - BME board pressure data invalid, please check data in S3. Sensor may be in error."
                                        print(msg)
                                        errors.append(msg) # pressure sensor error
                                    if badRain > 0:
                                        msg = "2C - BME board rain data invalid, please check data in S3. Sensor may be in error."
                                        print(msg)
                                        errors.append(msg) # rain sensor error
                                    if badWindspd > 0:
                                        msg = "2D - BME board wind speed data invalid, please check data in S3. Sensor may be in error."
                                        print(msg)
                                        errors.append(msg) # wind speed sensor error
                                    if badWinddir > 0:
                                        msg = "2E - BME board wind direction data invalid, please check data in S3. Sensor may be in error."
                                        print(msg)
                                        errors.append(msg) # wind direction sensor error
                                    if badAirtemp > 0:
                                        msg = "2F - BME board air temperature data invalid, please check data in S3. Sensor may be in error."
                                        print(msg)
                                        errors.append(msg) # air temperature sensor error
                        else: 
                            msg = "0  - No errors detected for this radiometer."
                            print(msg)
                            errors.append(msg)
                            
                        rad["errors"] = errors
                        f.seek(0)
                        json.dump(json_file, f, indent=2)
                        f.truncate()

            f.close()
            print("Closing radiometer_data.json")

            # reset the variables
            badChannels = 0
            badHum = 0
            badPres = 0
            badRain = 0
            badWindspd = 0
            badWinddir = 0
            badAirtemp = 0
            found = False


if __name__ == "__main__":
    print("------------------------------")
    today = date.today() - datetime.timedelta(1)
    today_string = str(today).replace("-","_")
    processDay(str(today.year), str(today.month), str(today.day))
    print("------------------------------")
