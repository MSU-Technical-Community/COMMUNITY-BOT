import os

from dotenv import load_dotenv
from peewee import SqliteDatabase
from playhouse.migrate import SqliteMigrator

load_dotenv()
db_name = os.getenv("db_name")

db = SqliteDatabase(db_name)
migrator = SqliteMigrator(db)


def run_migrations(migrations):
    with db.transaction():
        migrator.run(migrations)
