import youtube_dl
import requests
from pycaption import WebVTTReader, DFXPReader

ydl_playlist = youtube_dl.YoutubeDL({'extract_flat': 'in_playlist'})

# https://www.youtube.com/user/TheLinuxFoundation/videos
def get_video_list(channel_name):
    url = 'https://www.youtube.com/user/{}/videos'.format(channel_name)
    r = ydl_playlist.extract_info(url, download=False)
    return [i['url'] for i in r['entries'] if i['_type'] == 'url']


ydl_subtitle = youtube_dl.YoutubeDL({'skip_download': True,
                                     'allsubtitles': True,
                                     'writesubtitles': True,
                                     'writeautomaticsub': True
                                     })

# https://www.youtube.com/watch?v=yrkSmLDsCsU
def get_subtitle(vid):
    url = 'https://www.youtube.com/watch?v={}'.format(vid)
    r = ydl_subtitle.extract_info(url, download=False)
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

def test(channel_name):
    # todo: collect channel list
    vids = get_video_list(channel_name)
    f = open('{}.data'.format(channel_name), 'w')
    debug = 20
    for vid in vids:
        url, ext = get_subtitle(vid)
        if ext == 'ttml':
            r = requests.get(url)
            if r.ok:
                subtitles = DFXPReader().read(r.text)
                # todo: maybe ' ' rather than '\n'
                text = '\n'.join(i.get_text() for i in subtitles.get_captions('en-US'))
                f.write('''
<DOC>
<VID> {} </VID>
<CONTENT>
{}
</CONTENT>
</DOC>'''.format(vid, text))

                # todo: remove labels like "[music]"

                debug = debug - 1
                if debug <= 0:
                    return

                # if True: # debug
                #     with open('./ttml.ttml', 'w') as ttml, open('./result.text', 'w') as result:
                #         ttml.write(r.text)
                #         result.write(text)
                #     return
            else:
                pass
                # todo: error, retry and store error url
                print('!!! net error -> {}'.format(vid))
        else:
            # todo: vtt has some problem, see if all videos has ttml captions
            pass
            print('!!!!! no ttml format -> {}'.format(vid))

if __name__ == '__main__':
    test('TheLinuxFoundation')
