#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  create database registry;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "registry" <<-EOSQL
  create extension postgis;
  create extension "uuid-ossp";

  create table node (
    id     serial   primary key,
    url    text     not null,
    region geometry
  );

  create index node_idx on node using gist(region);
EOSQL
