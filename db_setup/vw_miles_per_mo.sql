--CREATE OR REPLACE VIEW CORE_FITNESS.MILES_PER_MO AS
--Get total miles, total time, and number of runs by month
WITH MILES_BY_MO AS (
  SELECT
    date_trunc('month',WRKT_DT) DT_BY_MO
    , count(1) NBR_RUNS
    --Time data types do not work with sum so convert from time to number of seconds
    , sum(TOT_TM_sec) TOT_TM_SEC
    , sum(DIST_mi) TOT_DIST
  FROM CORE_FITNESS.WRKT
  WHERE WRKT_TYP in ('Running', 'Indoor Running')
  GROUP BY date_trunc('month',WRKT_DT)
)
SELECT curr_MO.dt_by_mo, curr_mo.nbr_runs, curr_mo.tot_dist
  , round(((curr_mo.tot_dist / prev_mo.tot_dist) -1) * 100, 1) dist_delta_pct
  , cmn.SEC_TO_TM_STR(curr_mo.TOT_TM_SEC,'hms') TOT_TM
  , round(((curr_mo.TOT_TM_SEC::decimal / prev_mo.TOT_TM_SEC) -1) * 100, 1) Tm_delta_pct
  , curr_mo.TOT_TM_SEC
FROM MILES_BY_MO CURR_MO
LEFT OUTER JOIN MILES_BY_MO PREV_MO
  ON CURR_mo.dt_by_mo - interval '1 month' = prev_mo.dt_by_mo
ORDER BY curr_mo.dt_by_mo desc
;
