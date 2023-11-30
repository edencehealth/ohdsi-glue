SELECT
  source_daimon_id,
  source_id,
  daimon_type,
  table_qualifier,
  priority
FROM
  {ID_schema}.source_daimon
WHERE
  source_id = {source_id};
