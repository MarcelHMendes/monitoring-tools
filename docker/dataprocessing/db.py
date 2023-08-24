import sys
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
import re

Base = declarative_base()


class PrefixASNMapping(Base):
    __tablename__ = "prefix_asn_mapping"

    id = Column(Integer, primary_key=True)
    prefix = Column(String, nullable=False)
    subnet_mask = Column(String, nullable=False)
    asn = Column(String, nullable=False)


class MappingDB:
    def __init__(self, db_file):
        self.engine = create_engine(db_file, echo=True)
        self.table = PrefixASNMapping()
        Base.metadata.create_all(self.engine)

    def insert_data(self, prefix, subnet_mask, asn):
        session = sessionmaker(bind=self.engine)
        new_data = PrefixASNMapping(prefix=prefix, subnet_mask=subnet_mask, asn=asn)
        session.add(new_data)
        session.commit()

    def delete_data(self, prefix):
        prefix_mapping = self.query_data(prefix)
        if prefix_mapping:
            session = sessionmaker(bind=self.engine)
            session.delete(prefix_mapping)
            return True
        return False

    def query_data(self, prefix):
        session = sessionmaker(bind=self.engine)
        result = session.query(PrefixASNMapping).filter(
            PrefixASNMapping.prefix == prefix
        )
        return result


def main():
    raw_file = "routeviews-rv2-20230820-1200.pfx2as"
    db_file = "sqlite:///my_database.db"
    db = MappingDB(db_file)


if __name__ == "__main__":
    sys.exit(main())
