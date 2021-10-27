import sys
import requests
from time import sleep

REGISTRY = 'http://localhost:5000'
DB_URL = 'dbname=sensors user=proxy host=localhost password=irtlab7lw2'

GEOJSON = {
    "type": "GeometryCollection",
    "geometries":[{
        "type": "Polygon",
        "coordinates":[[
            [-73.960433, 40.8095505],
            [-73.9604169, 40.8095732],
            [-73.9604784, 40.8095997],
            [-73.9604712, 40.8096096],
            [-73.9605286, 40.8096338],
            [-73.9605026, 40.8096694],
            [-73.9607213, 40.8097616],
            [-73.9609257, 40.8098477],
            [-73.9609516, 40.8098123],
            [-73.9610097, 40.8098368],
            [-73.9610172, 40.8098266],
            [-73.9610606, 40.8098446],
            [-73.9610759, 40.8098233],
            [-73.9610327, 40.8098054],
            [-73.9610486, 40.8097836],
            [-73.9610606, 40.8097887],
            [-73.9611311, 40.8096921],
            [-73.9611197, 40.8096873],
            [-73.9611582, 40.8096346],
            [-73.9610994, 40.8096098],
            [-73.9611238, 40.8095765],
            [-73.960699, 40.8093975],
            [-73.9606732, 40.8094328],
            [-73.9606175, 40.8094093],
            [-73.9605793, 40.8094615],
            [-73.9605674, 40.8094564],
            [-73.9605, 40.8095488],
            [-73.9604984, 40.809551],
            [-73.9605103, 40.809556],
            [-73.9604956, 40.8095761],
            [-73.960433, 40.8095505]]]
    }]
}

def publisher(number, port):
    while True:
        try:
            r = requests.post(f'{REGISTRY}/backend', json={
                'url': f'{DB_URL} port={port}',
                'serviceRegion': GEOJSON
            })
        except requests.exceptions.ConnectionError:
            pass
        else:
            if r.status_code == 200:
                break

        sleep(2)

    handle = r.json()['id']   
    print(f'Registered with handle {handle}')

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        pass

    

def main():
    number = int(sys.argv[1])
    port = int(sys.argv[2])
    publisher(number, port)


if __name__ == '__main__':
    main()