import json
import paho.mqtt.client as mqtt
from database_services.functions import MyDB
import argparse

MQTT_BROKER = "localhost"

def process_cli_arguments():
    parser = argparse.ArgumentParser(description='parse db_id and db_cs')
    parser.add_argument('db_id', type=int,
            help='A required integer positional argumenti db_id')
    parser.add_argument('db_cs', type=str,
            help='A required integer positional argument db_cs')
    args = parser.parse_args()
    return args.db_id, args.db_cs


def on_connect(client, userdata, flags, rc):
    client.subscribe("morningside_heights/db/" + str(db_id))


def on_message(client, userdata, message):
    json_dict = json.loads(message.payload)
    uuid = json_dict['deviceId']
    aqi = json_dict['aqi']
    temp = json_dict['temperature']
    humidity = json_dict['humidity']
    cloudy = json_dict['cloudy']
    location_dict = json_dict['location']
    time_data = json_dict['timestamp']
    print( message.payload)
    MyDatabase.insert_row(uuid, aqi, temp, humidity, cloudy, location_dict, time_data)

db_id, db_cs = process_cli_arguments()
MyDatabase = MyDB(db_cs)
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER)
client.loop_forever()
