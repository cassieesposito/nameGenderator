DB_INSTANCE = [
    "portfolio-334101",  # project
    "us-west1",  # region
    "ssa-name-data",  # instance
]

DB_KWARGS = {
    "drivername": "postgresql+pg8000",
    "username": "reader",
    "database": "ssa-name-data",
    "password": "6ioAbqTYrVYRe3",
    "query": {"unix_sock": "/cloudsql/{}/.s.PGSQL.5432".format(":".join(DB_INSTANCE))},
}

NAME_DATA_URL = "https://www.ssa.gov/oact/babynames/names.zip"
DB_TABLE_NAME = "ssa_name_data"
