#!/usr/bin/python
# from pprint import pprint
import itertools
from pathlib import Path
from dns.name import from_text
import dns.name

OUTDIR = Path("zones")
SUBTREE = from_text("test.")
DNSSEC_PARAMS = [
    {"nsec": None, "origin": from_text("unsigned", origin=SUBTREE)},
    {"nsec": 1, "origin": from_text("nsec", origin=SUBTREE)},
    {"nsec": 3, "optout": False, "origin": from_text("nsec3", origin=SUBTREE)},
    {"nsec": 3, "optout": True, "origin": from_text("optout-nsec3", origin=SUBTREE)},
]


def zone_path(origin: dns.name.Name):
    return Path(str(origin.relativize(dns.name.root) + from_text("zone", origin=None)))


for zone_params in DNSSEC_PARAMS:
    zone_params["zone_path"] = zone_path(zone_params["origin"])

rr_examples = {
    "ns": ["NS", "ns1.test."],
    "a": ["A", "192.0.2.1"],
    "deleg": ["DELEG", "server-name=ns1.test."],
}


def delegation_name(ns: bool, deleg: bool, a: bool):
    present = []
    if ns:
        present.append("ns")
    if deleg:
        present.append("deleg")
    if a:
        present.append("a")
    if not present:
        present = ["nxdomain"]
    return "-".join(present)


def zone_data():
    rr_combinations = [
        {"ns": bool1, "deleg": bool2, "a": bool3}
        for bool1, bool2, bool3 in itertools.product(*[[False, True]] * 3)
    ]
    rrs = [
        ["@", "SOA", ". . 1 86400 86400 86400 86400"],
        ["@", "NS", "todo.invalid.  ; TODO not necessary"],
    ]
    for combination in rr_combinations:
        name = delegation_name(**combination)
        for rrtype, present in combination.items():
            if present:
                rrs.append([name] + rr_examples[rrtype])
            # if not all(combination.values()):
            # for NXDOMAIN case we don't generate any values
    return rrs


def print_zone(rrtuples):
    for owner, rrtype, rdata in rrtuples:
        print("\t".join([owner, rrtype, rdata]))


def parent_zones():
    zones = {}

    for zone_params in DNSSEC_PARAMS:
        zones[zone_params["origin"]] = zone_data()
    return zones


def main():
    for origin, rrtuples in parent_zones().items():
        with open(zone_path(origin), "w") as zf:
            zf.write("$TTL 86400\n")
            zf.writelines(f'{"\t".join(rrtuple)}\n' for rrtuple in rrtuples)


if __name__ == "__main__":
    main()
