#!/usr/bin/python
"""
Quick hack to generate giant table with all sensible and some less-sensible
combinations of query parameters, zone content, and server software versions.
Output is a table in CSV format.
It is intended as exploratory tool so we don't forget some corner case.

The tool pre-generates "answer" according to my understanding of the protocol
and my personal taste but it does NOT represent the only possible outcome of
the design process. Reasons why it generates given "answer" are given in
answer() function below.

Author: Petr Špaček <pspacek@isc.org>
"""
import csv
from enum import StrEnum
import itertools
import sys


# combination of options we consider:
class Qname(StrEnum):
    """qname"""

    EXACT = "test."
    SUBDOMAIN = "sub.test."


class Qtype(StrEnum):
    """qtype"""

    DELEG = "DELEG"
    DS = "DS"
    NS = "NS"
    OTHER = "A"


class Queryflag(StrEnum):
    """DE"""

    DE0 = "DE=0"
    DE1 = "DE=1"


class Auth(StrEnum):
    """DELEG aware auth"""

    DELEG_UNAWARE = "DELEG unaware"
    DELEG_AWARE = "DELEG aware"


class NSRR(StrEnum):
    """test. NS"""

    ABSENT = "NS absent"
    PRESENT = "NS present"


class DELEGRR(StrEnum):
    """test. DELEG"""

    ABSENT = "DELEG absent"
    PRESENT = "DELEG present"


class Answer(StrEnum):
    """answer"""

    TODO = ""


def filter_possibilities(variant):
    """skip all types except one for SUBDOMAIN query, they are all the same"""
    if variant[Qname] != Qname.SUBDOMAIN:
        return variant
    if variant[Qtype] != Qtype.OTHER:
        return None
    variant[Qtype] = "all"
    return variant


def answer(row):
    """generate 'answer' column value for given table row"""
    note = ""  # appended to end of answer if applicable
    if row[NSRR] == NSRR.ABSENT and row[DELEGRR] == DELEGRR.ABSENT:
        # does not exist in any case, does not depend on DELEG-awareness of client or server, qname or qtype
        return "NXDOMAIN, AUTHORITY: NSEC"

    if row[Qtype] == Qtype.DS:
        # no change to DS processing, does not depend on DELEG-awareness on client or server
        assert (
            row[Qname] == Qname.EXACT
        )  # our table should not have DS rows for subdomains
        if row[NSRR] == NSRR.ABSENT and row[Queryflag] == Queryflag.DE0:
            note = " (odd case for an old validator - DS without NS)"
        return f"NOERROR, ANSWER: DS / AUTHORITY: NSEC{note}"

    if row[Auth] == Auth.DELEG_UNAWARE and row[DELEGRR] == DELEGRR.PRESENT:
        # odd combinations of an old auth with a DELEG RR in zone
        match row[NSRR]:
            case NSRR.PRESENT:
                # DELEG RR is occluded by NS and does not affect processing
                note = " (DELEG RR occluded)"
            case NSRR.ABSENT:
                # NS does not exist so it's not a zone cut from old auth's perspective
                # old server does not know DELEG is allowed only on zone cut so it will be accepted
                if row[Qname] == Qname.SUBDOMAIN:
                    # ... but at the same time DELEG does not create delegation for this server
                    return "NXDOMAIN, AUTHORITY: NSEC"
                match row[Qtype]:
                    case Qtype.DELEG:
                        # DELEG RR will be accepted in unknown RR format so it will be returned as usual
                        return "NOERROR, ANSWER: DELEG"
                    case _:
                        # the node is non-empty because of DELEG, which is not a delegation for an old server
                        return "NOERROR, AUTHORITY: NSEC"

    if row[Auth] == Auth.DELEG_UNAWARE or row[Queryflag] == Queryflag.DE0:
        # no change to existing NS delegations if unaware or DE=0
        if row[NSRR] == NSRR.PRESENT and row[Qtype] != Qtype.DS:
            return f"NOERROR, AUTHORITY: NS + (DS / NSEC){note}"

    # all DELEG-unaware cases were handled above (or we have a bug)
    assert row[Auth] is Auth.DELEG_AWARE

    if row[Qname] == Qname.EXACT and row[Qtype] == Qtype.DELEG:
        # explicit query for DELEG, we don't care about DE bit
        # (same logic as for DS DO=0 queries)
        match row[DELEGRR]:
            case DELEGRR.PRESENT:
                return "NOERROR, ANSWER: DELEG"
            case DELEGRR.ABSENT:
                return "NOERROR, AUTHORITY: NSEC"

    # DELEG and DS queries were handled above,
    # all remaining cases are queries for non-authoritative data either with DE=0/1
    # -> must result in delegation
    match row[Queryflag]:
        case Queryflag.DE0:
            # old client, look only at NS
            match row[NSRR]:
                case NSRR.PRESENT:
                    return "NOERROR, AUTHORITY: NS + (DS / NSEC)"
                case NSRR.ABSENT:
                    match row[Qname]:
                        case Qname.EXACT:
                            return "NOERROR, AUTHORITY: NSEC"
                        case Qname.SUBDOMAIN:
                            return "NXDOMAIN, AUTHORITY: NSEC (same as DELEG-unaware with correct proof for an old validator, but TODO discuss)"

    # we have dealt with DELEG-unaware servers and old clients above, welcome to the new wonderful world of DELEG
    assert row[Queryflag] is Queryflag.DE1

    match row[DELEGRR]:
        case DELEGRR.PRESENT:
            return "NOERROR, AUTHORITY: DELEG + (DS / NSEC)"
        case DELEGRR.ABSENT:
            assert (
                row[NSRR] is NSRR.PRESENT
            )  # case of no delegation whatsoever is handled at the beginning
            return "NOERROR, AUTHORITY: NS + DS + NSEC (for DELEG and possibly also DS)"

    return ""


def list_posibilities(source_enum):
    return (source_enum, list(source_enum))


def main():
    """Spit out table of combinations to stdout"""
    possibilities = dict(
        [
            list_posibilities(field)
            for field in [Qname, Qtype, Queryflag, DELEGRR, NSRR, Auth, Answer]
        ]
    )
    writer = csv.DictWriter(sys.stdout, fieldnames=possibilities.keys())
    names = [e.__doc__ for e in writer.fieldnames]
    writer.writerow(dict(zip(writer.fieldnames, names)))
    for row in itertools.product(*possibilities.values()):
        variant = dict(zip(possibilities.keys(), row))
        variant = filter_possibilities(variant)
        if variant:
            variant[Answer] = answer(variant)
            writer.writerow(variant)


if __name__ == "__main__":
    main()
