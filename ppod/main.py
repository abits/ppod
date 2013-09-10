#!/bin/env python

import xml.etree.ElementTree as ET
import feedparser
import urllib
import math
tree = ET.parse('subscriptions.opml')
root = tree.getroot()

DOWNLOAD_EPISODES_COUNT = 1

def import_feeds():
    """docstring for import_feeds"""

    pod_feeds = []
    for i in root.findall(".//outline"):
        if 'xmlUrl' in i.attrib:
            pod_feed = {'url': i.attrib['xmlUrl'],
                        'title': i.attrib['title']}
            pod_feeds.append(pod_feed)
    return pod_feeds


def parse_feed(feed_url):
    feed  = feedparser.parse(feed_url)
    return feed

def episode_infos(feed):
    pod_infos = []
    for entry in range(DOWNLOAD_EPISODES_COUNT):
        pod_info = {}
        for lk in fd['entries'][entry]['links']:
            if lk['rel'] == u'enclosure':
                pod_info['episode_url'] = lk['href']
                pod_info['mime_type'] = lk['type']
                break
        pod_info['episode_title'] =  fd['entries'][entry]['title']
        pod_info['episode_date'] =  fd['entries'][entry]['published']
        pod_info['feed_title'] = fd['feed']['title']
        pod_infos.append(pod_info)
    return pod_infos

def generate_filename(episode_info):
    """docstring for generate_filename"""
    return 'episode.mp3' 

def show_progress(count, block_size, total):
    """docstring for show_progress"""
    total_blocks = math.ceil(total / block_size)
    percent_progress = (count / total_blocks) * 100
    msg = '\r%d' % percent_progress
    print (msg),

def update_tag():
    """docstring for update_tag"""
    pass

if __name__ == '__main__':
    feeds = import_feeds()
    fd = parse_feed(feeds[3]['url'])
    episode_infos = episode_infos(fd)
    for episode in episode_infos:
        filename = generate_filename(episode)
        urllib.urlretrieve(episode['episode_url'], filename, show_progress)
        update_tag(filename)


