import re
import sqlalchemy
import json

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
    if request.method == "OPTIONS":
        return corsInfo()

    if "name" in request.args:
        name = str.capitalize(request.args.get("name"))
    else:
        return "Name argument required."

    engine = sqlalchemy.create_engine(sqlalchemy.engine.URL.create(**DB_KWARGS))
    with engine.connect() as conn:
        query = f"SELECT year, female, male FROM ssa_name_data WHERE name='{name}';"
        result = conn.execute(sqlalchemy.text(query)).all()

    nameData = {name: {}}
    for record in result:
        nameData[name][record[0]] = {"girls": record[1], "boys": record[2]}

    headers = {"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"}
    return (json.dumps(nameData), 200, headers)


def corsInfo():
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Max-Age": "3600",
    }
    return ("", 204, headers)
