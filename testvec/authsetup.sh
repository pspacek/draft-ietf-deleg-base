#!/usr/bin/bash
set -o nounset -o errexit -o xtrace

source testvars.sh

rm -rfv wrk
mkdir -v wrk
pushd wrk
../generate_zones.py
../sign_zones.py || :

for ZONE in $SIGNEDZONES; do
  KEYID="$(keymgr -c ../knotd.conf "$ZONE" import-bind K${ZONE}.*.private | cut -f 1 -d $'\n')"
  keymgr -c ../knotd.conf "$ZONE" set "$KEYID" ksk=yes zsk=yes # CSK
  keymgr -c ../knotd.conf "$ZONE" list
done
popd
