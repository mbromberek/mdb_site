select * from stg.exercise_sheet;
select * from lake.exercise_sheet where wrkt_dt in ('2021-01-08 21:50:45','2021-01-07 03:00:45');
select * from lake.exercise_brkdn where wrkt_dt in ('2021-01-08 21:50:45','2021-01-07 03:00:45');
select * from core_fitness.wrkt where wrkt_dt in ('2021-01-08 21:50:45','2021-01-07 03:00:45');
select * from core_fitness.wrkt_tags where wrkt_dt in ('2021-01-08 21:50:45','2021-01-07 03:00:45');

delete from lake.exercise_sheet where wrkt_dt in ('2021-01-08 21:50:45','2021-01-07 03:00:45');
delete from lake.exercise_brkdn where wrkt_dt in ('2021-01-08 21:50:45','2021-01-07 03:00:45');
delete from core_fitness.wrkt where wrkt_dt in ('2021-01-08 21:50:45','2021-01-07 03:00:45');
delete from core_fitness.wrkt_tags where wrkt_dt in ('2021-01-08 21:50:45','2021-01-07 03:00:45');

delete from stg.exercise_sheet;
select wrkt_dt,cmn.sec_to_tm_str(tot_tm_sec) tot_tm, tot_tm_sec, cmn.sec_to_tm_str(pace_sec) pace, pace_sec
, ele_up, ele_down from core_fitness.wrkt where wrkt_dt in ('2021-01-08 21:50:45','2021-01-07 03:00:45');
