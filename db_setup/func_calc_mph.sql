create or replace function cmn.calcMPH(dist_mi decimal, tm_sec decimal)
returns decimal
as $$
--calculate miles per hour based on the passed distance and time
SELECT
  round(dist_mi / tm_sec*3600,2)
;
$$ LANGUAGE SQL
