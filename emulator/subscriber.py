import json
import re
import paho.mqtt.client as mqtt
import multiprocessing
from database_services.functions import MyDB

CLIENT_NAME = "Client"
MQTT_BROKER = "localhost"
my_databases = {}  # initialize database objects storage
data_queues = {}  # store data in queues to process by each worker


def on_message(client, userdata, message):
    json_dict = json.loads(message.payload)
    if message.topic == "morningside_heights/srv":
        db_id = json_dict['db-id']
        action = json_dict['action']
        db_cs = json_dict['db-url']
        print("Data:", message.payload)
        my_databases[db_id] = MyDB(db_cs)  # store database objects
        data_queues[db_id] = multiprocessing.Queue()  # initialize queues for each process
        process = multiprocessing.Process(  # spawn worker for this db
            target=my_databases[db_id].insert_row, args=[data_queues[db_id]])  # insert data from queue
        process.start()
    else:
        db_id = re.search('[0-9]+', message.topic).group(0)
        if db_id in my_databases:
            print("Data:", message.payload)
            data_queues[db_id].put(json_dict)


client = mqtt.Client(CLIENT_NAME)
client.connect(MQTT_BROKER)
client.subscribe("morningside_heights/srv")
client.subscribe("morningside_heights/db/#")
client.on_message = on_message
client.loop_forever()
