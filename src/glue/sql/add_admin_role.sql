INSERT INTO {ID_schema}.sec_user_role (
  user_id,
  role_id) (
  SELECT
    id,
    {LIT_admin_role_id}
  FROM
    {ID_schema}.sec_user
  WHERE
    login = {login});
