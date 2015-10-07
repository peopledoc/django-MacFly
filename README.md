# django-MacFly – Forward To The Past
Output sql migrations for ahead of time schema changes.

## TL;DR

```sh
pip install django-MacFly
```

```python
INSTALLED_APPS += ['django_macfly']

```

On a develop environment, deploy the old (version N) code and run migrations.
Then, deploy the new code (version N+1) without running the migrations.

Then run:


```sh
python manage.py sqlmigratefwd
```

Read the result, think, hack, do.

## Rationale

Here, at Peopledoc we found that:

- ZDD is great. We need to achieve at least "Almost Zero Downtime Deployments"
- ZDD is (quite) easy except when there are SQL Database schema migrations.
- Django migration system is useless in ZDD context, especially for large databases.

Our strategy for schema migration is to run migrations ahead of time, the database
is migrated to schema N+1 while the code is at N.

This strategy requires coding discipline (do not rename a DB Column,
do not change a column type...) and we needed a tool that checks the code changes,
warn us if the changes are not ZDD-friendly, and gather all (safe) SQL commands to
make the migration.

### WARNING

This is NOT AT ALL an automatic migration tool. It's just a (dumb) HELPER. It
outputs hints that you MUST read and understand. Your ahead-of-time migration
will probably need DB triggers, query re-writing, default values and all sort
of DBA voodoo stuff to work properly. MacFly DO NOT handle this. Candide use
may eat your data and voids even the no-warranty-of-any-kind clause.

## What it does

Basically it walks through pending migration (using django migrate internals).

For each migration:

- Check migration safety
  - if it's unsafe, MacFly writes commented sql and issues a warning
    It's your responsabilty to interpret the issue reading SQL and the migration script
  - it it's safe, MacFly prints a modified version of `sqlmigrate`:
    - `sqlmigrate` remove default values for `NOT NULL` columns. Here we need a SQL default
      because the code doesn't know the column, and inserts would fail. Hence, `sqlmigratefwd`
      doesn't drop defaults
    - `sqlmigratefwd` also issues a faked migration (an insert in `django_migration` table).
      So it's safe at deploy time to run `migrate`
