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

    def create_session(self):
        self.Session = sessionmaker(bind=self.engine)

    def insert_data(self, prefix, subnet_mask, asn):
        session = self.Session()
        new_data = PrefixASNMapping(prefix=prefix, subnet_mask=subnet_mask, asn=asn)
        session.add(new_data)
        session.commit()

    def delete_data():
        pass

    def query_data():
        pass

    def _clean_line_data(self, line):
        # remove spaces and add comma between elements
        new_line = re.sub(r"\s+", ",", line.strip())
        new_line = new_line.split(",")
        return new_line

    def load_db(self, file_path):
        bulk_data = []
        fd = open(file_path, "r")
        line = fd.readline()
        while line:
            new_line = self._clean_line_data(line)
            # ignore badly formatted lines
            if len(new_line) > 3:
                continue
            bulk_data.append(
                PrefixASNMapping(
                    prefix=new_line[0], subnet_mask=new_line[1], asn=new_line[2]
                )
            )
            line = fd.readline()

        self.Session.add_all(bulk_data)
        self.Session.commit()


def main():
    raw_file = "routeviews-rv2-20230820-1200.pfx2as"
    db_file = "sqlite:///my_database.db"
    db = MappingDB(db_file)
    # db.create_session()
    # db.load_db(raw_file)


if __name__ == "__main__":
    sys.exit(main())
