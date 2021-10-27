#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  create database sensors;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "sensors" <<-EOSQL
  create extension postgis;
  create extension "uuid-ossp";

  create table measurements (
    timestamp timestamptz  not null default now(),
    type      text         not null,
    device    text         not null,
    data      jsonb        not null default '{}'::jsonb,
    center    geometry(Point),
    radius    real
  );

  insert into measurements (type, device, data) values ('zigbee', 'lock-${NODE_NUMBER}', '{"value": "open"}');
EOSQL
