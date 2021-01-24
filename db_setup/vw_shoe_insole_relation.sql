create view core_fitness.shoe_insole_relation as
--Shoe Insole relation
select shoes.name shoe_name, insoles.name insole_name
  , case when shoes.retired or insoles.retired then True else False end retired
  , shoes.prchse_dt shoe_prchse_dt, insoles.prchse_dt insole_prchse_dt
  , shoes.id shoe_id, insoles.id insole_id
  , shoe_insole.adjust_miles, shoe_insole.link_strt_dt
from
core_fitness.gear shoes
left join core_fitness.shoe_insole
  on shoe_insole.shoe_id = shoes.id
left join (select * from core_fitness.gear where type = 'insole') insoles
  on shoe_insole.insole_id = insoles.id
where shoes.type = 'shoe'
order by shoes.prchse_dt asc
;
