SELECT
    login,
    sec_user.id AS user_id,
    sec_role.name AS role_name,
    sec_role.id AS role_id
FROM
    {ID_schema}.sec_user
    JOIN {ID_schema}.sec_user_role
        ON {ID_schema}.sec_user.id = {ID_schema}.sec_user_role.user_id
    JOIN {ID_schema}.sec_role
        ON {ID_schema}.sec_user_role.role_id = {ID_schema}.sec_role.id;
