INSERT INTO {ID_schema}.source_daimon (
  source_daimon_id,
  source_id,
  daimon_type,
  table_qualifier,
  priority)
VALUES (
  NEXTVAL('{ID_schema}.source_daimon_sequence'),
  {source_id},
  {daimon_type},
  {table_qualifier},
  {priority});
