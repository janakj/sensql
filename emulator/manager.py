import json
import paho.mqtt.client as mqtt
from subprocess import Popen

MQTT_BROKER = "localhost"
children = []

def on_connect(client, userdata, flags, rc):
    client.subscribe("morningside_heights/srv")


def on_message(client, userdata, message):
    json_dict = json.loads(message.payload)
    db_id = json_dict['db-id']
    action = json_dict['action']
    db_cs = json_dict['db-url']
    print("Data:", message.payload)
    command = ["python3", "subscriber.py", db_id, db_cs]
    child = Popen(command)
    children.append(child)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER)
try:
    client.loop_forever()
except KeyboardInterrupt:
    pass

print("Terminating")

for child in children:
    child.terminate()

for child in children:
    child.wait()

print("All terminated...")

