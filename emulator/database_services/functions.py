#!/usr/bin/python
import psycopg2


def insert_row(cs, uuid, aqi, temp, humidity, cloudy, loc, time_data):
    """ insert a new vendor into the vendors table """
    sql = """INSERT INTO data(uuid, aqi, temperature, humidity, cloudy, location, timestamp)
                VALUES(%s,%s,%s,%s,%s,%s,%s);"""
    conn = None
    try:
        # read database configuration
        # connect to the PostgreSQL database
        conn = psycopg2.connect(cs)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql, (uuid, aqi, temp, humidity, cloudy, loc, time_data,))
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
