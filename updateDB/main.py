from zipfile import ZipFile
from io import BytesIO
import urllib.request
import sqlalchemy
import re
import textwrap

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
    archive = ZipFile(BytesIO(response.read()))

    engine = sqlalchemy.create_engine(sqlalchemy.engine.URL.create(**DB_KWARGS))
    with engine.begin() as conn:
        for decade in range (188, 210):
            result = conn.execute(sqlalchemy.text(f"SELECT * FROM {DB_TABLE}"))
            print(result.all())
            conn.execute(sqlalchemy.text(fQuery))
            conn.execute(sqlalchemy.text(mQuery))

    archive.close()

    fData, mData = getData()
    fQuery = buildQuery("female", fData)
    mQuery = buildQuery("male", mData)



def getData():
    response = urllib.request.urlopen(NAME_DATA_URL)

    with  as zip:
        dataFileNames = re.compile(r"yob[0-9]{4}\.txt")
        mData = fData = ""
        for file in zip.namelist():
            if dataFileNames.match(file):
                year = file.removeprefix("yob").removesuffix(".txt")
                for line in zip.open(file).readlines():
                    data = line.decode("utf-8").split(",")
                    data[2] = data[2].removesuffix("\r\n")
                    if data[1] == "F":
                        fData += f"('{data[0]}',{year},{data[2]}), "
                    if data[1] == "M":
                        mData += f"('{data[0]}',{year},{data[2]}), "

    return fData.removesuffix(", "), mData.removesuffix(", ")


def buildQuery(sex, data):
    return textwrap.dedent(
        f"""
        INSERT INTO {DB_TABLE}
        (name, year, {sex})
        VALUES {data}
        ON CONFLICT (name, year) DO
        UPDATE SET {sex} = EXCLUDED.{sex};
        """
    )


# if __name__ == "__main__":
#     main("", "")
