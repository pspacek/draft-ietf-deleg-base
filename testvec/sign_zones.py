#!/usr/bin/python
import sys
import subprocess

import generate_zones

EVENTS = set(["subprocess.Popen", "os.putenv", "os.getenv"])


def audit(event, data):
    if event in EVENTS:
        print(event, data)


def generate_keyfiles():
    zones = generate_zones.DNSSEC_PARAMS.copy()
    for zone_params in zones:
        if not zone_params["nsec"]:
            continue
        keygen_cmd = [
            "dnssec-keygen",
            "-fADT",
            "-fKSK",
            "-aECDSAP256SHA256",
            str(zone_params["origin"]),
        ]
        out = subprocess.check_output(keygen_cmd)
        keyfile = out.decode("ascii").strip()
        zone_params["keyfile"] = keyfile
    return zones


def sign(zone_params):
    assert zone_params["nsec"], zone_params
    cmd = [
        "dnssec-signzone",
        "-N",
        "increment",  # 1 -> 2, same as Knot DNS
        "-s",  # inception
        "20000101000000",
        "-e",  # expiration
        "20380119031407",  # just because we can,
        "-o",  # origin
        str(zone_params["origin"]),
        "-z",  # sign all records with KSKs
        "-S",  # smart signing: automatically finds key files
        # for the zone and determines how they are to be used
        # (so we don't have to manipulate zone file by hand to include DNSKEY)
    ]
    if zone_params["nsec"] == 3:
        cmd.extend(["-3", "-", "-H", "0"])
        if zone_params.get("optout"):
            cmd.extend(["-A"])

    cmd.extend([str(zone_params["zone_path"]), zone_params["keyfile"]])
    subprocess.check_call(cmd)


def main():
    zones = generate_keyfiles()
    for zone_params in zones:
        if "keyfile" in zone_params:
            sign(zone_params)


if __name__ == "__main__":
    sys.addaudithook(audit)
    main()
