create or replace view core_fitness.gear_usage as
select
  gear
  , sum(dist_mi) tot_dist_mi
  , count(*) wrkt_ct
  , CMN.SEC_TO_TM_STR(sum(tot_tm_sec), 'hms') tot_tm
  , sum(tot_tm_sec) tot_tm_sec
  , min(wrkt_dt) first_wrkt_dt
  , max(wrkt_dt) last_wrkt_dt
from core_fitness.wrkt
where gear is not null
group by gear
order by max(wrkt_dt) desc
;
