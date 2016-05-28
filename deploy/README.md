Qabool Deployment
-----------------

## Required Manual Steps

1. Create database user (password to be added to
   `environments/*/group_vars/qabool/vault.yml`):

        create user qabool with encrypted password 'ai7XhoWBbUbNzX8EqmQDuqjgTI9fZs';

2. Create database owned by database user:

        create database qabool owner qabool;

## Optional Manual Steps

1. Grant read access (`SELECT`) on all tables to `bi` database user while
   connected to the application's database, e.g. `qabool`:

        qabool=# grant select on all tables in schema public to bi;

## TODO

1. Create super user.
2. More comprehensive monitoring of all tiers.
