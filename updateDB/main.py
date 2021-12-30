from zipfile import ZipFile
from io import BytesIO
import urllib.request
import sqlalchemy
import re
import base64
from datetime import date
from textwrap import dedent
from deepmerge import always_merger
from sqlalchemy.sql.expression import except_

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
DB_TABLE = "ssa_name_data"


def main(event, context):
    years = getYearsToInsert(event)
    ssaData = getSSAData(years)
    record(ssaData)
    return


def getYearsToInsert(event):
    message = base64.b64decode(event["data"]).decode("utf-8").split(",")
    years = {"end": float("inf")}
    years["start"] = int(message[0]) if message[0].isdigit() else date.today().year - 3
    if len(message) > 1:
        years["end"] = int(message[1]) if message[1].isdigit() else float("inf")
    return years


def record(ssaData):
    engine = sqlalchemy.create_engine(sqlalchemy.engine.URL.create(**DB_KWARGS))
    with engine.begin() as conn:
        for year in ssaData:
            print(f"Inserting {year}")
            conn.execute(sqlalchemy.text(buildQuery(year, ssaData[year])))
    return


def getSSAData(years):
    archive = downloadSSAData()
    return extractData(archive, years)


def downloadSSAData():
    return urllib.request.urlopen(NAME_DATA_URL)


def extractData(archive, years):
    ssaData = {}
    dataFileNames = re.compile(r"yob[0-9]{4}\.txt")
    with ZipFile(BytesIO(archive.read())) as files:
        for f in files.namelist():
            year = f.removeprefix("yob").removesuffix(".txt")
            if dataFileNames.match(f) and years["start"] <= int(year) <= years["end"]:
                ssaData[year] = {}
                for line in files.open(f).readlines():
                    always_merger.merge(ssaData[year], parseLine(line))
    return ssaData


def parseLine(line):
    # Incoming format is b'Name,[M/F],#\r\n'
    line = line.decode("utf-8").split(",")

    name = line[0]
    sex = {"F": "female", "M": "male"}
    sex = sex[line[1]]
    number = line[2].rstrip("\r\n")

    return {name: {sex: number}}


def buildQuery(year, ssaData):
    values = ""
    for name in ssaData:
        female = ssaData[name]["female"] if "female" in ssaData[name] else 0
        male = ssaData[name]["male"] if "male" in ssaData[name] else 0
        values += f"('{name}',{year},{female},{male}), "
    values = values.removesuffix(", ")

    if ";" in values:
        raise Exception(
            f"Possible SQL injection attack detected: character ; exists in source data."
            + f" Please verify {NAME_DATA_URL} points to a trusted data source."
        )

    return dedent(
        f"""
		INSERT INTO {DB_TABLE}
		(name, year, female, male)
		VALUES {values}
		ON CONFLICT (name, year) DO
		UPDATE SET female = EXCLUDED.female, male = EXCLUDED.male;
		"""
    )


# if __name__ == "__main__":
#     main({"data": base64.b64encode("".encode("utf-8"))}, "")
