import sys
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
import re

Base = declarative_base()


class IPASNMapping(Base):
    __tablename__ = "ip_asn_mapping"

    # id = Column(Integer, primary_key=True)
    addr = Column(String, primary_key=True)
    asn = Column(Integer, nullable=False)
    as_name = Column(String, nullable=False)


class MappingDB:
    def __init__(self, db_file):
        self.engine = create_engine(db_file, echo=False, query_cache_size=0)
        self.table = IPASNMapping()
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def insert_data(self, ip, asn, as_name):
        session = self.Session()
        new_data = IPASNMapping(ip=ip, asn=asn, as_name=as_name)
        session.add(new_data)
        session.commit()

    def delete_data(self, ip):
        ip_mapping = self.query_data(ip)
        if ip_mapping:
            session = self.Session()
            session.delete(ip_mapping)
            session.commit()
            return True
        return False

    def query_data(self, ip):
        session = self.Session()
        result = session.query(IPASNMapping).filter(IPASNMapping.ip == ip)

        if result.count() != 0:
            result = result.first().asn
        else:
            result = None
        session.close()
        return result


def main():
    db_file = "sqlite:///cymru.db"
    db = MappingDB(db_file)


if __name__ == "__main__":
    sys.exit(main())
