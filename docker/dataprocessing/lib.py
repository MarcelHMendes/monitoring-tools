import ipaddress
import pandas as pd
import re
import db

BOGONS = [
    "0.0.0.0/8",  # RFC 1122 'this' network
    "10.0.0.0/8",  # RFC 1918 private space
    "100.64.0.0/10",  # RFC 6598 Carrier grade nat space
    "127.0.0.0/8",  # RFC 1122 localhost
    "169.254.0.0/16",  # RFC 3927 link local
    "172.16.0.0/12",  # RFC 1918 private space
    "192.0.2.0/24",  # RFC 5737 TEST-NET-1
    "192.88.99.0/24",  # RFC 7526 6to4 anycast relay
    "192.168.0.0/16",  # RFC 1918 private space
    "198.18.0.0/15",  # RFC 2544 benchmarking
    "198.51.100.0/24",  # RFC 5737 TEST-NET-2
    "203.0.113.0/24",  # RFC 5737 TEST-NET-3
    "224.0.0.0/4",  # multicast
    "240.0.0.0/4",  # reserved
]

BOGON_PREFIXES = list(ipaddress.IPv4Network(b) for b in BOGONS)


def is_private_ip(ip):
    ip_obj = ipaddress.IPv4Address(ip)
    for pfx in BOGON_PREFIXES:
        if ip_obj in pfx:
            return True
    return False


def load_db(file_path):
    db_file = "sqlite:///my_database.db"
    database = db.MappingDB(db_file)
    database.create_session()

    fd = open("routeviews-rv2-20230820-1200.pfx2as", "r")
    line = fd.readline()
    while line:
        new_line = re.sub(r"\s+", ",", line.strip())
        new_line = new_line.split(",")
        if len(new_line) > 3:
            continue

        database.insert_data(
            prefix=new_line[0], subnet_mask=new_line[1], asn=new_line[2]
        )

    # data_frame = pd.read_csv(file_path)

    # remove whitespaces from dataframe
    # data_frame["prefix"] = data_frame["prefix"].apply(lambda x: str(x))
    # data_frame["subnet_mask"] = data_frame["subnet_mask"].apply(lambda x: str(x))
    # data_frame["asn"] = data_frame["asn"].apply(lambda x: str(x))

    # data_frame["prefix"] = rm_spaces("prefix", data_frame)
    # data_frame["subnet_mask"] = rm_spaces("subnet_mask", data_frame)
    # data_frame["asn"] = rm_spaces("asn", data_frame)

    # for idx, row in df.iterrows():
    #    print(idx, row)


load_db("routeviews-rv2-20230820-1200.pfx2as")
