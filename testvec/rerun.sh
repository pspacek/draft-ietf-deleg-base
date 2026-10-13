#!/usr/bin/bash
set -o nounset -o errexit -o xtrace
source testvars.sh

RESPDIFFDIR=${RESPDIFFDIR:-~/w/pkg/respdiff/git}

rm -rf deleg/
${RESPDIFFDIR}/qprep.py -f tcpdns --tcpdns-file queries.tcpdns deleg/
${RESPDIFFDIR}/orchestrator.py -c respdiff.cfg deleg/
${RESPDIFFDIR}/msgdiff.py -c respdiff.cfg deleg/
${RESPDIFFDIR}/diffsum.py -c respdiff.cfg deleg/

pushd wrk
for ZONE in $ALLZONES; do
  dig +unknownformat +dnssec +de @127.0.0.1 -p 5375 nsec.test. AXFR >xfr.${ZONE}.knot.db
  dig +unknownformat +dnssec +de @127.0.0.1 -p 5366 nsec.test. AXFR >xfr.${ZONE}.bind.db
  dig +unknownformat +dnssec +de @127.0.0.1 -p 5377 nsec.test. AXFR >xfr.${ZONE}.pdns.db
  ldns-compare-zones -e xfr.${ZONE}.knot.db xfr.${ZONE}.bind.db
  ldns-compare-zones -e xfr.${ZONE}.pdns.db xfr.${ZONE}.bind.db
done
popd
