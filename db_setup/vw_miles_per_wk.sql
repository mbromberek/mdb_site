--CREATE OR REPLACE VIEW CORE_FITNESS.MILES_PER_WK AS
--Get total miles, total time, and number of runs by week
WITH MILES_BY_WK AS (
  SELECT
    date_trunc('WEEK',WRKT_DT) DT_BY_WK
    , count(1) NBR_RUNS
    --Time data types do not work with sum so convert from time to number of seconds
    , sum(TOT_TM_sec) TOT_TM_SEC
    , sum(DIST_mi) TOT_DIST
  FROM CORE_FITNESS.WRKT
  WHERE WRKT_TYP in ('Running', 'Indoor Running')
  GROUP BY date_trunc('WEEK',WRKT_DT)
)
SELECT curr_wk.dt_by_wk, curr_wk.nbr_runs, curr_wk.tot_dist
  , round(((curr_wk.tot_dist / prev_wk.tot_dist) -1) * 100, 1) dist_delta_pct
  , cmn.SEC_TO_TM_STR(curr_wk.TOT_TM_SEC,'hms') TOT_TM
  , round(((curr_wk.TOT_TM_SEC::decimal / prev_wk.TOT_TM_SEC) -1) * 100, 1) Tm_delta_pct
  , curr_wk.TOT_TM_SEC
FROM MILES_BY_WK CURR_WK
LEFT OUTER JOIN MILES_BY_WK PREV_WK
  ON CURR_WK.dt_by_wk - interval '7 day' = prev_wk.dt_by_wk
ORDER BY curr_wk.DT_BY_WK desc
;
