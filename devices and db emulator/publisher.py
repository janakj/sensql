# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


import paho.mqtt.client as mqtt
from random import randrange, uniform, choice
import time
import math
import datetime
import json
from uuid import uuid4
import re

mqttBroker ="mqtt.eclipseprojects.io"

client = mqtt.Client("sensor_1")
client.connect(mqttBroker)


def user_inputs():
    num_devices_inp = '-1'
    while True:
        try:
            temp = input("Enter number of devices: ")
            if temp == 'test':
                num_devices_inp = 2
                num_databases_inp = 1
                lat_min_inp = 40.802047
                lat_max_inp = 40.817930
                lon_min_inp = -73.970704
                lon_max_inp = -73.956542
                return num_devices_inp, num_databases_inp, lat_min_inp, lat_max_inp, lon_min_inp, lon_max_inp
            num_devices_inp = int(temp)
            num_databases_inp = int(input("Enter number of databases: "))
        except ValueError:
            print("[ERROR] Enter integer")
            continue
        else:
            break
    while True:
        try:
            lat_min_inp = float(input("Enter min lat: "))  # i.e. 40.802047
            lat_max_inp = float(input("Enter max lat: "))  # i.e. 40.817930
            lon_min_inp = float(input("Enter min lon: "))  # i.e. -73.970704
            lon_max_inp = float(input("Enter max lon: "))  # i.e. -73.956542
        except ValueError:
            print("[ERROR] Enter integer/float")
            continue
        else:
            break
    return num_devices_inp, num_databases_inp, lat_min_inp, lat_max_inp, lon_min_inp, lon_max_inp


def get_start_coord(num_devices_temp, lat_min_temp, lat_max_temp, lon_min_temp, lon_max_temp):
    lat_diff = lat_max_temp - lat_min_temp
    lon_diff = lon_max_temp - lon_min_temp
    area = abs(lat_diff * lon_diff)
    area_per_device = area / num_devices_temp
    side_of_square_per_device = round(math.sqrt(area_per_device),2)
    lat_start = lat_min_temp + side_of_square_per_device / 2
    lon_start = lon_min_temp + side_of_square_per_device / 2
    return lat_start, lon_start, side_of_square_per_device


def get_coordinates(num_devices_calc, lat_min_calc, lat_max_calc, lon_min_calc, lon_max_calc):

    lat_start_temp, lon_start_temp, offset = get_start_coord(num_devices_calc,
                                                 lat_min_calc, lat_max_calc, lon_min_calc, lon_max_calc)
    lat_temp, lon_temp = lat_start_temp, lon_start_temp
    latitudes_arr, longitudes_arr = [], []
    while lon_temp <= lon_max_calc:
        while lat_temp <= lat_max_calc:
            latitudes_arr.append(round(lat_temp, 8))
            longitudes_arr.append(round(lon_temp, 8))
            lat_temp += offset
        lat_temp = lat_start_temp
        lon_temp += offset
    return latitudes_arr, longitudes_arr


def get_rand_uuid(n):
    ids_array = []
    for x in range(n):
        unique_id = str(uuid4())
        ids_array.append(unique_id)
    return ids_array


def test_get_start_coord():
    assert get_start_coord(100, 40.8000, 40.9000, -74.0500, -73.9500) == \
           (40.805, -74.045, 0.01), "Should be 40.805, -74.045, 0.01"


def test_get_coordinates():
    assert get_coordinates(10, 40.8000, 40.9000, -74.0500, -73.9500) == \
           ([40.815, 40.845, 40.875, 40.815, 40.845, 40.875, 40.815, 40.845, 40.875],
               [-74.035, -74.035, -74.035, -74.005, -74.005, -74.005, -73.975, -73.975, -73.975]), \
           "Should be ([40.815, 40.845, 40.875, 40.815, 40.845, 40.875, 40.815, 40.845, 40.875], " \
           "[-74.035, -74.035, -74.035, -74.005, -74.005, -74.005, -73.975, -73.975, -73.975])"


def test_get_rand_uuid():
    temp = str(get_rand_uuid(4)[0])
    print(temp)
    assert re.match('\w{8}-\w{4}-\w{4}-\w{4}-\w{12}', temp), "Should match"


if __name__ == '__main__':
    test_get_start_coord()
    test_get_coordinates()
    test_get_rand_uuid()
    print("Unit tests passed")

    num_devices, num_dbs, lat_min, lat_max, lon_min, lon_max = user_inputs()
    latitudes, longitudes = get_coordinates(num_devices, lat_min, lat_max, lon_min, lon_max)
    device_id_arr = get_rand_uuid(num_devices)
    device_idx = 0

    while True:
        randAqi = uniform(20, 30)
        randTemp = uniform(65, 70)
        randHumidity = uniform(65, 75)
        randCloudy = choice(['yes', 'no'])
        timestamp = datetime.datetime.now()

        data = {}
        data["deviceId"] = device_id_arr[device_idx]
        data["aqi"] = randAqi
        data['temperature'] = randTemp
        data['humidity'] = randHumidity
        data['cloudy'] = randCloudy
        location = {}
        location["latitude"] = latitudes[device_idx]
        location["longitude"] = longitudes[device_idx]
        data["location"] = location
        data["timestamp"] = timestamp.strftime("%m/%d/%Y, %H:%M:%S")
        if device_idx+1 < num_devices:
            device_idx += 1
        else:
            device_idx = 0

        data_out = json.dumps(data)  # encode object to JSON

        client.publish("morningside_heights/main_db", data_out)
        print("Just published " + str(data_out) + " to topic morningside_heights/main_db")
        time.sleep(1)

    # See PyCharm help at https://www.jetbrains.com/help/pycharm/
