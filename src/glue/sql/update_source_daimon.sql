UPDATE
  {ID_schema}.source_daimon
SET
  daimon_type = {daimon_type},
  table_qualifier = {table_qualifier},
  priority = {priority}
WHERE
  source_daimon_id = {source_daimon_id};
