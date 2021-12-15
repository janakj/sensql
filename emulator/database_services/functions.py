#!/usr/bin/python
import psycopg2
import json


class MyDB(object):

    def __init__(self, cs):
        self._db_connection = psycopg2.connect(cs)
        self._db_cur = self._db_connection.cursor()

    def insert_row(self, queue):
        json_dict = queue.get()
        uuid = json_dict['deviceId']
        aqi = json_dict['aqi']
        temp = json_dict['temperature']
        humidity = json_dict['humidity']
        cloudy = json_dict['cloudy']
        location_dict = json_dict['location']
        time_data = json_dict['timestamp']

        """ insert a new vendor into the vendors table """
        sql = """INSERT INTO measurements(timestamp, type, device, data, center)
                    VALUES(%s,%s,%s,%s,St_GeomFromGeoJSON(%s));"""
        # execute the INSERT statement
        data = json.dumps({"aqi": aqi,
                           "temperature": temp,
                           "humidity": humidity,
                           "cloudy": cloudy
                           })
        self._db_cur.execute(sql, (time_data, "emulated", uuid, data, json.dumps({
            "type": "Point",
            "coordinates": [location_dict["longitude"], location_dict["latitude"]]
        })))
        # commit the changes to the database
        self._db_connection.commit()

#    def __del__(self):
#        self._db_connection.close()
