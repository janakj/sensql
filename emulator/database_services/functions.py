#!/usr/bin/python
import psycopg2
from database_services.config import config


def insert_row(db_name, uuid, aqi, temp, humidity, cloudy, lat, lon, time_data):
    """ insert a new vendor into the vendors table """
    sql = """INSERT INTO data(uuid, aqi, temperature, humidity, cloudy, latitude, longitude, timestamp)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s);"""
    conn = None
    try:
        # read database configuration
        params = config()
        params['database'] = db_name
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql, (uuid, aqi, temp, humidity, cloudy, lat, lon, time_data,))
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def test_connection():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()
        params['database'] = 'db1'

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)

        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


#if __name__ == '__main__':
    # test_connection()
    # insert_row('db1', 'b81ed938-b10c-4af3-9fb2-798a87947e93', 23, 69, 72, 'no', 40.81037089, -73.96627959, '10/27/2021, 14:15:17')
