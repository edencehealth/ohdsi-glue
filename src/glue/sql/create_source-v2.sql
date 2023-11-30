INSERT INTO {ID_schema}.source (
  source_id,
  source_name,
  source_key,
  source_connection,
  source_dialect,
  is_cache_enabled)
VALUES (
  NEXTVAL('{ID_schema}.source_sequence'),
  {source_name},
  {source_key},
  {source_connection},
  {source_dialect},
  {is_cache_enabled});
