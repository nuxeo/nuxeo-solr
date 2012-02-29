#!/bin/sh

TREE_CSV=`pwd`/tree.csv
DOCS_CSV=`pwd`/docs.csv

# Turn on echoing and exit on error
set -x -e

if [ ! -f $TREE_CSV ]; then
	time python gen_tree_csv.py tree > $TREE_CSV
	time curl "http://localhost:8983/solr/update/csv?stream.file=$TREE_CSV&stream.contentType=text/plain;charset=utf-8&fieldnames=id,path,aclr&f.aclr.split=true&commit=true"
fi
if [ ! -f $DOCS_CSV ]; then
	time python gen_tree_csv.py > $DOCS_CSV
	time curl "http://localhost:8983/solr/update/csv?stream.file=$DOCS_CSV&stream.contentType=text/plain;charset=utf-8&fieldnames=tree_id,id,text&commit=true"
fi


