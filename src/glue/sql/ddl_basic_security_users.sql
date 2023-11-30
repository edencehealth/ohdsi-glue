CREATE TABLE {ID_schema}.users (
  username VARCHAR(255) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  firstname VARCHAR(255),
  middlename VARCHAR(255),
  lastname VARCHAR(255),
  PRIMARY KEY (username)
);
