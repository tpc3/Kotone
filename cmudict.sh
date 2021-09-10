#!/bin/bash
if [ -e "cmudict-0.7b_baseform" ]
then
    echo Baseform exists, skipping cmudict build...
    exit 0
fi
curl http://svn.code.sf.net/p/cmusphinx/code/trunk/cmudict/scripts/make_baseform.pl -o make_baseform.pl
curl https://svn.code.sf.net/p/cmusphinx/code/trunk/cmudict/cmudict-0.7b -o cmudict-0.7b
perl make_baseform.pl cmudict-0.7b cmudict-0.7b_baseform
rm make_baseform.pl cmudict-0.7b
