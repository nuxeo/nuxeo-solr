# Architecture Overview (doc and modelling scripts)

In order to index the Nuxeo ACL into Solr and to avoid reindexing half
of the repository every time some ones grant a new right to a group on a
top level workspace we need to find a way to do smart BROWSE permission
filter with inherited rights resolution.

The scripts in this folder aims at check the feasability of implementing this
using the new join feature from the future Solr 4 release.


## Description of the data model

TODO:

In the mean time try to reverse engineer the `gen_tree_csv.py` file :)


## Loading the prototype model

Checkout and build the lucene / solr trunk

    $ svn co https://svn.apache.org/repos/asf/lucene/dev/trunk lucene
    $ cd lucene
    $ ant compile
    $ cd solr
    $ ant dist

Deploy the solr war in the example jetty webapps folder using a symlink:

    $ cd example/webapps
    $ ln -s ../../dist/apache-solr-4.0-SNAPSHOT.war solr.war

Configure the solrconfig.xml of the `example/solr/conf` folder to add the
following query parser plugin:

    <queryParser name="join"
        class="org.apache.solr.search.JoinQParserPlugin"/>

Replace the the default `example/solr/conf/schema.xml` with the one provided in
this folder.

Start solr:

    $ java -Xmx4g start.jar

Check you can login and use the solr admin interface at:

    http://localhost:8983/solr/

Install Python and Funkload:

    $ sudo pip install Funkload

Use the provided script to load some fake document tree structure with
text documents and aggregated positive ACLs on folders.

    $ sh load.sh

It is now possible to look for any document below some workspace using
the principals of the currently logged in user (use the "Query" interface
of the "singlecore" core in the Solr Web UI):

    q=text:stoma
    fq={!join from=id to=tree_id}(aclr:user_14110 OR aclr:administrators) path:/default-domain/workspaces/main-workspace/ajgrronr/48ewd4z/88n1bvp7/*
