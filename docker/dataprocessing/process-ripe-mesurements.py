import json
import ipaddress
import db

def traceroute_ips2asn(DBinstance, traceroute_hops):
    for hop in traceroute_hops:
        result = hop["result"]
        ip_str = result["from"]
        ip_addr = ipaddress.IPv4Address(ip_str)
        ip_net = ipaddress.ip_network(ip_addr)

        for pfxlen in range(24, 8, -1)
            query = DBinstance.query_data(
                prefix=ip_net.network_address, subnet_mask=pfxlen
            )
            if query:
                DBinstance.print_query(query)
                break


fd = open("/etc/peering/monitor/data/ripe-measurements/41439480.json", "r")


data = json.load(fd)
count = 0
parsed_data = []
for traceroute in data:
    parsed_traceroute = {}

    parsed_traceroute["src_addr"] = traceroute.get("src_addr", "x")
    parsed_traceroute["dst_addr"] = traceroute.get("dst_addr", "x")
    traceroute_hops = traceroute.get("result", "x")
    parsed_traceroute["result"] = #traceroute.get("result", "x")

    parsed_data.append(parsed_traceroute)
for traceroute in parsed_data:
    print(traceroute)
    if count == 10:
        break
    count = count + 1
