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
mdb=# CREATE TABLE STG.EXERCISE_SHEET (
    wrkt_dt timestamp without time zone,
    wrkt_typ character varying,
    tot_tm character varying,
    dist numeric(5,2),
    pace character varying,
    notes character varying,
    category character varying,
    gear character varying,
    elevation character varying,
    hr smallint,
    cal_burn integer,
    dist_km numeric(5,2),
    insrt_ts timestamp without time zone DEFAULT CURRENT_TIMESTAMP
)
;
# See tables in STG schema
mdb=# \dt STG.*

mdb=# select * from STG.EXERCISE_sheet;

# Loaded data to STG.EXERCISE using Postico Import of CSV

```

## Create and Load data to LAKE.Exercise
```
CREATE SCHEMA LAKE;
CREATE TABLE LAKE.EXERCISE_SHEET (
    wrkt_dt timestamp without time zone PRIMARY KEY UNIQUE,
    wrkt_typ character varying,
    tot_tm character varying,
    dist numeric(5,2),
    pace character varying,
    notes character varying,
    category character varying,
    gear character varying,
    elevation character varying,
    hr smallint,
    cal_burn integer,
    dist_km numeric(5,2),
    insrt_ts timestamp without time zone DEFAULT CURRENT_TIMESTAMP
)
;
select column_name from information_schema.columns where table_name = 'exercise';

insert into LAKE.exercise
(wrkt_dt, wrkt_typ, tot_tm, dist, pace, notes, category, gear, elevation, hr, cal_burn, dist_km)
(select wrkt_dt, wrkt_typ, tot_tm, dist, pace, notes, category, gear, elevation, hr, cal_burn, dist_km
from STG.exercise
);
commit;

CREATE TABLE lake.exercise_brkdn (
    wrkt_dt timestamp without time zone,
    wrkt_typ character varying,
    tot_tm_sec integer,
    dist_mi numeric(5,2),
    pace_sec integer,
    gear character varying,
    temp_strt numeric(8,2),
    temp_feels_like_strt numeric(8,2),
    wethr_cond_strt character varying,
    hmdty_strt numeric(8,2),
    wind_speed_strt numeric(8,2),
    wind_gust_strt numeric(8,2),
    temp_end numeric(8,2),
    temp_feels_like_end numeric(8,2),
    wethr_cond_end character varying,
    hmdty_end numeric(8,2),
    wind_speed_end numeric(8,2),
    wind_gust_end numeric(8,2),
    clothes character varying,
    ele_up numeric(8,2),
    ele_down numeric(8,2),
    hr smallint,
    cal_burn integer,
    notes character varying,
    category character varying,
    insrt_ts timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    warm_up_tot_dist_mi numeric(5,2),
    warm_up_tot_tm_sec integer,
    warm_up_tot_pace_sec integer,
    cool_down_tot_dist_mi numeric(5,2),
    cool_down_tot_tm_sec integer,
    cool_down_tot_pace_sec integer,
    intrvl_tot_dist_mi numeric(5,2),
    intrvl_tot_tm_sec integer,
    intrvl_tot_pace_sec integer,
    intrvl_tot_ele_up numeric(8,2),
    intrvl_tot_ele_down numeric(8,2),
    intrvl_avg_dist_mi numeric(5,2),
    intrvl_avg_tm_sec integer,
    intrvl_avg_pace_sec integer,
    intrvl_avg_ele_up numeric(8,2),
    intrvl_avg_ele_down numeric(8,2),
    CONSTRAINT wrkt_pkey PRIMARY KEY (wrkt_dt, wrkt_typ)
);

CREATE UNIQUE INDEX wrkt_pkey ON lake.exercise_brkdn(wrkt_dt timestamp_ops,wrkt_typ text_ops);

```

## Create and setup Core schema and tables
```
create schema core_fitness;
--Create and Populate CORE tables
create table CORE_FITNESS.WRKT (
    wrkt_dt timestamp without time zone,
    wrkt_typ character varying,
    tot_tm_sec integer,
    dist_mi numeric(5,2),
    pace_sec integer,
    gear character varying,
    temp_strt numeric(8,2),
    temp_feels_like_strt numeric(8,2),
    wethr_cond_strt character varying,
    hmdty_strt numeric(8,2),
    wind_speed_strt numeric(8,2),
    wind_gust_strt numeric(8,2),
    temp_end numeric(8,2),
    temp_feels_like_end numeric(8,2),
    wethr_cond_end character varying,
    hmdty_end numeric(8,2),
    wind_speed_end numeric(8,2),
    wind_gust_end numeric(8,2),
    clothes character varying,
    ele_up numeric(8,2),
    ele_down numeric(8,2),
    hr smallint,
    cal_burn integer,
    notes character varying,
    insrt_ts timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT wrkt_pkey PRIMARY KEY (wrkt_dt, wrkt_typ)
);

create table CORE_FITNESS.WRKT_TAGS (
    wrkt_dt timestamp without time zone,
    wrkt_typ character varying,
    tag_typ character varying,
    tag_val character varying,
    insrt_ts timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT wrkt_tags_pkey PRIMARY KEY (wrkt_dt, wrkt_typ, tag_typ)
);


--Not in use yet
create table CORE_FITNESS.WRKT_BRKDN (
    wrkt_dt timestamp without time zone,
    wrkt_typ character varying,
    brkdn_typ varchar,
    intvl varchar,
    tm_sec integer,
    dist_mi numeric(6,3),
    pace_sec integer,
    mph numberic(6,2),
    avg_hr numeric(5,2),
    ele_up numeric(8,2),
    ele_down numeric(8,2),
    elevation numeric(8,2),
    CONSTRAINT wrkt_pkey PRIMARY KEY (wrkt_dt, wrkt_typ, brkdn_typ, intvl)
};



```
## Create and setup CMN SCHEMA
```
CREATE SCHEMA CMN;
```
## Create and setup apirelease table
```
CREATE TABLE CMN.apirelease (
  buildtime timestamp,
  vers varchar(30) primary key,
  links varchar(30),
  methods varchar(30)
)
;
Insert into cmn.apirelease values ('2020-12-24 11:57:00', 'v1',
   '/api/v1/wrkts', 'get, post, put, delete');
select * from cmn.apirelease;
```
