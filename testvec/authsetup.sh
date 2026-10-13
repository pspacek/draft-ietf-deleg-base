#!/usr/bin/bash
set -o nounset -o errexit -o xtrace

source testvars.sh

rm -rfv wrk
mkdir -v wrk
pushd wrk
../generate_zones.py
../sign_zones.py || :

for ZONE in $ALLZONES; do
  pdnsutil --config-dir=.. zone load "${ZONE}" "${ZONE}.zone"
done

for ZONE in $SIGNEDZONES; do
  KEYID="$(keymgr -c ../knotd.conf "$ZONE" import-bind K${ZONE}.*.private | cut -f 1 -d $'\n')"
  keymgr -c ../knotd.conf "$ZONE" set "$KEYID" ksk=yes zsk=yes # CSK
  keymgr -c ../knotd.conf "$ZONE" list

  pdnsutil --config-dir=.. zone import-key "${ZONE}" K${ZONE}.+013+*.private KSK active

  if [ "${ZONE}" = "nsec3.test" ]; then
    pdnsutil --config-dir=.. zone set-nsec3 "${ZONE}" "1 0 0 -"
  elif [ "${ZONE}" = "optout-nsec3.test" ]; then
    pdnsutil --config-dir=.. zone set-nsec3 "${ZONE}" "1 1 0 -"
  fi

  pdnsutil --config-dir=.. zone rectify "${ZONE}"
  pdnsutil --config-dir=.. zone show "${ZONE}"
done
popd
