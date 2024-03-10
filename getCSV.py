# get CSV from S3 bucket

import boto3

def main():
    s3 = boto3.client('s3')
    bucket_name = 'radiometer-data'
    object_name = 'radiometer0X6185CC28/2023/08/24/2023_08_24.csv'
    received_file = s3.get_object(Bucket=bucket_name, Key=object_name)
    print(received_file)
    
    
if __name__ == "__main__":
    main()

