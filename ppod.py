#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# ppod.py - download podcast episodes
#
# Copyright (C) 2013 Christoph Martel
#
# This program is free software; you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by the 
# Free Software Foundation; either version 3 of the License, or (at your 
# option) any later version.
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY 
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License 
# along with this program; if not, see <http://www.gnu.org/licenses/>.

'''
:mod:`ppod` -- Download podcasts
================================

.. module:: ppd
   :platform: Unix
   :synopsis: Download podcasts episodes.
.. moduleauthor:: Christoph Martel <chris@codeways.org>

Ppod reads feed information from an opml file called `subscriptions.opml`.
It downloads the latest episode of each podcast defined in that file.  Ppod
renames the downloaded audio files using their publication date and updates
their mp3 tag information.  Download progress is displayed in a curses window.

Use this program at your own risk!

Requirements:
    feedparser
    eyed3
    dateutil

Usage: ./ppod.py
'''

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

# some intial settings for curses
locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()
scr_line = 0
stdscr = None

# config
DOWNLOAD_EPISODES_COUNT = 1
OPML_FILE = 'subscriptions.opml'


def import_feeds():
    """Extract feed url and titles from opml file.
    
    :returns: list of dicts with feed info
    :rtype: list
    """

    tree = ET.parse(OPML_FILE)
    root = tree.getroot()
    pod_feeds = []
    for i in root.findall(".//outline"):
        if 'xmlUrl' in i.attrib:
            pod_feed = {'url': i.attrib['xmlUrl'],
                        'title': i.attrib['title']}
            pod_feeds.append(pod_feed)
    return pod_feeds


def parse_feed(feed_url):
    """Parse feed with feedparser.

    :param feed_url: str
    :returns: parsed feed 
    :rtype: dict
    """
    feed = feedparser.parse(feed_url)
    return feed


def get_episode_infos(feed):
    """Extract episode info from feed,

    :param feed: str
    :returns: episode information
    :rtype: list
    """
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
        pod_info['episode_title'] = fd['entries'][entry]['title']
        pod_info['episode_date'] = fd['entries'][entry]['published']
        pod_info['feed_title'] = fd['feed']['title']
        pod_infos.append(pod_info)
    return pod_infos


def generate_filename(episode_info):
    """Construct filename for download from episode data.
    
    :param episode_info: dict
    :returns: filename
    :rtype: str
    """
    date = dateutil.parser.parse(episode_info['episode_date'])
    title = '_'.join(episode_info['feed_title'].split())
    title = clean_string(title)
    filename = '%04d%02d%02d_%s.mp3' % (date.year, date.month, date.day, title)
    return filename


def show_progress(count, block_size, total):
    """Display progress in percent of download size in curses window.
    
    :param count: block count
    :param block_size: block size in byte
    :param total: total size of chunk in byte
    """
    total_blocks = math.ceil(total / block_size)
    percent_progress = (count / total_blocks) * 100
    msg = '%d%%' % percent_progress
    stdscr.addstr(scr_line, 70, msg)
    stdscr.refresh()


def update_tag(filename, episode_info):
    """Update mp3 tag information from episode data.
    
    :param filename: str
    :param episode_info: dict
    """
    audiofile = eyed3.load(filename)
    date = dateutil.parser.parse(episode_info['episode_date'])
    orig_date = eyed3.core.Date(year=date.year, month=date.month, day=date.day)
    if not audiofile.tag:
        tag = eyed3.id3.tag.Tag()
        tag.artist = episode_info['feed_title']
        tag.album = episode_info['feed_title']
        tag.title = episode_info['episode_title']
        tag.original_release_date = orig_date
        tag.genre = u'Podcast'
        tag.save(filename, version=eyed3.id3.ID3_V2_3)
    else:
        audiofile.tag.artist = episode_info['feed_title']
        audiofile.tag.album = episode_info['feed_title']
        audiofile.tag.title = episode_info['episode_title']
        audiofile.tag.date = episode_info['episode_date']
        audiofile.tag.genre = u'Podcast'
        audiofile.tag.save()


def clean_string(string):
    """Remove certain characters from string.

    :param string: str
    :returns: cleaned string
    :rtype: str
    """
    string = re.sub('[^\w\-_\.]', '_', string)
    string = re.sub('__', '_', string)
    string = re.sub('__', '_', string)
    string = string.strip('_')
    return string


def generate_dirname(episode_info):
    """Construct download dir for feed from episode data.
    
    :param episode_info: dict
    :returns: dir name
    :rtype: str
    """
    title = '_'.join(episode_info['feed_title'].split())
    dirname = clean_string(title)
    return dirname


def download_episode(episode, target):
    """Save episode audio file to disk and update mp3 tag."""
    urllib.urlretrieve(episode['episode_url'], target, show_progress)
    update_tag(target, episode)


def init_curses():
    """Initialize curses window.

    :returns: default screen
    :rtype: curses window
    """
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    stdscr.keypad(1)
    return stdscr


def end_curses(stdscr):
    """Reset terminal.
    
    :param stdscr: curses window
    """

    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()


def display_dl_msg(episode):
    """Display downloaded episode info in curses window.
    
    :param episode: dict
    """
    msg = u'%s: %s' % (episode['feed_title'], episode['episode_title'])
    stdscr.addnstr(scr_line, 0, msg, 60)
    stdscr.refresh()


def display_complete_msg(episode):
    """Display episode info for completed download.
    
    :param episode: dict
    """
    msg = u'%s: %s' % (episode['feed_title'], episode['episode_title'])
    stdscr.addnstr(scr_line, 0, msg, 60)
    stdscr.addstr(scr_line, 70, 'OK  ')
    stdscr.refresh()


# main application
if __name__ == '__main__':
    stdscr = init_curses()
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
