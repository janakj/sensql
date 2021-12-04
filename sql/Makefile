db_name := geonaming

schema.sql: .FORCE
	ssh postgres@db pg_dump -Csv $(db_name) > $@

data.sql: .FORCE
	ssh postgres@db pg_dump -av $(db_name) > $@

.PHONY: .FORCE
.FORCE:

schema:: schema.sql
data:: data.sql

