#!/usr/bin/python
# from pprint import pprint
import itertools
from pathlib import Path
from typing import Optional

OUTDIR = Path("zones")

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


def zone(nsec, optout: Optional[bool] = False):
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


def zones():
    dnssec_params = [
        {"nsec": None},
        {"nsec": 1},
        {"nsec": 3, "optout": False},
        {"nsec": 3, "optout": True},
    ]

    for zone_params in [{"nsec": None}]:
        print_zone(zone(**zone_params))


def main():
    zones()


if __name__ == "__main__":
    main()
