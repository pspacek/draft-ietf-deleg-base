#!/usr/bin/env python3
import sys
import dns.zone
import dns.name
import dns.rdatatype


def zero_signature(rrset):
    new = []
    for rr in rrset:
        newrr = dns.rdtypes.ANY.RRSIG.RRSIG(
            rdclass=rr.rdclass,
            rdtype=rr.rdtype,
            type_covered=rr.type_covered,
            algorithm=rr.algorithm,
            labels=rr.labels,
            original_ttl=rr.original_ttl,
            expiration=rr.expiration,
            inception=rr.inception,
            key_tag=rr.key_tag,
            signer=rr.signer,
            # Zero the signature
            signature=b"\x00" * len(rr.signature),
        )
        new.append(newrr)
    rrset.clear()
    for newrr in new:
        rrset.add(newrr)


def main():
    origin = dns.name.from_text(sys.argv[1])
    zone = dns.zone.from_text(sys.stdin.read(), relativize=False, origin=origin)
    for node in zone.nodes.values():
        for rrset in node:
            if rrset.rdtype == dns.rdatatype.RRSIG:
                zero_signature(rrset)
    print(zone.to_text())


if __name__ == "__main__":
    main()
