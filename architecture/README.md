# Architecture Overview (doc and modeling scripts)

In order to index the Nuxeo ACL into Solr and to avoid reindexing half
of the repository every time some ones grant a new right to a group on a
top level workspace we need to find a way to do smart BROWSE permission
filter with inherited rights resolution.

The scripts in this folder aims at check the feasability of implementing this
using the new join feature from the future Solr 4 release.


## Description of the data model

The main idea is to have two types of Solr document in the Solr Core,
a lightweight ones for modeling the tree structure and ACLs inheritance
and a larger one for the documents themselves.

The tree nodes only have 3 fields: an id, a fullpath
(`document.getPathAsString()` in Nuxeo) and a multivalued field holding
the list all principals that have a positive BROWSE permission on the
node after ACL inheritance resolution. There is one such entry for each
folderish documents or non folderish document that carries a local ACL
directly on itself.

The ACL inheritance is thus expanded/denormalized at indexing time but
only on the tree entries, not on the document entries. Only the `DENY
Everything Everyone` negative ACE is supported. Other than that only
positive ACL are handled by the current model. If the support for stacked
negative ACE is required it could be later implemented with a custom
Solr QueryParser plugin that would derive from
`org.apache.solr.search.JoinQParserPlugin` further adding the negative
filtering logic).

The other solr documents hold a `tree_id` (which is foreign reference to the
parent tree node), the nuxeo doc ref and (optionally the parent ref),
the indexed fulltext fields. There is one such entry for every single nuxeo
document in the repository (including the folderish documents).

Searching a document with ACL and/or path filtering happens using a
[join](https://wiki.apache.org/solr/Join) on the 2 types of entries.

Updating ACLs or moving a folder to one workspace to another can happen
without reindexing the fulltext of all the documents belonging to the
local subtree.

Updating ACLs or moving a folder would involve reindexing all the
ACL/folderish entries in the subtree but this should be doable in a single
Solr Update query + commit to handle the atomicity of the operation at
least for flat/wide enough hierarchies (to be checked).

This design expects to handle up to 100k ACL/folderish entries and up
to several tens or hundreds of millions of document entries.


## Installing and configuring Solr trunk

In order to implement the ACL filtering we need the join query parser plugin
that will be shipped in Solr 4. Hence we build the developer version.


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


## Loading a fake document tree with inherited ACLs

The following builds a tree with ~90k folders, 50k of which are personal
flat user workspaces with restricted local rights and the remaining are
5 levels nested tree with a mix of inherited permissions.

This folderish tree is populated with 1M text documents spread in the
various folders.

The first part generates 2 CSV files, one for the tree structure and
the other for the documents themselves.

Install Python and Funkload:

    $ sudo pip install Funkload

Use the provided script to load some fake document tree structure with
text documents and aggregated positive ACLs on folders.

    $ sh load.sh
    
This will result in an heterogenous core (tree nodes + docs) of total
size ~700MB on the disk.

It is now possible to look for any document below some workspace using
the principals of the currently logged in user (use the "Query" interface
of the "singlecore" core in the Solr Web UI):

    q=text:stoma
    fq={!join from=id to=tree_id}(aclr:user_14110 OR aclr:administrators) path:/default-domain/workspaces/main-workspace/ajgrronr/48ewd4z/88n1bvp7/*

## Conclusions

This approach seems quite feasible for the 1M documents scale using the
default Solr settings.

- a subpath + ACL administrators query matching 570352 documents returns
  in around 1s

- refining the previous query (same fq clause, hence warm field query caches)
  but adding a text criteria (e.g. the word folius) matches 185230 documents
  in ~30ms

The JVM was launched with max heap space of 3GB, 500MB of which
are effectively allocated and 90MB are actually used when performing
the queries according to JVisualVM)

Futher experiments with larger volumes and concurrency with a mix of queries,
doc update, folder move and ACL updates need to be implemented to confirm
those early results.
