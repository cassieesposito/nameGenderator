import base64
from datetime import date
import urllib.request
import re
from zipfile import ZipFile
from io import BytesIO
from deepmerge import always_merger
import sqlalchemy

import CONST
import MODELS


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


def getSSAData(years):
    archive = downloadSSAData()
    return extractData(archive, years)


def downloadSSAData():
    return urllib.request.urlopen(CONST.NAME_DATA_URL)


def extractData(archive, years):
    ssaData = {}
    dataFileNames = re.compile(r"yob[0-9]{4}\.txt")
    with ZipFile(BytesIO(archive.read())) as files:
        for f in files.namelist():
            year = f.removeprefix("yob").removesuffix(".txt")
            if dataFileNames.match(f) and years["start"] <= int(year) <= years["end"]:
                year = int(year)
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
    number = int(line[2].rstrip("\r\n"))

    return {name: {sex: number}}


def record(ssaData):
    engine = sqlalchemy.create_engine(sqlalchemy.engine.URL.create(**CONST.DB_KWARGS))
    with engine.begin() as conn:
        for year in ssaData:
            print(f"Processing {year}")
            allRecords = getRecords(year, ssaData[year])
            for records in allRecords:
                print(f"Inserting {year}")
                conn.execute(buildSQLStatement(records))
    return


def getRecords(year, ssaData):
    allRecords = []
    records = []
    for name in ssaData:
        records.append(
            {
                "name": name,
                "year": year,
                "female": ssaData[name]["female"] if "female" in ssaData[name] else 0,
                "male": ssaData[name]["male"] if "male" in ssaData[name] else 0,
            }
        )
        if len(records) > 5000:
            allRecords.append(records)
            records = []
    if records:
        allRecords.append(records)

    return allRecords


def buildSQLStatement(records):
    statement = sqlalchemy.dialects.postgresql.insert(MODELS.TABLE).values(records)
    doUpdateStatement = statement.on_conflict_do_update(
        index_elements=["name", "year"],
        set_={"female": statement.excluded.female, "male": statement.excluded.male},
    )
    return doUpdateStatement


# if __name__ == "__main__":
#     main({"data": base64.b64encode("1880,1880".encode("utf-8"))}, "")
