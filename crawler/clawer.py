#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 16:29:27 2019

@author: simon
"""

import youtube_dl
import requests
from googleapiclient.discovery import build
from pycaption import WebVTTReader, DFXPReader

DEVELOPER_KEY = 'AIzaSyBofGDrV8lckZmEu9iVP9gaMUCyCkFZhww' 
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

def search_channel():
    
    PageToken = "CEsQAA"
    #Token: CDIQAQ,CDIQAA,CEsQAA,CGQQAA,CH0QAA,CJYBEAA,CK8BEAA,CMgBEAA
    
    request = youtube.search().list(
            part="snippet",
            channelType="any",
            maxResults=25,
            order="viewCount",
            pageToken=PageToken,
            type="channel"
            )
    
    channels = []
    channels_print = []
    for i in range(1, 2):
        
        response = request.execute()
        
        for search_result in response.get('items', []):
            print('%s (%s)' % (search_result['snippet']['title'], search_result['id']['channelId']))
            channels.append(search_result['id']['channelId'])
            channels_print.append('%s (%s)' % (search_result['snippet']['title'],
                                        search_result['id']['channelId']))
        
        PageToken = response.get('nextPageToken')
        request = youtube.search().list(
            part="snippet",
            channelType="any",
            maxResults=25,
            order="viewCount",
            pageToken=PageToken,
            type="channel"
            )
    
    f = open('channel.data', 'w')
    f.write('\n'.join(channels_print))
    
    return channels

ydl_playlist = youtube_dl.YoutubeDL({'extract_flat': 'in_playlist',
                                     'playlistend': 500})

# https://www.youtube.com/user/TheLinuxFoundation/videos
def get_video_list(channel_id):
    url = 'https://www.youtube.com/channel/{}'.format(channel_id)
    r = ydl_playlist.extract_info(url, download=False)
    return [i['url'] for i in r['entries'] if i['_type'] == 'url']


ydl_subtitle = youtube_dl.YoutubeDL({'skip_download': True,
                                     'allsubtitles': True,
                                     'writesubtitles': True,
                                     'writeautomaticsub': True,
                                     'writethumbnail': True,
                                     })

# https://www.youtube.com/watch?v=yrkSmLDsCsU
def get_subtitle(r):
    sub = r.get('subtitles', None)
    auto = r.get('automatic_captions', None)

    en = sub.get('en', None) if sub else None
    if not en:
        en = auto.get('en', None) if auto else None

    if en:
        for i in en:
            if i['ext'] == 'ttml':
                return i['url'], i['ext']

        return en[-1]['url'], en[-1]['ext']
    else:
        return None, None
    
def get_title(r):
    title = r.get('title', None)
    return title

def get_desc(r):
    description = r.get('description', None)
    return description

def get_picture(r):
    picture = r.get('thumbnail', None)
    return picture

def datestr2secs(datestr):
    array = datestr.split('.')
    array1 = array[0].split(':')
    sectime = 0
    i = 2
    for v in array1:
        sectime = sectime + int(v) * pow(60, i)
        i = i -1
    return sectime

def getVidfromchannel(channel_id, f, vid_num):
    vids = get_video_list(channel_id)
    
    #f = open('{}.data'.format(channel_id), 'w')
    num = vid_num
    debug = 500
    useless = 20
    
    for vid in vids:
        try:
            #if the video is available
            #vid_request = youtube.videos().list(
            #        part="contentDetails",
            #        id=vid
            #        )
            #vid_response = vid_request.execute()
            #vid_item = vid_response.get('items',[])[0]
            #vid_license = vid_item['contentDetails']['licensedContent']
            #if 'regionRestriction' in vid_item['contentDetails']:
            #    vid_regRest = vid_item['contentDetails']['regionRestriction']
            #    if 'allowed' in vid_regRest:
            #        if 'US' not in vid_regRest['allowed']:
            #            continue
            #    if 'blocked' in vid_regRest:
            #        if 'US' in vid_regRest['blocked']:
            #            continue
            #if vid_license == False:
            #    continue
            #url
            vid_url = 'https://www.youtube.com/watch?v={}'.format(vid)
            r = ydl_subtitle.extract_info(vid_url, download=False)
            #video title
            vid_title = get_title(r)
            #video thumbnail
            vid_picture = get_picture(r)
            url, ext = get_subtitle(r)
            if url == None and ext == None:
                useless = useless - 1
                if useless <= 0:
                    return num
                continue
            if ext == 'ttml':
                r = requests.get(url)
                if r.ok:
                    subtitles = DFXPReader().read(r.text)
                    captions = subtitles.get_captions('en-US')
                    time_subtitle = []
                    for i in captions:
                        #subtitle content
                        text = i.get_text()
                        if text.find('[' and ']') != -1:
                            continue
                        starttime = i.format_start()
                        #subtitle time in sec
                        sectime = datestr2secs(starttime)
                        
                        time_subtitle.append('<time>{}</time>{}'.format(sectime,text))
                    time_subtitleFormat = '\n'.join(time_subtitle)
                    
                    num = num + 1
                    f.write('''
<new>
<title>{}</title>
<url>{}</url>
<picture>{}</picture>
<subtitle>
{}
</subtitle>
</new>
==end artical==
'''.format(vid_title,vid_url,vid_picture,time_subtitleFormat))
                    debug = debug - 1
                    if debug <= 0:
                        return num
        except:
            pass
    return num
                

if __name__ == '__main__':
    channels_id = search_channel()
    
    f = open('dataset.data', 'w')
    vid_num = 0
    cha_num = 0
    for channel in channels_id:
        vid_num = getVidfromchannel(channel, f, vid_num)
        cha_num = cha_num + 1
    print("video nums:"+str(vid_num))
    print("channel nums:"+str(cha_num))