import time
import json
import re
import paho.mqtt.client as mqtt
from database_services.functions import insert_row

CLIENT_NAME = "Client"
MQTT_BROKER = "mqtt.eclipseprojects.io"
db_dict = {}


def on_message(client, userdata, message):
    json_dict = json.loads(message.payload)
    if message.topic == "morningside_heights/srv":
        db_id = json_dict['db-id']
        action = json_dict['action']
        db_cs = json_dict['db-cs']
        db_dict[db_id] = db_cs
        print("Data:", message.payload)
    else:
        db_id = int(re.search('[0-9]+', message.topic).group(0))
        if db_id in db_dict:
            uuid = json_dict['deviceId']
            aqi = json_dict['aqi']
            temp = json_dict['temperature']
            humidity = json_dict['humidity']
            cloudy = json_dict['cloudy']
            location_dict = json_dict['location']
            lat = location_dict['latitude']
            lon = location_dict['longitude']
            loc = str((lat, lon))
            time_data = json_dict['timestamp']
            print("Data:", message.payload)
            insert_row(db_dict[db_id], uuid, aqi, temp, humidity, cloudy, loc, time_data)

client = mqtt.Client(CLIENT_NAME)
client.connect(MQTT_BROKER)
client.subscribe("morningside_heights/srv")
client.subscribe("morningside_heights/db/#")
client.on_message = on_message
client.loop_forever()
