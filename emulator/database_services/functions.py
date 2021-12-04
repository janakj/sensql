#!/usr/bin/python
import psycopg2
import json

def insert_row(cs, uuid, aqi, temp, humidity, cloudy, loc_dict, time_data):
    """ insert a new vendor into the vendors table """
    sql = """INSERT INTO measurements(timestamp, type, device, data, center)
                VALUES(%s,%s,%s,%s,St_GeomFromGeoJSON(%s));"""
    conn = None
    try:
        # read database configuration
        # connect to the PostgreSQL database
        conn = psycopg2.connect(cs)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        data = json.dumps({"aqi": aqi,
                "temperature": temp,
                "humidity": humidity,
                "cloudy": cloudy
                })
        cur.execute(sql, (time_data, "emulated", uuid, data, json.dumps({
            "type": "Point",
            "coordinates": [loc_dict["longitude"], loc_dict["latitude"]]
        })))
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
