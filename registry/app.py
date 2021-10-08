import json
import psycopg2
from time import sleep
from flask import Flask, jsonify, request, abort

DB_URL = "host=proxy-db user=postgres password=ikebana dbname=registry"

app = Flask(__name__)


def rec2json(v):
    return {
        'id'     : v[0],
        'url'    : v[1],
        'region' : json.loads(v[2]) if v[2] else None}


@app.route("/")
def index():
    return "<p>SenSQL node registry</p>"


@app.route('/node', methods=['POST'])
def register_node():
    data = request.json
    if 'id' in data:
        abort(400)

    if type(data.get('url', None)) is not str:
        abort(400)

    sr = data.get('region', None)
    if type(sr) is not dict and sr is not None:
        abort(400)

    if sr:
        sr = json.dumps(sr)
        val = 'ST_GeomFromGeoJSON(%s)'
    else:
        val = '%s'

    with psycopg2.connect(DB_URL) as db:
        with db.cursor() as c:
            c.execute(f'''
                insert into node
                    (url, region)
                values
                    (%s, {val})
                returning
                    id, url, ST_AsGeoJSON(region)
            ''', (data['url'], sr))
            return jsonify(rec2json(c.fetchone()))


@app.route('/node/<int:id>', methods=['DELETE'])
def unregister_node(id):
    with psycopg2.connect(DB_URL) as db:
        with db.cursor() as cur:
            cur.execute('delete from node where id=%s', (id,))
            cur.commit()
            return '', 204


@app.route('/node', methods=['GET'])
def list_nodes():
    with psycopg2.connect(DB_URL) as db:
        with db.cursor() as cur:
            cur.execute('select id, url, ST_AsGeoJSON(region) from node')
            recs = map(rec2json, cur.fetchall())
            return jsonify(list(recs))


@app.route('/node/<int:id>', methods=['GET'])
def get_node(id):
    with psycopg2.connect(DB_URL) as db:
        with db.cursor() as cur:
            cur.execute('select id, url, ST_AsGeoJSON(region) from node where id=%s', (id,))
            return jsonify(rec2json(cur.fetchone()))


if __name__ == '__main__':
    print('Purging old nodes')

    while True:
        try:
            with psycopg2.connect(DB_URL) as db:
                with db.cursor() as c:
                    c.execute('delete from node')
            break
        except:
            sleep(2)

    app.run(threaded=True)
