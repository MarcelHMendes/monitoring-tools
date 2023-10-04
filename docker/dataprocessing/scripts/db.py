import sys
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class IPASNMapping(Base):
    __tablename__ = "ip_asn_mapping"

    asn = Column(Integer, nullable=True)
    addr = Column(String, primary_key=True)
    as_name = Column(String, nullable=True)


class MappingDB:
    def __init__(self, db_file):
        self.engine = create_engine(db_file, echo=True)
        self.table = IPASNMapping()
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)


def main():
    db_file = "sqlite:///cymru.db"
    db = MappingDB(db_file)


if __name__ == "__main__":
    sys.exit(main())
