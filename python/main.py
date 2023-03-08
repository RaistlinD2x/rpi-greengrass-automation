import time
import board
import adafruit_dht
import json
import os
import sys
sys.path.append('/home/pi/src/python')
from ssm_param_store import get_parameter
import s3
from write_to_csv import csv_create
from MPU6050 import MPU6050

# Initial the dht device, with data pin connected to:
dhtDevice = adafruit_dht.DHT11(board.D17)

bucket_name, bucket_key = get_parameter()

MAX_RECORDS_PER_FILE = 500
MPU6050_DATA_COLUMNS = ['aX', 'aY', 'aZ', 'gX', 'gY', 'gZ', 'Temp_in_C', 'Time']


# def merge_objects(dict1, dict2):
#     return(dict1.update(dict2))

def main():
    FILE_NUMBER = 0
    mpu = MPU6050(0x68)
    while True:
        try:
            FILE_NUMBER += 1

            data_dict_list = []
            row_counter = 0
            while row_counter < MAX_RECORDS_PER_FILE:
                row_counter += 1
                accel, gyro, temp = mpu.get_all_data()
                sensor_data = {
                    'aX': accel['x'],
                    'aY': accel['y'],
                    'aZ': accel['z'],
                    'gX': gyro['x'],
                    'gY': gyro['y'],
                    'gZ': gyro['z'],
                    'Temp_in_C': temp,
                    'Time': time.time()
                }
                data_dict_list.append(sensor_data)
                print("Data row #{} added to list.".format(row_counter))

            file_name = csv_create(MPU6050_DATA_COLUMNS, data_dict_list, "MPU6050_DATA_{}".format(FILE_NUMBER))

            print("File {} created. Preparing to send to S3.".format(file_name))

            s3.upload_file(file_name, bucket_name, '{}/{}'.format(bucket_key,file_name))

            print("File {} pushed to S3. Will now delete local file.".format(file_name))

            if os.path.exists(file_name):
                os.remove(file_name)

            print("File {} deleted: {}".format(file_name, file_name not in './'))

        except RuntimeError as error:
            # Errors happen fairly often, DHT's are hard to read, just keep going
            print(error.args[0])
            time.sleep(2.0)
            continue
        except Exception as error:
            dhtDevice.exit()
            raise error

if __name__ == "__main__":
    main()