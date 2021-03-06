#!/usr/bin/env python3

import json
import os
import urllib
import re
from time import mktime, sleep
from datetime import datetime as dt

import feedparser
import requests


# Read bot token from environment
TOKEN = os.environ['MIA_TG_TOKEN']
CHATID = os.environ['MIA_TG_CHATID']

URL = f"https://api.telegram.org/bot{TOKEN}/"


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates():
    url = URL + "getUpdates"
    js = get_json_from_url(url)
    return js


def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return text, chat_id


def send_message(text, chat_id):
    text = re.sub('(?<!\\\\)!', '\\!', text)
    text = re.sub('(?<!\\\\)#', '\\#', text)
    text = urllib.parse.quote_plus(text)
    url = (f"{URL}sendMessage?text={text}"
           f"&chat_id={chat_id}"
           "&parse_mode=MarkdownV2")
    get_url(url)


def tg_send(text):
    send_message(text, CHATID)


def check_minkorrekt(max_age=3600):
    MINKORREKT_RSS = 'http://minkorrekt.de/feed/'
    mi_feed = feedparser.parse(MINKORREKT_RSS)
    newest_episode = mi_feed['items'][0]
    episode_release = dt.fromtimestamp(mktime(newest_episode['published_parsed']))
    if (dt.now() - episode_release).total_seconds() < max_age:
        tg_send(f'*{newest_episode.title}*\n'
                'Eine neue Folge Methodisch inkorrekt ist erschienen\\!\n'
                f'[Jetzt anhören]({newest_episode.link})')


def check_youtube(max_age=3600):
    YOUTUBE_RSS = 'https://www.youtube.com/feeds/videos.xml?channel_id=UCa8qyXCS-FTs0fHD6HJeyiw'
    yt_feed = feedparser.parse(YOUTUBE_RSS)
    newest_episode = yt_feed['items'][0]
    episode_release = dt.fromtimestamp(mktime(newest_episode['published_parsed']))
    if (dt.now() - episode_release).total_seconds() < max_age:
        tg_send(f'*{newest_episode.title}*\n'
                'Eine neues Youtube Video ist erschienen!\n'
                f'[Jetzt ansehen]({newest_episode.link})')


while True:
    check_minkorrekt(3600)
    check_youtube(3600)
    sleep(3595)
