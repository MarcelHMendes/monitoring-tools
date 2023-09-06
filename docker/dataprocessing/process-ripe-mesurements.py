import json
import os
import argparse
import logging
import sys
import radix
import ip2as
import pathlib


def get_ripe_files_list(dir):
    files = []
    files = os.listdir(dir)
    return files


def set_logging():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    root.addHandler(handler)


def routeviews_db():
    radix_tree = radix.Radix()
    ip2asn = ip2as.IP2ASRadix(radix_tree)
    current_path = pathlib.Path().absolute()
    local = ip2asn.download_latest_caida_pfx2as(current_path)
    ip2asn = ip2asn.from_caida_prefix2as(local)
    return ip2asn


def cymru_db(opts):
    ip2asn = ip2as.IP2ASDict()
    ip2asn = ip2asn.from_team_cymru_sqlite3(opts.db_file)
    return ip2asn

def ip2asn_mapping(radixdb, asdictdb, traceroute_hops):
    hops = []
    for hop in traceroute_hops:
        result = hop.get("result", None)
        if not result:
            continue
        ip_str = result[0].get("from", None)
        if not ip_str:
            continue
        asn = radixdb.get(ip_str)
        # if radixdb doesn't resolve, we'll try asdictdb
        if not asn:
            asn = asdictdb.get(ip_str, None)
        hops.append(asn)
    return hops

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
        default="parsed_traceroutes",
        required=False,
        help="Directory where the dump file will be located",
    )
    return parser


def main():
    set_logging()

    parser = create_parser()
    opts = parser.parse_args()

    rv_ip2asn = routeviews_db()
    cy_ip2asn = cymru_db(opts)

    for file in get_ripe_files_list(opts.ripedir):
        fd = open(os.path.join(opts.ripedir, file), "r")
        data = json.load(fd)

        parsed_data = []
        for traceroute in data:
            parsed_traceroute = {}

            parsed_traceroute["src_addr"] = traceroute.get("src_addr", "*")
            parsed_traceroute["dst_addr"] = traceroute.get("dst_addr", "*")
            parsed_traceroute["endtime"] = traceroute.get("endtime", "*")

            mapping = ip2asn_mapping(
                rv_ip2asn, cy_ip2asn, traceroute.get("result", None)
            )
            parsed_traceroute["result"] = mapping

            parsed_data.append(parsed_traceroute)

    with open(opts.outdir, "w") as fd_out:
        json.dump(parsed_data, fd_out)


main()
