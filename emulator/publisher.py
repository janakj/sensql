import time
import math
import datetime
import json
import re
import sched
import schedule
import paho.mqtt.client as mqtt
from uuid import uuid4
from random import randrange, uniform, choice

MQTT_BROKER = "mqtt.eclipseprojects.io"
CLIENT_NAME = "sensor_1"
latitudes_arr = longitudes_arr = device_id_arr = []  # global arr


def user_inputs():
    num_devices_inp = '-1'
    while True:
        try:
            temp = input("Enter number of devices: ")
            if temp == 'test':
                num_devices_inp = 10000
                num_databases_inp = 10
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
    side_of_square_per_device = round(math.sqrt(area_per_device), 8)
    lat_start = lat_min_temp + side_of_square_per_device / 2
    lon_start = lon_min_temp + side_of_square_per_device / 2
    return lat_start, lon_start, side_of_square_per_device


def get_coordinates(num_devices_calc, lat_min_calc, lat_max_calc, lon_min_calc, lon_max_calc):

    lat_start_temp, lon_start_temp, offset = get_start_coord(num_devices_calc,
                                                 lat_min_calc, lat_max_calc, lon_min_calc, lon_max_calc)
    lat_temp, lon_temp = lat_start_temp, lon_start_temp
    latitudes, longitudes = [], []
    while lon_temp <= lon_max_calc:
        while lat_temp <= lat_max_calc:
            latitudes.append(round(lat_temp, 8))
            longitudes.append(round(lon_temp, 8))
            lat_temp += offset
        lat_temp = lat_start_temp
        lon_temp += offset
    new_num_devices = len(latitudes)
    return latitudes, longitudes, new_num_devices


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
           ([40.81581139, 40.84743417, 40.87905695, 40.81581139, 40.84743417, 40.87905695, 40.81581139, 40.84743417,
                40.87905695], [-74.03418861, -74.03418861, -74.03418861, -74.00256583, -74.00256583, -74.00256583,
                               -73.97094305, -73.97094305, -73.97094305], 9), \
           "Should be ([40.81581139, 40.84743417, 40.87905695, 40.81581139, 40.84743417, 40.87905695, 40.81581139, " \
           "40.84743417, 40.87905695], [-74.03418861, -74.03418861, -74.03418861, -74.00256583, -74.00256583, " \
           "-74.00256583, -73.97094305, -73.97094305, -73.97094305], 9)"


def test_get_rand_uuid():
    temp = str(get_rand_uuid(4)[0])
    assert re.match('\w{8}-\w{4}-\w{4}-\w{4}-\w{12}', temp), "Should match"


def generate_payload(dev_index):
    rand_aqi = int(uniform(20, 30))
    rand_temp = int(uniform(65, 70))
    rand_humidity = int(uniform(65, 75))
    rand_cloudy = choice(['yes', 'no'])
    timestamp = datetime.datetime.now()
    data = {}
    data["deviceId"] = device_id_arr[dev_index]
    data["aqi"] = rand_aqi
    data['temperature'] = rand_temp
    data['humidity'] = rand_humidity
    data['cloudy'] = rand_cloudy
    location = {}
    location["latitude"] = latitudes_arr[dev_index]
    location["longitude"] = longitudes_arr[dev_index]
    data["location"] = location
    data["timestamp"] = timestamp.strftime("%m/%d/%Y, %H:%M:%S")

    return json.dumps(data)  # encode object to JSON


def publish(idx):
    data_out = generate_payload(idx)
    devices_per_db = num_devices // num_dbs
    db_idx = (idx // devices_per_db) + 1
    topic = "morningside_heights/db" + str(db_idx)
    client.publish(topic, data_out)
    print("Just published " + str(data_out) + " to topic " + topic)


# helper function for schedule devices to specify what function to run and frequency
def schedule_helper(freq, idx):
    schedule.every(freq).seconds.do(publish, idx)


# schedule n devices to run at frequency f and random offset from 0 to offset_max
def schedule_devices(n, f, offset_max):
    s = sched.scheduler(time.time, time.sleep)
    dev_idx = 0  # to keep track of current device being scheduled
    for x in range(n):
        rand_offset = uniform(0.0, offset_max)
        s.enter(rand_offset, 1, schedule_helper, argument=(f, dev_idx,))
        dev_idx += 1
    s.run()  # run sched for offset start
    while True:
        schedule.run_pending()  # run schedule for repeated calls


if __name__ == '__main__':
    test_get_start_coord()
    test_get_coordinates()
    test_get_rand_uuid()
    print("Unit tests passed")

    num_devices, num_dbs, lat_min, lat_max, lon_min, lon_max = user_inputs()
    latitudes_arr, longitudes_arr, num_devices = get_coordinates(num_devices, lat_min, lat_max, lon_min, lon_max)
    device_id_arr = get_rand_uuid(num_devices)

    client = mqtt.Client(CLIENT_NAME)
    client.connect(MQTT_BROKER)
    schedule_devices(num_devices, 5, 5.0)

    # See PyCharm help at https://www.jetbrains.com/help/pycharm/
