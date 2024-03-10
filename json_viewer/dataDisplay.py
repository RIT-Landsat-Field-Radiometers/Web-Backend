import json
import csv
from os import walk
from os import path

import matplotlib.pyplot as plt
import numpy as np

from datetime import datetime

if __name__ == "__main__":

    mypath = "./Data/"
    filenames = next(walk(mypath), (None, None, []))[2]  # [] if no file

    ## START DEBUGGING WALK ##
    #print(filenames)
    filenames = list(walk(mypath))  # type: List[Tuple[str, List[str], List[str]]]
    print(filenames)
    print("\n")
    filenames = []
    for root, dirs, files in walk(mypath):
        for name in files:
            print(name)
            print(path.join(root, name))
            #filenames.append(name)
            filenames.append(path.join(root, name))
    print("filenames\n")
    print(filenames)
    if filenames[0] == './Data/output.csv':
        filenames = filenames[1::2]
    else:
        filenames = filenames[0::2]
    print("no rpb")
    print(filenames)
    ## END DEBUGGING WALK ##

    #filenames.sort(key=lambda x: int(x[1:-5]))

    first = True

    sensors = [[[] for _ in range(8)] for _ in range(2)]

    chans = [[] for _ in range(8)]
    hum = []
    pres = []
    rain = []
    rainTemp = []   # array to hold current json rain vals for dataTime loops
    windspd = []
    winddir = []
    events = []
    dataTime_extracted = []  # array to hold the dataStart val from json file
    dataTime_offset = []    # array to place the JSON val and add offset to
    dataTime_hr = []    # human readable datetime
    # duration = []   # array to hold duration val from json file

    for fidx, fname in enumerate(filenames):
        # with open(mypath + fname, 'r') as dfp: #original line
        with open(fname, 'r') as dfp:
            data = json.loads(dfp.read())
            print(fname)
            for sidx, sen in enumerate(data['sensors']):
                if not sen:
                    continue
                ichans = sen['channels']
                ichans = [x['values'] for x in ichans]
                for cidx, i in enumerate(ichans):
                    sensors[sidx][cidx].extend(i)
                    # chans[cidx].extend(i)
            tx = np.array(data['bmeBoard']['humidity']['values'])
            tx = tx.astype(float)
            hum.extend(tx)
            # hum.extend(data['bmeBoard']['humidity']['values'])
            pres.extend(data['bmeBoard']['pressure']['values'])
            rain.extend(data['bmeBoard']['rain'])
            rainTemp.extend(data['bmeBoard']['rain'])   # gather rain vals from current json file

            tx = np.array(data['bmeBoard']['windSpeed']['values'])
            tx = tx.astype(float)
            tx = [x * (x < 50) for x in tx]
            # windspd.extend(data['bmeBoard']['windSpeed']['values'])
            winddir.extend(data['bmeBoard']['windDirection']['values'])
            # duration.extend(data['duration'])
            dataTime_extracted.extend([str(data['dataStart']['unixTime'])])  # grab initial startTime
            # print(dataTime)
            for ridx, rainStatus in enumerate(rainTemp):
                dataTime_offset.extend([ str(int(dataTime_extracted[fidx]) + (ridx+1)*1) ])
                # print(dataTime)
            rainTemp = []   # reset rainTemp vals for next json file

    for tidx, timeValue in enumerate(dataTime_offset):
        dataTime_hr.extend([datetime.fromtimestamp(float(dataTime_offset[tidx])).strftime('%Y-%m-%d %H:%M:%S')])




    # writes data into single column test
    # sensorTest = [[[1, 2, 3],
    #                [4, 5, 6],
    #                [7, 8, 9],
    #                [10, 11, 12]],
    #               [[13, 14, 15],
    #                [16, 17, 18],
    #                [19, 20, 21],
    #                [22, 23, 24]]]
    # humTest = [68, 69, 70]
    # presTest = [100, 101, 102]
    # BMEdata = [hum] + [pres] + [rain] + [winddir]
    # data = sensors[0] + sensors[1] + BMEdata[0] + BMEdata[1] + BMEdata[2] + BMEdata[3]

    # getting the time column #

    BMEdata = [[hum], [pres], [rain], [winddir]]
    data = [dataTime_hr] + sensors[0] + sensors[1] + BMEdata[0] + BMEdata[1] + BMEdata[2] + BMEdata[3]
    headerList = ['Time'] + ['C1'] + ['C2'] + ['C3'] + ['C4'] + ['C5'] + ['C6'] + ['C7'] + ['C8'] + ['C9'] + ['C10'] + ['C11'] + \
                 ['C12'] + ['C13'] + ['C14'] + ['C15'] + ['C16'] + ['Humidity'] + ['Pressure'] + ['Rain'] + ['Wind Direction']
    with open("./output.csv", "w", encoding='utf8', newline='') as csvfile:
        hrd = csv.writer(csvfile)
        # hrd.writerow(["C%d" % d for d in range(1, 1 + len(data))])
        hrd.writerow(headerList)
        for r in zip(*data):
            hrd.writerow(r)

    plt.figure(1)
    plt.plot(hum)
    plt.title("Relative Humidity")
    plt.xlabel("Time(s)")
    plt.ylabel("RHUM %")

    plt.figure(2)
    plt.plot(pres)
    plt.title("Atmospheric Pressure")
    plt.xlabel("Time(s)")
    plt.ylabel("Pressure (Pa)")

    plt.figure(3)
    plt.plot(rain)
    plt.title("Rain Detected")
    plt.xlabel("Time(s)")
    plt.ylabel("Yes/No")

    plt.figure(5)
    wfig, (wax1, wax2) = plt.subplots(2, 1)
    wfig.suptitle("Wind Speed/Direction")
    wax1.plot(windspd)
    wax1.set_ylabel("Speed (m/s)")
    wax2.plot(winddir)
    wax2.set_ylabel("Degrees from North")
    wax2.set_xlabel("Time (s)")

    for sidx, sen in enumerate(sensors):
        plt.figure(6 + sidx)
        fig, ax = plt.subplots()
        leg = []
        for idx, c in enumerate(sen):
            # if idx != 4:
            #     continue
            leg.append('chan' + str(idx))
            ax.plot(c)
        ax.legend(leg)
        # ax.legend(['chan' + str(x) for x in range(len(sen))])
        plt.ylabel("Volts")
        plt.title("Sensor" + str(sidx))
        plt.xlabel("Seconds")
    plt.show()


    for idx, i in enumerate(hum):
        if i < 0.0:
            print(str(i) + ", " + str(idx))
        if i > 100.0:
            print(str(i) + ", " + str(idx))
        if np.isnan(i):
            print(str(i) + ", " + str(idx))
        if np.isinf(i):
            print(str(i) + ", " + str(idx))
    pass
