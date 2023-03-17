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

    # START DEBUGGING WALK #
    # print(filenames)
    filenames = list(walk(mypath))  # type: List[Tuple[str, List[str], List[str]]]
    print(filenames)
    print("\n")
    filenames = []
    for root, dirs, files in walk(mypath):
        for name in files:
            print(name)
            print(path.join(root, name))
            # filenames.append(name)
            filenames.append(path.join(root, name))
    print("filenames\n")
    print(filenames)
    if filenames[0] == './Data/output.csv':
        filenames = filenames[1::2]
    else:
        filenames = filenames[0::2]
    print("no rpb")
    print(filenames)
    # END DEBUGGING WALK #

    # filenames.sort(key=lambda x: int(x[1:-5]))

    first = True

    sensors = [[[] for _ in range(8)] for _ in range(2)]

    chans = [[] for _ in range(8)]
    hum = []
    pres = []
    rain = []
    windspd = []
    winddir = []
    events = []
    dataTime = []  # array to hold the dataStart val from json file
    # duration = []   # array to hold duration val from json file

    for fname in filenames:
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

            tx = np.array(data['bmeBoard']['windSpeed']['values'])
            tx = tx.astype(float)
            tx = [x * (x < 50) for x in tx]
            # windspd.extend(data['bmeBoard']['windSpeed']['values'])
            winddir.extend(data['bmeBoard']['windDirection']['values'])
            # duration.extend(data['duration'])
            dataTime.extend(str(data['dataStart']['unixTime']))  # grab initial startTime
