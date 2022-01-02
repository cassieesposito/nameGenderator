from sqlalchemy import select
import json
import MODELS


def main(request):
    if request.method == "OPTIONS":
        return corsInfo()

    if "name" in request.args:
        return httpGetResponse(request.args.get("name"))

    return 'Error 400: Parameter "name" is required.', 400


def httpGetResponse(name):
    nameData = queryDatabase(str.capitalize(name))
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Content-Type": "application/json",
    }

    return json.dumps(nameData), 200, headers


def queryDatabase(name):
    nameData = {}
    with MODELS.ENGINE.connect() as conn:
        stmt = select(MODELS.TABLE).where(MODELS.TABLE.c.name == name)
        for row in conn.execute(stmt):
            nameData[row.year] = {"female": row.female, "male": row.male}

    return nameData


def corsInfo():
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Max-Age": "3600",
    }
    return "", 204, headers
