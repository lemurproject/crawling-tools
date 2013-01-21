#!/bin/bash

DIR=$(cd $(dirname "$0"); pwd)

java=`which java`
#/usr/java/latest/bin/java

expfile=$1
warc=$2

if [[ ! -f $expfile ]] || [[ -z $warc ]]; then
    echo "Usage: $0 regexp-file file1.warc.gz ..."
    exit 1
fi


$java -cp $DIR/target/crawling-tools-assembly-0.1.jar lemur.tools.ExtractLinks $* | sort | uniq

