# Setup
https://www.codementor.io/@engineerapart/getting-started-with-postgresql-on-mac-osx-are8jcopb
```
brew install postgresql

# Start Postgres
pg_ctl -D /usr/local/var/postgres start
# Start Postgres and set Brew to start it on bootup
pg_ctl -D /usr/local/var/postgres start && brew services start postgresql

# Access postgresql from terminal
% psql postgres
\q # quits

```

##Creating DATABASE
```
mdb=# CREATE DATABASE mdb;
mdb=# \connect mdb #connect to DB mdb
mdb=# CREATE SCHEMA STG;
mdb=# CREATE TABLE STG.EXERCISE (
  WRKT_DT TIMESTAMP,
  WRKT_TYP VARCHAR,
  TOT_TM VARCHAR,
  DIST NUMERIC(5,2),
  PACE VARCHAR,
  NOTES VARCHAR,
  CATEGORY VARCHAR,
  GEAR VARCHAR,
  ELEVATION VARCHAR,
  HR SMALLINT,
  CAL_BURN INT,
  DIST_KM NUMERIC(5,2)
)
;
# See tables in STG schema
mdb=# \dt STG.*

mdb=# select * from STG.EXERCISE;

# Loaded data to STG.EXERCISE using Postico Import of CSV

```

## Create and Load data to LAKE.Exercise
```
CREATE SCHEMA LAKE;
CREATE TABLE LAKE.EXERCISE (
  WRKT_DT TIMESTAMP,
  WRKT_TYP VARCHAR,
  TOT_TM VARCHAR,
  DIST NUMERIC(5,2),
  PACE VARCHAR,
  NOTES VARCHAR,
  CATEGORY VARCHAR,
  GEAR VARCHAR,
  ELEVATION VARCHAR,
  HR SMALLINT,
  CAL_BURN INT,
  DIST_KM NUMERIC(5,2)
)
;
select column_name from information_schema.columns where table_name = 'exercise';

insert into LAKE.exercise
(wrkt_dt, wrkt_typ, tot_tm, dist, pace, notes, category, gear, elevation, hr, cal_burn, dist_km)
(select wrkt_dt, wrkt_typ, tot_tm, dist, pace, notes, category, gear, elevation, hr, cal_burn, dist_km
from STG.exercise
);
commit;
select * from LAKE.exercise;
```

## Create and setup Core schema and tables
```
create schema core_fitness;
create table CORE_FITNESS.WRKT (

)
;
```
