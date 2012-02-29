#!/usr/bin/env python
"""
Generates a csv of the "tree" ready to inject into solr
"""
import sys
import random
from funkload import Lipsum

# docs (not yet impl)
DOCS = 1000 * 1000
ACLS = 1 * 1000                 # in addition to personal tree acls

# tree
PERSONAL_TREE = 50 * 1000
USERS = 50 * 1000
GROUPS = 1 * 1000
FOLDER_PER_LEVEL = 8            # for 5 level hard coded 8**5 -> 32768 folders
FOLDER_PER_ACL = 25             # 1 acl for 25 folder

# -- test
#PERSONAL_TREE = 50

BASE_PATH = '/default-domain/workspaces'
PERSONAL_BASE_PATH = BASE_PATH + '/members'
MAIN_BASE_PATH = BASE_PATH + '/main-workspace'
LIPSUM = Lipsum.Lipsum()
GROUP_NAMES = []
for i in xrange(GROUPS):
    GROUP_NAMES.append('group_%3.3d' % i)


def get_id(levels):
    lvl = [0, 0, 0, 0, 0]
    for i in range(len(levels)):
        lvl[i] = levels[i]
    return "%2.2d_%2.2d_%2.2d_%2.2d_%2.2d" % (lvl[0], lvl[1], lvl[2], lvl[3], lvl[4])


def get_perso_id(i):
    lev = [99, i]
    return "%2.2d_%6.6d" % (lev[0], lev[1])


def gen_personal_acl(num):
    return "user_%5.5d,administrators,Administrator" % num


def gen_personal_tree():
    for i in xrange(PERSONAL_TREE):
        print '%s,"%s/%s","%s"' % (get_perso_id(i), PERSONAL_BASE_PATH, LIPSUM.getUniqWord(), gen_personal_acl(i))


def gen_main_acl():
    group = random.choice(GROUP_NAMES)
    principals = ','.join(['user_%d' % random.randint(0, USERS) for i in range(random.randint(1,5))])
    return "%s,%s,administrators,Administrator" % (principals, group)


def gen_main_tree():
    #print "id, path, aclr"
    lvl = [0, 0, 0, 0, 0]
    path = [MAIN_BASE_PATH, '', '', '', '', '']
    n = 0
    acls = gen_main_acl()
    for i in range(FOLDER_PER_LEVEL):
        path[1] = LIPSUM.getUniqWord()
        for j in range(FOLDER_PER_LEVEL):
            path[2] = LIPSUM.getUniqWord()
            for k in range(FOLDER_PER_LEVEL):
                path[3] = LIPSUM.getUniqWord()
                for l in range(FOLDER_PER_LEVEL):
                    path[4] = LIPSUM.getUniqWord()
                    if not n % FOLDER_PER_ACL:
                        acls = gen_main_acl()
                    for m in range(FOLDER_PER_LEVEL):
                        lvl = [i, j, k, l, m]
                        path[5] = LIPSUM.getUniqWord()
                        print '"%s","%s","%s"' % (get_id(lvl), '/'.join(path), acls)


def get_random_id(i):
    if i % 30:
        return "%2.2d_%2.2d_%2.2d_%2.2d_%2.2d" % (random.randint(0, FOLDER_PER_LEVEL),
                                                  random.randint(0, FOLDER_PER_LEVEL),
                                                  random.randint(0, FOLDER_PER_LEVEL),
                                                  random.randint(0, FOLDER_PER_LEVEL),
                                                  random.randint(0, FOLDER_PER_LEVEL))
    return "99_%6.6d" % random.randint(0, USERS)


def gen_docs():
    #print "tree_id, id, text"
    for i in xrange(DOCS):
        tid = get_random_id(i)
        print '"%s","%32.32d","%s"' % (tid, i, LIPSUM.getParagraph())


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "tree":
        gen_personal_tree()
        gen_main_tree()
    else:
        gen_docs()
