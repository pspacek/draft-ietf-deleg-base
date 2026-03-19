#!/usr/bin/python
import itertools

import dns.message
import dns.name

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

        # print("-" * 40)
        # print(qname, qtype, f"DO={do} DE={de}")
        assert qtype
        yield dns.message.make_query(qname, qtype, ednsflags=ednsflags)


def main():
    with open(OUTFILE, "wb") as outf:
        for query in gen_queries("test"):
            wire = query.to_wire()
            msglen = len(wire)
            assert outf.write(msglen.to_bytes(length=2, byteorder="big")) == 2
            assert outf.write(wire) == msglen


if __name__ == "__main__":
    main()
