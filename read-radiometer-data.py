import boto3
import pandas as pd
import sys
from datetime import date, timedelta, datetime
import botocore
import matplotlib.pyplot as plt


BUCKET_NAME = 'radiometer-data'

s3_client = boto3.client('s3')
radiometer_name = str(sys.argv[1])
radiometers = ('radiometer0X6185CC28', 'radiometer0XAF77B198', 'radiometer0X1E1BFEE6', 'radiometer0XDCBF5A7F')
if radiometer_name not in radiometers:
     print("Not a valid radiometer")
     exit(1)
#ensure all parameters are passed
n = len(sys.argv)
if n != 8:
    print("Arguments should be: YY MM DD YY MM DD")
    exit()

start_year = sys.argv[2]
start_month = sys.argv[3]
start_day = sys.argv[4]
start_date = date(int(start_year), int(start_month), int(start_day))

end_year = sys.argv[5]
end_month = sys.argv[6]
end_day = sys.argv[7]
end_date = date(int(end_year), int(end_month), int(end_day))

combined_df = pd.DataFrame()
current_date = start_date
missing_files = []
while current_date <= end_date:
    try:
            #pad with 0 to match file naming convention
            if(current_date.month < 10):
                 month_string = '0' + str(current_date.month)
            else:
                 month_string = str(current_date.month)
            
            if(current_date.day < 10):
                 day_string = '0' + str(current_date.day)
            else:
                 day_string = str(current_date.day)

            #create object key
            file_name = str(current_date.year) + '_' + month_string + '_' + day_string + '.csv'
            s3_key = radiometer_name + '/' + str(current_date.year) + '/' + month_string + '/' + day_string + '/' + file_name
            

            #read from s3
            response = s3_client.get_object(Bucket='radiometer-data', Key=s3_key)
            print(s3_key)
            
    except botocore.exceptions.ClientError as e:
          # No file for that day
          missing_files.append(file_name)
    else:
        combined_df = pd.concat([combined_df, pd.read_csv(response.get("Body"))])
    current_date += timedelta(days=1)  # Move to the next day

print(combined_df.head())
date_time = combined_df["Time"].tolist()

timestamps = []
for dt in date_time:
     time_to_convert = datetime.strptime(str(dt),"%Y-%m-%d %H:%M:%S")
     timestamps.append(datetime.timestamp(time_to_convert))
timestamps = [x - timestamps[0] for x in timestamps]

combined_df.insert(1, "Timestamp", timestamps)
#combined_df.to_csv("test_all.csv")
#print(combined_df)
#print(combined_df)

channel_col = []
internal_col = []
nums = [1,2]
channels = ['A', 'B', 'C', 'D']
for num in nums:
     for chan in channels:
          channel_col.append("T" + str(num) + "C" + str(chan))
     internal_col.append("IT" + str(num))

plt.plot(combined_df["Timestamp"], combined_df[channel_col], marker = ".", linestyle='None', markersize = 10.0)
plt.legend(channel_col)
plt.title("Radiometer Channels Raw Data")
plt.ylim([0, 3.4])
plt.ylabel("Voltage (V)")
plt.savefig('radiometer_images/' + str(radiometer_name) + '/' + str(radiometer_name) + '_' + str(start_date) + '_to_' + str(end_date) + '.png', bbox_inches='tight')
    



