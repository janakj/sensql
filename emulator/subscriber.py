import time
import json
import re
import paho.mqtt.client as mqtt
from database_services.functions import insert_row

CLIENT_NAME = "Client"
MQTT_BROKER = "mqtt.eclipseprojects.io"


def on_message(client, userdata, message):
    db_name = re.search('db[0-9]+', message.topic).group(0)
    json_dict = json.loads(message.payload)
    uuid = json_dict['deviceId']
    aqi = json_dict['aqi']
    temp = json_dict['temperature']
    humidity = json_dict['humidity']
    cloudy = json_dict['cloudy']
    location_dict = json_dict['location']
    lat = location_dict['latitude']
    lon = location_dict['longitude']
    time_data = json_dict['timestamp']
    print("Data:", message.payload)
    insert_row(db_name, uuid, aqi, temp, humidity, cloudy, lat, lon, time_data)


client = mqtt.Client(CLIENT_NAME)
client.connect(MQTT_BROKER)

client.subscribe("morningside_heights/#")
client.on_message = on_message
client.loop_forever()
