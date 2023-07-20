from peewee import SqliteDatabase
from playhouse.migrate import SqliteMigrator

from config import db_name

db = SqliteDatabase(db_name)
migrator = SqliteMigrator(db)


def run_migrations(migrations):
    with db.transaction():
        migrator.run(migrations)
