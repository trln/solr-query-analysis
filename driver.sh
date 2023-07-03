#!/bin/sh


# Sample driver script to run tests against a Solr host
# a number of times.

for host in solr_4 solr_7; do
    if [ $host == 'solr_4' ]; then
        collection='trlnbib'
    else
        collection='trlnbib20230622'
    fi
    for i in 1 2 3 4 5 6; do
        ./qp2.py -n $i -c $collection $host
    done
done
