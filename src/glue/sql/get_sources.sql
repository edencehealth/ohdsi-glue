SELECT
  source_id,
  source_name,
  source_key,
  source_connection,
  source_dialect
FROM
  {ID_schema}.source
WHERE
  source_key = {source_key};
