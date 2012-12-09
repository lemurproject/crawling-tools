#!/usr/bin/env python
'''
Collects unique URLs of Blogger hosted blogs using the list of the most recently
updated sites.

The most recent updates are published every 10 minutes using this feed:

    http://www.blogger.com/changes10.xml

This script fetches that feed and stores the URLs on an sqlite database.

'''

import sys
import os
import time
import logging
import sqlite3
import datetime
import xml.etree.cElementTree as ElementTree

import argparse
import dateutil.parser
import requests

BLOGGER_CHANGES_URL = 'http://www.blogger.com/changes10.xml' 
USER_AGENT = 'Mozilla/5.0 (compatible; mandalay admin@lemurproject.org; +http://boston.lti.cs.cmu.edu/crawler/clueweb12pp/)'


def get_db_conn(db_path):
   
    if os.path.isfile(db_path):
        conn = sqlite3.connect(db_path)
        return conn


    conn = sqlite3.connect(db_path)

    # Create URL table
    c = conn.cursor()
    c.execute('''CREATE TABLE blogger_url
             (url text PRIMARY KEY, name text, updated text)''')

    conn.commit()

    return conn

def get_last_update(tree):
    try:
        last_update = tree.attrib['updated']
        return dateutil.parser.parse(last_update)
    except:
        return datetime.datetime.now()


def add_blog(blog, conn, last_updated):
    url = blog['url']

    sql_find = 'SELECT COUNT(1) FROM blogger_url WHERE url=?'

    conn.execute(sql_find, (url, ))
    (n_existing, ) = conn.fetchone()
    if n_existing > 0:
        return

    sql_insert = 'INSERT INTO blogger_url (url, name, updated)  VALUES (?, ?, ?)'
    

    n_secs = int(blog.get('when', 0))
    blog_updated = last_updated + datetime.timedelta(seconds=n_secs)

    conn.execute(sql_insert, (url, blog['name'], blog_updated.isoformat()))

    return True


def fetch_feed():
    headers = {'user-agent': USER_AGENT}
    res = requests.get(BLOGGER_CHANGES_URL, headers=headers)   

    if not res.encoding:
        res.encoding = 'utf8'

    content = res.text
    content = content.encode('utf-8', 'replace')
    tree = ElementTree.fromstring(content)

    return tree


def discover_urls(conn):
    cur = conn.cursor()
    tree = fetch_feed()

    last_updated = get_last_update(tree)

    n_added = 0
    for elem in tree.iterfind('weblog'):
        try:
            blog = dict(elem.items())
            added = add_blog(blog, cur, last_updated)
            n_added += added and 1 or 0
        except:
            logging.exception('Error adding blog')

    conn.commit()
    return n_added

def main():
    logging.BASIC_FORMAT = '%(asctime)-15s %(levelname)s:%(name)s:%(message)s'
    db_path = 'blogger-urls.sqlite'
    conn = get_db_conn(db_path) 
    n_added = discover_urls(conn)
    logging.info('Added %d blogs', n_added)

if __name__ == '__main__':
    main()

