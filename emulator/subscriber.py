# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


import paho.mqtt.client as mqtt
import time
import json

def on_message(client, userdata, message):
    m_decode = str(message.payload.decode("utf-8"))
    record_list = json.loads(m_decode)  # decode json data
    if type(record_list) == list:
        first_record = record_list[0]
        # get the column names from the first record
        columns = list(first_record.keys())
        print("\ncolumn names:", columns)
    print(record_list)


mqttBroker ="mqtt.eclipseprojects.io"

client = mqtt.Client("Smartphone")
client.connect(mqttBroker)

client.loop_start()

client.subscribe("morningside_heights/main_db")
client.on_message=on_message

time.sleep(30)
client.loop_stop()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
