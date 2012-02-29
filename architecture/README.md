# Architecture Overview (doc and modelling scripts)

In order to index the Nuxeo ACL into Solr and to avoid reindexing half
of the repository every time some ones grant a new right to a group on a
top level workspace we need to find a way to do smart BROWSE permission
filter with inherited rights resolution.

The scripts in this folder aims at check the feasability of implementing this
using the new join feature from the future Solr 4 release.
