Schema
======

- The postgresql database stores instance information in a ``instances_table`` table. This is the data you can see here: https://mnm.social/. The model code matching this table may be found here: https://github.com/EliotBerriot/mnm/blob/master/mnm/instances/models.py#L17
- Every day, for each instance, we fetch latest data, update this table, and sends a copy of the information to an InfluxDB database. This one is responsible to store historical data and enable the visualizations you can see in https://dashboards.mnm.social/

Dumps
-----

Dumps are available at https://mnm.social/dumps/ and made of two parts:

- A postgres (9.6) dump
- An influxdb (1.5) dump

Postgres data
-------------

To restore, download the dump file, ensure you have a postgres 9.6 database available, and import the dump with:

```
pg_restore -d yourlocaldatabase < postgres.dump
```

Then you can run queries on the database:

```
psql -d yourlocaldatabase
SELECT name, users from instances_instance ORDER BY name LIMIT 10 
```

Influxdb data
-------------

To restore, download the dump file, ensure you have an influxd server at version 1.5, and execute the following commands:

```
# the backup is made of a lof of small gzip files, so we untar those
tar xvf influxdb-mnm.backup.tar
influxd restore -portable influxdb-mnm.backup
```

Then you can run queries on this database:

```
influx -precision rfc3339
use mnm;
SHOW MEASUREMENTS;
# hourly evolution of statuses on instance pawoo.net
SELECT mean("statuses") FROM "instances_daily" WHERE ("name" = 'pawoo.net') AND time >= now() - 7d GROUP BY time(1h) fill(null);
# daily evolution of users on the whole network
SELECT sum("users") FROM "instances_daily" WHERE time >= now() - 60d GROUP BY time(1d) fill(null);

```

Refer to https://docs.influxdata.com/influxdb/v1.5/query_language/data_exploration/ and https://docs.influxdata.com/influxdb/v1.5/query_language/schema_exploration/ for details about Influx query language.
