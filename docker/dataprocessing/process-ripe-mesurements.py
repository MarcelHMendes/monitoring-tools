import json
import db
import os
import argparse
import logging
import ipaddress
import sys
import radix
import ip2as
import pathlib


def get_ripe_files_list(dir):
    files = []
    files = os.listdir(dir)
    return files


def ip2asn_mapping(asdictdb, radixdb, traceroute_hops):
    hops = []
    cont_radix = 0
    cont_asdict = 0
    for hop in traceroute_hops:
        result = hop.get("result", None)
        if not result:
            continue
        ip_str = result[0].get("from", None)
        if not ip_str:
            continue
        asn = radixdb.get(ip_str)
        cont_radix += 1
        if not asn:
            asn = asdictdb.get(ip_str, None)
            if asn:
                cont_asdict += 1
        hops.append(asn)
    print(cont_radix, cont_asdict)

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

    radix_tree = radix.Radix()
    ip2asn = ip2as.IP2ASRadix(radix_tree)
    current_path = pathlib.Path().absolute()
    local = ip2asn.download_latest_caida_pfx2as(current_path)
    ip2asn = ip2asn.from_caida_prefix2as(local)

    ip2asn_2 = ip2as.IP2ASDict()
    ip2asn_2 = ip2asn_2.from_team_cymru_sqlite3(opts.db_file)


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
            parsed_traceroute["result"] = ip2asn_mapping(ip2asn_2,
                ip2asn, traceroute.get("result", None)
            )

            parsed_data.append(parsed_traceroute)

    print(parsed_data[-10:-1])
main()
