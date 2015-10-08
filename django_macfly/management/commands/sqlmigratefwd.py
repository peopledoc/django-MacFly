from django.core.management.base import BaseCommand
from django.db.migrations.loader import MigrationLoader
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.operations import (
    CreateModel,
    AddField,
    DeleteModel,
    RenameModel,
    AlterModelTable,
    AlterUniqueTogether,
    AlterIndexTogether,
    AlterOrderWithRespectTo,
    AlterModelOptions,
    RemoveField,
    AlterField,
    RenameField,
    RunSQL,
    RunPython,
    SeparateDatabaseAndState,
)

# only these operations are allowed
OPS = [
    CreateModel,
    AddField,
    AlterModelOptions,
]

# if a migration contains any of these, the result is commented
DANGEROUS_OPS = (
    DeleteModel,
    RenameModel,
    AlterModelTable,
    AlterUniqueTogether,
    AlterIndexTogether,
    AlterOrderWithRespectTo,
    RemoveField,
    AlterField,
    RenameField,
    RunSQL,
    RunPython,
    SeparateDatabaseAndState,
)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--database', default=DEFAULT_DB_ALIAS,
            help='Nominates a database to create SQL for. Defaults to the '
                 '"default" database.')

    def handle(self, *args, **options):
        #db_name = options["database"]
        p = SQLDiffProducer(DEFAULT_DB_ALIAS)
        for line in p:
            print line
        #print p.apps
        #print p.remaining


class SQLDiffProducer(object):
    def __init__(self, database):
        self.database = database
        self.migrations = {}
        self.load_migrations()
        self.commented = False

    @property
    def conn(self):
        return connections[self.database]

    def format(self, line):
        if line.startswith("--"):
            return line
        if not line.endswith(";"):
            line += ";"
        if self.commented :
            line = "-- " + line
        return line

    def __iter__(self):
        l = MigrationLoader(self.conn)
        for app, migrations in self.migrations.iteritems():
            yield "-- Application: " + app
            migrations.sort()
            for name in migrations:
                yield "-- Migration: " + name
                state = l.project_state((app, name), at_end=False)
                mig = l.graph.nodes[(app, name)]
                self.commented = False
                if not len(mig.operations):
                    yield "-- Blank migration"
                    yield """INSERT INTO "django_migrations" ("app", "name", "applied") VALUES ('{}', '{}', now());""".format(app, name)
                    yield ""
                    continue
                for op in mig.operations:
                    # reject mutating changes
                    if op.__class__ in DANGEROUS_OPS:
                        yield "-- DANGEROUS OPERATION FOUND. : {}".format(
                            op.__class__.__name__
                        )
                        self.commented = True
                        break
                try:
                    se = self.conn.schema_editor(collect_sql=True)
                    se.deferred_sql = []
                    # Hack!!! do not drop default on column creation
                    se.skip_default = lambda x: True
                    mig.apply(state, se, collect_sql=True)
                    lines = se.collected_sql + se.deferred_sql
                except:
                    yield "-- GOT AN EXCEPTION!"
                else:
                    if not lines:
                        yield "-- NO SQL MIGRATION HERE"
                        self.commented = True
                    for line in lines:
                        yield self.format(line)
                        yield ""
                    yield self.format("""INSERT INTO "django_migrations" ("app", "name", "applied") VALUES ('{}', '{}', now());""".format(app, name))
                yield ""

    def load_migrations(self):
        l = MigrationLoader(self.conn)
        disk_migrations = set(l.disk_migrations.keys())
        applied = l.applied_migrations
        # DEBUG selector
        # applied = set([m for m in applied if not "initial" in m[1]])
        diff = disk_migrations.difference(applied)
        for k, v in diff:
            remains = self.migrations.setdefault(k, list())
            remains.append(v)
