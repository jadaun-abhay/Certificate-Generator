from typing import override

import psycopg
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from psycopg import sql


class Command(BaseCommand):
    help = (
        "Creates the database named in DATABASES['default'] on the connected "
        "Postgres server, if it doesn't already exist. Run this before "
        "`migrate` on a fresh server - `migrate` only creates tables inside "
        "an existing database, it can't create the database itself."
    )

    @override
    def handle(self, *args, **options) -> None:
        db_config = settings.DATABASES["default"]

        if "postgresql" not in db_config["ENGINE"]:
            raise CommandError(
                "createdb only supports Postgres; DATABASES['default']['ENGINE'] "
                f"is {db_config['ENGINE']!r}."
            )

        db_name = db_config["NAME"]
        connect_kwargs = {
            # Connect to the always-present `postgres` maintenance database -
            # the target database doesn't exist yet, so we can't connect to
            # it directly.
            "dbname": "postgres",
            "user": db_config.get("USER"),
            "password": db_config.get("PASSWORD"),
            "host": db_config.get("HOST") or "localhost",
            "port": db_config.get("PORT") or 5432,
        }

        self.stdout.write(
            f"Connecting to Postgres at {connect_kwargs['host']}:"
            f"{connect_kwargs['port']} as '{connect_kwargs['user']}'..."
        )

        try:
            # CREATE DATABASE can't run inside a transaction block.
            with psycopg.connect(**connect_kwargs, autocommit=True) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT 1 FROM pg_database WHERE datname = %s", (db_name,)
                    )
                    if cursor.fetchone() is not None:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Database '{db_name}' already exists - nothing to do."
                            )
                        )
                        return

                    cursor.execute(
                        sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name))
                    )
        except psycopg.OperationalError as exc:
            raise CommandError(f"Could not connect to Postgres: {exc}") from exc

        self.stdout.write(self.style.SUCCESS(f"Database '{db_name}' created."))
        self.stdout.write("Next: run `manage.py migrate`.")
