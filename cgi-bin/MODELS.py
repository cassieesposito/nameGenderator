import CONST

from sqlalchemy import (
    engine,
    create_engine,
    Table,
    MetaData,
    Column,
    String,
    SmallInteger,
    Integer,
)

ENGINE = create_engine(engine.URL.create(**CONST.DB_KWARGS))

TABLE = Table(
    CONST.DB_TABLE_NAME,
    MetaData(),
    Column("name", String(30), primary_key=True),
    Column("year", SmallInteger, primary_key=True),
    Column("female", Integer),
    Column("male", Integer),
)
