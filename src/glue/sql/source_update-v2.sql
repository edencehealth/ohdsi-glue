UPDATE
  {ID_schema}.source
SET
  source_name = {source_name},
  source_connection = {source_connection},
  source_dialect = {source_dialect},
  is_cache_enabled = {is_cache_enabled}
WHERE
  source_key = {source_key};
