import sys
import json
from datetime import datetime

print(str(sys.argv[1]) + " " + str(sys.argv[2]))
uploadTime = datetime.fromtimestamp(int(sys.argv[1]))
radiometerID = sys.argv[2]

with open('./frontend/radiometer_info.json', 'r+') as f:
    json_file = json.load(f)
    for rad in json_file['radiometers']:
        if rad['id'] == radiometerID:
                
            rad["lastupload"] = str(uploadTime)
            f.seek(0)
            json.dump(json_file, f, indent=2)
            f.truncate()

f.close()
print("Closing radiometer_data.json")
