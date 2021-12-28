import sqlalchemy
import json
from sqlalchemy import text

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


def main(request):
    if "name" in request.args:
        name = request.args.get("name")
    else:
        return "Must supply name argument"

    engine = sqlalchemy.create_engine(sqlalchemy.engine.URL.create(**DB_KWARGS))
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT * FROM ssa_name_data WHERE name='{name}';"))
        nameData = result.all()

    response = {name: {}}
    for year in nameData:
        response[name][year[1]] = {"girls": year[2], "boys": year[3]}

    return json.dumps(response)
