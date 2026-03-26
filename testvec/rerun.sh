#!/usr/bin/bash
set -o nounset -o errexit -o xtrace
export PATH=~/w/pkg/bind/install/each-deleg-auth_36dd69fac375b546870915f58c13edc6f91add58_ccache_gcc-march-native-ggdb3-O0/bin:~/w/pkg/bind/install/each-deleg-auth_36dd69fac375b546870915f58c13edc6f91add58_ccache_gcc-march-native-ggdb3-O0/sbin:$PATH
export PYTHONPATH=~/w/pkg/python-dns/git

rm -rf deleg/
~/w/pkg/respdiff/git/qprep.py -f tcpdns --tcpdns-file queries.tcpdns deleg/
~/w/pkg/respdiff/git/orchestrator.py -c respdiff.cfg deleg/
~/w/pkg/respdiff/git/msgdiff.py -c respdiff.cfg deleg/
~/w/pkg/respdiff/git/diffsum.py -c respdiff.cfg deleg/
