#!/usr/bin/env python3
"""
This script runs the `sdig` tool with many different queries
against several nameservers.

These servers should be running at the ports in the NAMESERVERS dict.

For each nameserver, a file with the all the query results will be available in the
OUTDIR ("sdig") directory. These files can be compared using `diff` to see
if (and what) differs between answers from the different nameservers.

Note that SOA details and EDNS RData are hidden (e.g. PowerDNS bumps the SOA serial, and some
implementations send different EDE's), that the RRSets are ordered (i.e. may not appear in
the order they were sent) and that all owner names are lowercased. All these changes
should not affect the comparison of DelExt responses, but be aware of them.

You'll need an unreleased version of `sdig` in your $PATH, built from
the "auth-deleg" branch of the pieterlexis/pdns fork (https://github.com/pieterlexis/pdns/).

To build sdig, clone the repo, checkout the correct branch, then:

meson setup build -Dtools=true && meson compile -C build sdig
"""

import itertools
import os
import shutil
import subprocess

import dns.name

from generate_zones import parent_zones

OUTDIR = "sdig"
NAMESERVERS = {
    "knot": 5375,
    "bind": 5366,
    "pdns": 5377
}


def gen_queries(delegation_owner: dns.name.Name):
    subdomains = [None, "sub"]
    qtypes = ["NS", "TYPE61440", "DS", "A", "TXT"]
    booleans = [False, True]
    for prefix, qtype, do, de in itertools.product(
        *[subdomains, qtypes, booleans, booleans]
    ):
        if prefix:
            qname = dns.name.from_text(prefix, origin=delegation_owner)
        else:
            qname = delegation_owner

        resp = [str(qname), qtype]

        if do:
            resp.append("dnssec")
        if de:
            resp.append("delegation-extensions")

        yield resp


def do_query(query_info):
    # knot, bind, pdns
    for nameserver, port in NAMESERVERS.items():
        command = (
            ["sdig", "127.0.0.1", str(port)]
            + query_info
            + ["showedns", "hidesoadetails", "hideednsrdata", "sort", "lowercasename"]
        )
        out = subprocess.check_output(command)
        with open(f"{OUTDIR}/{nameserver}-{port}.txt", "ab") as f:
            f.write(b"=======> ")
            f.write(" ".join(query_info).encode())
            f.write(b" <=======")
            f.write(b"\n")
            f.write(out)


def main():
    shutil.rmtree(OUTDIR, ignore_errors=True)
    os.mkdir(OUTDIR)
    for origin, zonedata in parent_zones().items():
        for owner_rel, _, _ in zonedata:
            owner = dns.name.from_text(owner_rel, origin)
            for query in gen_queries(owner):
                do_query(query)


if __name__ == "__main__":
    main()
