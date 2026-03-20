#!/usr/bin/python
import itertools

import dns.message
import dns.name

from generate_zones import zone

OUTFILE = "queries.tcpdns"


def gen_queries(delegation_owner: str):
    subdomains = [None, "sub"]
    qtypes = ["NS", "TYPE61440", "DS", "A", "TXT"]
    booleans = [False, True]
    for prefix, qtype, do, de in itertools.product(
        *[subdomains, qtypes, booleans, booleans]
    ):
        if prefix:
            qname = dns.name.from_text(
                prefix, origin=dns.name.from_text(delegation_owner)
            )
        else:
            qname = dns.name.from_text(delegation_owner)
        ednsflags = 0
        if do:
            ednsflags |= 0x8000
        if de:
            ednsflags |= 0x2000

        print(qname, qtype, f"DO={do} DE={de}")
        q = dns.message.make_query(qname, qtype, ednsflags=ednsflags)
        q.flags = 0  # remove default RD bit (and everything else, too)
        yield q


def write_query(query, outfile):
    wire = query.to_wire()
    msglen = len(wire)
    assert outfile.write(msglen.to_bytes(length=2, byteorder="big")) == 2
    assert outfile.write(wire) == msglen


def main():
    zone_data = zone({"nsec": None})
    with open(OUTFILE, "wb") as outf:
        for owner, _, _ in zone_data:
            for query in gen_queries(f"{owner}.test."):
                write_query(query, outf)


if __name__ == "__main__":
    main()
