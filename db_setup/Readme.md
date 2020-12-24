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
--Create and Populate CORE tables
create table CORE_FITNESS.WRKT (
  WRKT_DT TIMESTAMP,
  WRKT_TYP VARCHAR,
  TOT_TM_SEC INT,
  DIST_MI NUMERIC(5,2),
  PACE_SEC INT,
  GEAR VARCHAR,
  TEMP_STRT NUMERIC(8,2),
  TEMP_FEELS_LIKE_STRT NUMERIC(8,2),
  WETHR_COND_STRT VARCHAR,
  HMDTY_STRT NUMERIC(8,2),
  WIND_SPEED_STRT NUMERIC(8,2),
  WIND_GUST_STRT NUMERIC(8,2),  
  TEMP_END NUMERIC(8,2),
  TEMP_FEELS_LIKE_END NUMERIC(8,2),
  WETHR_COND_END VARCHAR,
  HMDTY_END NUMERIC(8,2),
  WIND_SPEED_END NUMERIC(8,2),
  WIND_GUST_END NUMERIC(8,2),
  CLOTHES VARCHAR,
  ELE_UP NUMERIC(8,2),
  ELE_DOWN NUMERIC(8,2),
  hr SMALLINT,
  cal_burn INT,
  NOTES VARCHAR,
  PRIMARY KEY (WRKT_DT, WRKT_TYP)
);

create table CORE_FITNESS.WRKT_TAGS (
  WRKT_DT TIMESTAMP,
  WRKT_TYP VARCHAR,
  TAG_TYP VARCHAR,
  TAG_VAL VARCHAR,
  PRIMARY KEY (WRKT_DT, WRKT_TYP, TAG_TYP)
);



```
## Create and setup CMN SCHEMA
```
CREATE SCHEMA CMN;



```
