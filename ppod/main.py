#!/bin/env python

import xml.etree.ElementTree as ET
import feedparser
import urllib
import dateutil.parser
import math
import os
import eyed3
import re
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

def get_episode_infos(feed):
    pod_infos = []
    for entry in range(DOWNLOAD_EPISODES_COUNT):
        pod_info = {}
        try:
            for lk in feed['entries'][entry]['links']:
                if lk['rel'] == u'enclosure':
                    pod_info['episode_url'] = lk['href']
                    try:
                        pod_info['mime_type'] = lk['type']
                    except:
                        pod_info['mime_type'] = ''
                    break
        except IndexError:
            continue
        pod_info['episode_title'] =  fd['entries'][entry]['title']
        pod_info['episode_date'] =  fd['entries'][entry]['published']
        pod_info['feed_title'] = fd['feed']['title']
        pod_infos.append(pod_info)
    return pod_infos

def generate_filename(episode_info):
    """docstring for generate_filename"""
    date =  dateutil.parser.parse(episode_info['episode_date'])
    title = '_'.join(episode_info['feed_title'].split())
    title = clean_string(title)
    filename = '%04d%02d%02d_%s.mp3' % (date.year, date.month, date.day,
            title)
    return filename 

def show_progress(count, block_size, total):
    """docstring for show_progress"""
    total_blocks = math.ceil(total / block_size)
    percent_progress = (count / total_blocks) * 100
    msg = '\r\t\t\t\t\t%d%%' % percent_progress
    print (msg),

def update_tag(filename, episode_info):
    """docstring for update_tag"""
    audiofile = eyed3.load(filename)
    # TODO date galama
    orig_date = eyed3.core.Date(year, month=None, day=None, hour=None, minute=None, second=None)[source]
    if not audiofile.tag:
        tag = eyed3.id3.tag.Tag()
        tag.artist = episode_info['feed_title']
        tag.album = episode_info['feed_title']
        tag.title =  episode_info['episode_title']
        tag.original_release_date = episode_info['episode_date']
        tag.genre = u'Podcast'
        tag.save(filename, version=eyed3.id3.ID3_V2_3)
    else:
        audiofile.tag.artist = episode_info['feed_title']
        audiofile.tag.album = episode_info['feed_title']
        audiofile.tag.title =  episode_info['episode_title']
        audiofile.tag.date = episode_info['episode_date']
        audiofile.tag.genre = u'Podcast'
        audiofile.tag.save()

def clean_string(string):
    string = re.sub('[^\w\-_\.]', '_', string)
    string = re.sub('__', '_', string)
    string = re.sub('__', '_', string)
    string = string.strip('_')
    return string

def generate_dirname(episode_info):
    """docstring for generate_dirname"""
    title = '_'.join(episode_info['feed_title'].split())
    dirname = clean_string(title)
    return dirname 

def download_episode(episode, target):
    """docstring for download_episode"""
    os.system('setterm -cursor off')
    print episode['feed_title'],
    urllib.urlretrieve(episode['episode_url'], target, show_progress)
    os.system('setterm -cursor on')
    update_tag(target, episode)


if __name__ == '__main__':
    feeds = import_feeds()
    for feed in feeds:
        fd = parse_feed(feed['url'])
        episode_infos = get_episode_infos(fd)
        for episode in episode_infos:
            filename = generate_filename(episode)
            directory = generate_dirname(episode)
            target = os.path.join(directory, filename)
            if not os.path.exists(directory):
                os.makedirs(directory)
            if not os.path.exists(target):
                download_episode(episode, target)
                print 
