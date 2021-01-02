--Get order of fastest long runs for specified distance (12.01) +/- 10%
select row_number() over (order by wrkt.pace_sec) pos
  , wrkt.wrkt_dt, wrkt_tags.tag_val
  , cmn.sec_to_tm_str(wrkt.tot_tm_sec, 'hms') tot_tm
  , wrkt.dist_mi
  , cmn.sec_to_tm_str(wrkt.pace_sec, 'hms') pace
  , wrkt.tot_tm_sec
  , wrkt.pace_sec
from core_fitness.wrkt
inner join core_fitness.wrkt_tags
  on wrkt.wrkt_dt = wrkt_tags.wrkt_dt
  and wrkt.wrkt_typ = wrkt_tags.wrkt_typ
where
  wrkt.wrkt_typ = 'Running'
  and wrkt_tags.tag_typ = 'category'
  and wrkt_tags.tag_val in ('race','long run')
  and wrkt.dist_mi between (12*0.9) and (12*1.1)
order by wrkt.pace_sec asc, wrkt.wrkt_dt desc
;
