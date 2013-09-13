`ppod` -- Download podcasts
===========================

Ppod reads feed information from an opml file called ``subscriptions.opml``.
It downloads the latest episode of each podcast defined in that file.  Ppod
renames the downloaded audio files using their publication date and updates
their mp3 tag information.  Download progress is displayed in a curses window.

Use this program at your own risk!

Requirements::

    feedparser
    eyed3
    dateutil

Usage::

    ./ppod.py


