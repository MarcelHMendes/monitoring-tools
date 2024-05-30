import ipaddress
import logging
import os
import sys

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

PEERING = {}

BOGON_PREFIXES = list(ipaddress.IPv4Network(b) for b in BOGONS)


def peering_resolver(ip):
    if ip in PEERING:
        return PEERING[ip]
    return None


def is_private_ip(ip):
    ip_obj = ipaddress.IPv4Address(ip)
    for pfx in BOGON_PREFIXES:
        if ip_obj in pfx:
            return True
    return False


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
