import json
import db
import os
import argparse
import logging
import ipaddress
import sys


def get_ripe_files_list(dir):
    files = []
    files = os.listdir(dir)
    return files


def ip2asn(DBinstance, traceroute_hops):
    for hop in traceroute_hops:
        result = hop.get("result", None)
        if not result:
            continue
        ip_str = result[0].get("from", None)
        if not ip_str:
            continue
        ipr = DBinstance.query_data(ip_str)

        # ip_addr = ipaddress.IPv4Address(ip_str)
        # ip_net = ipaddress.ip_network(ip_addr)


def create_parser():
    desc = """Convert IP traceroutes to ASN traceroutes"""
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument(
        "--ripedir",
        dest="ripedir",
        action="store",
        required=True,
        help="Directory where ripe files are located",
    )
    parser.add_argument(
        "--db_file",
        dest="db_file",
        action="store",
        required=True,
        help="sqlite3 file db",
    )
    parser.add_argument(
        "--outdir",
        dest="outdir",
        action="store",
        default="ips_list",
        required=False,
        help="Directory where the dump file will be located",
    )
    return parser


def main():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    root.addHandler(handler)

    parser = create_parser()
    opts = parser.parse_args()
    fd_out = open(opts.outdir, "a")

    database = db.MappingDB(opts.db_file)

    for file in get_ripe_files_list(opts.ripedir):
        fd = open(os.path.join(opts.ripedir, file), "r")
        data = json.load(fd)

        parsed_data = []
        print(file)
        for traceroute in data:
            parsed_traceroute = {}

            parsed_traceroute["src_addr"] = traceroute.get("src_addr", "*")
            parsed_traceroute["dst_addr"] = traceroute.get("dst_addr", "*")
            parsed_traceroute["endtime"] = traceroute.get("endtime", "*")
            parsed_traceroute["result"] = ip2asn(
                database, traceroute.get("result", None)
            )

            parsed_data.append(parsed_traceroute)


main()
