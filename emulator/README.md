# IoT Devices Emulator
IoT Devices Emulator for SenSQL research project
# Description
## Publisher
Publisher script emulates IoT devices and posts data to MQTT topics.
<br><br> User inputs:
<br> - number of devices to emulate
<br> - number of databases to post to
<br> - min and max lat
<br> - min and max lon
<br><br>Payload:
<br> - uuid
<br> - air quality index (aqi), random 20 to 30
<br> - temperature, random 65 to 70
<br> - humidity, random 65 to 75
<br> - cloudy, random yes or no
<br> - location, lat and lon tuple for each device
<br>devices are uniformly distributed in a square bounded by lat and lon set by the user
<br> - timestamp, date and local time
<br><br>Topic:
<br>- /morningside_heights/dbx
where x is db number that goes from 0 to max set by the user
## Subscriber
Topic:
<br>- /morningside_heights/dbx
<br>where x can be any number
<br><br>Databases:
<br>Once a messages is received it is parsed and populated in a database with the same name as the end of the topic, i.e. db1.

# Quickstart
## Database Setup
1. Create PostgreSQL database
2. Create database.ini file and put it in the emulator project folder
<br> For example:
```
[postgresql]
host=localhost
user=postgres
password=admin
```
4. Create a table called ```data```, run the following sql command

```
CREATE TABLE IF NOT EXISTS data (
    n serial PRIMARY KEY,
    uuid VARCHAR ( 36 ) NOT NULL,
    aqi INT,
    temperature INT,
    humidity INT,
    cloudy VARCHAR ( 3 ),
    location point,
    timestamp TIMESTAMPTZ NOT NULL
)
```

5. Create 9 more PostgreSQL databases within the same instance, or change the default database count from 10 to something else.
## Python Setup and Execution
1. Install python packages listed in requirements.txt
2. Run publisher.py
3. For testing purposes, type test when prompted for number of devices
<br>Test inputs are 10000 devices, 1 database, latitude between 40.802047 and 40.817930, longitude between -73.970704 and -73.956542 which are the coordinates for Morningside Heights in New York. To adjust test inputs go to user_inputs function in publisher.py
4. Run subscriber.py
