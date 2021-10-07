#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  create user registry with password 'ikebana';
  create database registry;
  grant all privileges on database registry to registry;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "registry" <<-EOSQL
  create extension postgis;
  create extension "uuid-ossp";

  create table nodes (
    id             serial   primary key,
    url            text     not null,
    service_region geometry
  );

  grant all privileges on table nodes to registry;
  grant usage, select on sequence nodes_id_seq to registry;

  create index node_idx on nodes using gist(service_region);
EOSQL
