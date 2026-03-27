#!/usr/bin/bash
set -o nounset -o errexit -o xtrace
source testvars.sh

rm -rf deleg/
~/w/pkg/respdiff/git/qprep.py -f tcpdns --tcpdns-file queries.tcpdns deleg/
~/w/pkg/respdiff/git/orchestrator.py -c respdiff.cfg deleg/
~/w/pkg/respdiff/git/msgdiff.py -c respdiff.cfg deleg/
~/w/pkg/respdiff/git/diffsum.py -c respdiff.cfg deleg/

pushd wrk
for ZONE in $ALLZONES; do
  dig +unknownformat +dnssec +de @127.0.0.1 -p 5375 nsec.test. AXFR >xfr.${ZONE}.knot.db
  dig +unknownformat +dnssec +de @127.0.0.1 -p 5366 nsec.test. AXFR >xfr.${ZONE}.bind.db
  ldns-compare-zones -e xfr.${ZONE}.knot.db xfr.${ZONE}.bind.db
done
popd
