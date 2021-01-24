CREATE or replace VIEW core_fitness.gear_usage AS
--Gear_Usage
select gear.name
    ,sum(wrkt.dist_mi) AS tot_dist_mi,
    count(*) AS wrkt_ct,
    cmn.sec_to_tm_str(sum(wrkt.tot_tm_sec)::numeric, 'hms'::character varying) AS tot_tm,
    sum(wrkt.tot_tm_sec) AS tot_tm_sec,
    date_trunc('day'::text, min(wrkt.wrkt_dt)) AS first_wrkt_dt,
    date_trunc('day'::text, max(wrkt.wrkt_dt)) AS last_wrkt_dt
    , gear.type, gear.retired
from core_fitness.gear gear
left join (
  select shoes.name shoe_name, insoles.name insole_name
   , shoes.id shoe_id, insoles.id insole_id
  from core_fitness.gear shoes
  inner join core_fitness.shoe_insole
    on shoe_insole.shoe_id = shoes.id
  inner join (select * from core_fitness.gear where type = 'insole') insoles
    on shoe_insole.insole_id = insoles.id
  where shoes.type = 'shoe'
) shoe_insole_match
  on shoe_insole_match.insole_id = gear.id
left join (select * from core_fitness.wrkt where wrkt.gear IS NOT NULL) wrkt
  on coalesce(shoe_insole_match.shoe_name ,gear.name) = wrkt.gear
GROUP BY gear.name, gear.retired, gear.type
ORDER BY (max(wrkt.wrkt_dt)) DESC, gear.type desc
;
