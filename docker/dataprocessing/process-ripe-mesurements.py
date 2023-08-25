import json
import ipaddress
import db


def traceroute_ips2asn(DBinstance, traceroute_hops):
    for hop in traceroute_hops:
        result = hop.get("result", None)
        if not result:
            continue
        ip_str = result[0].get("from", None)
        if not ip_str:
            continue
        ip_addr = ipaddress.IPv4Address(ip_str)
        ip_net = ipaddress.ip_network(ip_addr)
        ip_net_addr = ".".join(str(ip_net.network_address).split(".")[:-1]) + ".2"
        # print(ip_net.network_address)
        for pfxlen in range(24, 8, -1):
            query = DBinstance.query_data(prefix=ip_net_addr, subnet_mask=str(pfxlen))
            if query:
                print(ip_net_addr)
                break
            else:
                print("NOT")
                return


def print_query(query):
    row_format = "Prefix={prefix}, Mask={subnet_mask} , ASN={asn}"
    for row in query:
        print(
            row_format.format(
                prefix=row.prefix, subnet_mask=row.subnet_mask, asn=row.asn
            )
        )


fd = open("/etc/peering/monitor/data/ripe-measurements/41439480.json", "r")
db_file = "sqlite:///my_database.db"
db = db.MappingDB(db_file)

data = json.load(fd)
count = 0
parsed_data = []
for traceroute in data:
    parsed_traceroute = {}

    parsed_traceroute["src_addr"] = traceroute.get("src_addr", "x")
    parsed_traceroute["dst_addr"] = traceroute.get("dst_addr", "x")
    parsed_traceroute["result"] = traceroute.get("result", "x")
    traceroute_ips2asn(db, traceroute.get("result", {}))

    parsed_data.append(parsed_traceroute)
for traceroute in parsed_data:
    print(traceroute)
    if count == 10:
        break
    count = count + 1
