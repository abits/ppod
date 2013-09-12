#!/bin/env python

import xml.etree.ElementTree as ET
import feedparser
import urllib
import dateutil.parser
import math
import os
import eyed3
import re
import curses
import locale

locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()
tree = ET.parse('subscriptions.opml')
root = tree.getroot()
scr_line = 0

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
    msg = '%d%%' % percent_progress
    stdscr.addstr(scr_line, 70, msg)
    stdscr.refresh()

def update_tag(filename, episode_info):
    """docstring for update_tag"""
    audiofile = eyed3.load(filename)
    date =  dateutil.parser.parse(episode_info['episode_date'])
    orig_date = eyed3.core.Date(year=date.year, month=date.month, day=date.day)
    if not audiofile.tag:
        tag = eyed3.id3.tag.Tag()
        tag.artist = episode_info['feed_title']
        tag.album = episode_info['feed_title']
        tag.title =  episode_info['episode_title']
        tag.original_release_date = orig_date
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
    urllib.urlretrieve(episode['episode_url'], target, show_progress)
    update_tag(target, episode)

def init_curses():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    stdscr.keypad(1)
    return stdscr

stdscr = init_curses()

def end_curses(stdscr):
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()

def display_dl_msg(episode):
    msg = u'%s: %s' % (episode['feed_title'], episode['episode_title'])
    stdscr.addnstr(scr_line, 0, msg, 60)
    stdscr.refresh()

def display_complete_msg(episode):
    """docstring for display_complete_message"""
    msg = u'%s: %s' % (episode['feed_title'], episode['episode_title'])
    stdscr.addnstr(scr_line, 0, msg, 60)
    stdscr.addstr(scr_line, 70, 'OK  ')
    stdscr.refresh()

if __name__ == '__main__':
    feeds = import_feeds()
    for idx, feed in enumerate(feeds):
        scr_line = idx
        fd = parse_feed(feed['url'])
        episode_infos = get_episode_infos(fd)
        for episode in episode_infos:
            filename = generate_filename(episode)
            directory = generate_dirname(episode)
            target = os.path.join(directory, filename)
            if not os.path.exists(directory):
                os.makedirs(directory)
            if not os.path.exists(target):
                display_dl_msg(episode) 
                download_episode(episode, target)
            display_complete_msg(episode)
    end_curses()
