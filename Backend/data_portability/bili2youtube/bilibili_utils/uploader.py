import requests
import math
import subprocess
import time
from fake_useragent import UserAgent
from ..youtube_utils import *
#from Backend.data_portability.bili2youtube.youtube_utils import *

SESSION_ID = ''
VIDEO_DOWNLOAD_PATH = "/Users/ziranmin/Downloads/"
VIDEO_DOWNLOAD_QUALITY_ID = 32 # 清晰度参考 https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/video/videostream_url.md

def get_user_info(session_id=SESSION_ID):
    url = 'https://api.bilibili.com/x/web-interface/nav'
    cookies = {'SESSDATA': session_id}
    try:
        response = requests.get(url, cookies=cookies)
        json_response = response.json()
        user = {}
        user['uname'] = json_response['data']['uname']
        user['mid'] = json_response['data']['mid']
        user['profile_pic'] = json_response['data']['face']
        return user

    except Exception as error:
        print("An exception occurred:", type(error).__name__, "–", error)


def get_all_videos(mid):
    '''

    :param mid: user id
    :return:
    '''

    cookie = (
        "buvid3=BD50D87E-E743-1743-C2A1-9A41DC86273F95198infoc; b_nut=1694354195; i-wanna-go-back=-1; b_ut=7; _uuid=23CA6788-D728-9B77-5E5F-F10D24638A18195282infoc;"
        "home_feed_column=4; buvid4=D17D272D-3947-6103-59E9-B477F4A6F10096454-023091021-ADgaJkpv35ag3jEPdUjt5A%3D%3D; header_theme_version=CLOSE;"
        "SESSDATA=87481b1e%2C1709943379%2C0441c%2A92CjAHfmGBZolEBjVXoxNTSolsIZoib7Jtc9i-EMWOeEhrBNhv2FlQbDNa0gn_sGGIhpoSVlNMSDBubVZKd1E4VU84Uk5WZlBETHpBRzFOekwxNG1NY3MtNkN0ZHNnVDFrUzFpWnZDNi1La2FyRFlxTktyZEVkdEJsc1ZjM1VuQ1duTzFkb1llUmtBIIEC;"
        "bili_jct=b7a72f2b5318bc9825f355e72b7d043c; DedeUserID=210437382; DedeUserID__ckMd5=f39352f467bcdc4c; sid=5kfzrj3i; rpdid=|(J|)RYllukR0J'uYmRJmuJmu;"
        "CURRENT_QUALITY=80; is-2022-channel=1; fingerprint=c92d21e3c77cb459556d4c284764ee0e; buvid_fp_plain=undefined; hit-new-style-dyn=1;"
        "hit-dyn-v2=1; LIVE_BUVID=AUTO8316944407472560; bsource=search_baidu; browser_resolution=1373-670; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9."
        "eyJleHAiOjE2OTU0NDkwOTYsImlhdCI6MTY5NTE4OTg5NiwicGx0IjotMX0.kezcVsJdP_jTH8IHoi3Cz_r9suiWvZfj3SpA1L2zv70; bili_ticket_expires=1695449096; PVID=1;"
        "CURRENT_BLACKGAP=0; CURRENT_FNVAL=4048; bp_video_offset_210437382=844202489484935223; buvid_fp=c92d21e3c77cb459556d4c284764ee0e; b_lsid=9F13B10610_18ABF3F3F36"
    )

    ua = UserAgent()
    # agent_set = set()
    # first_agent = ua.random
    # agent_set.add(first_agent)

    base_url = f'https://api.bilibili.com/x/space/wbi/arc/search?mid={mid}&ps=30&pn=1'
    # headers = {
    #     # 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    #     'Referer': f'https://space.bilibili.com/{mid}/video',
    #     # 'Referer': f'https://space.bilibili.com/',
    #     # "User-Agent": first_agent,
    #     "User-Agent": ua.random,
    # }

    headers = {
        "User-Agent": ua.random,
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.bilibili.com/",
        "Cookie": cookie  # 添加 Cookie
    }

    time.sleep(2)

    try:
        response = requests.get(base_url, headers=headers)
        json_response = response.json()

        # print(json_response)

        res = []
        total_videos = json_response['data']['page']['count']
        page_size = json_response['data']['page']['ps']
        total_pages = math.ceil(total_videos / page_size)

        # print("total_pages", total_pages)
        for page in range(1, total_pages + 1):
            # print('page: ', page)
            url = f'https://api.bilibili.com/x/space/wbi/arc/search?mid={mid}&ps=30&pn={page}'

            # next_agent = ua.random
            # while next_agent in agent_set:
            #     next_agent = ua.random
            # agent_set.add(first_agent)

            # headers = {
            #     # 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            #     'Referer': f'https://space.bilibili.com/{mid}/video',
            #     # 'Referer': f'https://space.bilibili.com/',
            #     # "User-Agent": next_agent,
            #     "User-Agent": ua.random,
            # }

            headers = {
                "User-Agent": ua.random,
                "Accept-Language": "en-US,en;q=0.5",
                "Referer": "https://www.bilibili.com/",
                "Cookie": cookie  # 添加 Cookie
            }

            response = requests.get(url, headers=headers)
            json_response = response.json()
            video_list = json_response['data']['list']['vlist']
            for v in video_list:
                res.append({'bvid': v['bvid'],
                            'aid': v['aid'],
                            'title': v['title'],
                            # 'description': v['description'],
                            # 'pic': v['pic'],
                            # 'play_count': v['play'],
                            # 'created_at': v['created'],
                            # 'owner_mid': v['mid'],
                            # 'owner_name': v['author'],
                            })
            time.sleep(2)

        return res

    except Exception as error:
        print("An exception occurred:", type(error).__name__, "–", error)


def get_series_lists(mid):
    '''

    :param mid: user id
    :return:
    '''
    base_url = f'https://api.bilibili.com/x/polymer/web-space/seasons_series_list?mid={mid}&page_num=1&page_size=20'
    try:
        response = requests.get(base_url)
        json_response = response.json()

        total_videos = json_response['data']['items_lists']['page']['total']
        page_size = json_response['data']['items_lists']['page']['page_size']
        total_pages = math.ceil(total_videos / page_size)

        # print("total_pages", total_pages)
        res = []

        for page in range(1, total_pages + 1):
            url = f'https://api.bilibili.com/x/polymer/web-space/seasons_series_list?mid={mid}&page_num={page}&page_size={page_size}'
            response = requests.get(url)
            json_response = response.json()
            series_list = json_response['data']['items_lists']['series_list']
            for item in series_list:
                res.append({'series_id': item['meta']['series_id'],
                            'name': item['meta']['name'],
                            'description': item['meta']['description']})
        return res

    except Exception as error:
        print("An exception occurred:", type(error).__name__, "–", error)


def get_series_list_videos(mid, series_id):
    base_url = f'https://api.bilibili.com/x/series/archives?mid={mid}&series_id={series_id}&only_normal=true&sort=desc&pn=1&ps=30'
    try:
        response = requests.get(base_url)
        json_response = response.json()

        total_videos = json_response['data']['page']['total']
        page_size = json_response['data']['page']['size']
        total_pages = math.ceil(total_videos / page_size)

        # print("total_pages", total_pages)
        res = []

        for page in range(1, total_pages + 1):
            url = f'https://api.bilibili.com/x/series/archives?mid={mid}&series_id={series_id}&only_normal=true&sort=desc&pn={page}&ps={page_size}'
            response = requests.get(url)
            json_response = response.json()
            for item in json_response['data']['archives']:
                # each video has two types of id, aid and bvid, we store both of them, but we primarily use bvid
                res.append({'bvid': item['bvid'],
                            'aid': item['aid'],
                            'title': item['title'],
                            })
        return res

    except Exception as error:
        print("An exception occurred:", type(error).__name__, "–", error)


def get_video_info(bvid):
    '''

    :param bvid: video id
    :return:
    '''
    url = 'https://api.bilibili.com/x/web-interface/view'
    params = {'bvid': bvid}
    try:
        response = requests.get(url, params=params)
        json_response = response.json()
        # video = {'bvid': bvid}
        data = json_response['data']
        video = {
            'id': bvid,
            'bvid': bvid,
            "aid": data["aid"],
            "cid": data["cid"],
            "title": data["title"],
            "desc": data["desc"],
            "img": data["pic"],
            'owner_mid': data['owner']['mid'],
            'owner_name': data['owner']['name'],
            "view": data["stat"]["view"],
            "like": data["stat"]["like"],
            "star": data["stat"]["favorite"],
            "share": data["stat"]["share"],
            "comment": data["stat"]["reply"],
            "disable": False,
            "checked": False,
        }
        return video

    except Exception as error:
        print("An exception occurred:", type(error).__name__, "–", error)


def get_video_tags(bvid, session_id=SESSION_ID):
    url = 'https://api.bilibili.com/x/tag/archive/tags'
    params = {'bvid': bvid}
    cookies = {'SESSDATA': session_id}
    try:
        response = requests.get(url, params=params, cookies=cookies)
        tags = []
        json_response = response.json()
        data = json_response['data']
        for item in data:
            tags.append(item['tag_name'])
        return tags
    except Exception as error:
        print("An exception occurred:", type(error).__name__, "–", error)


def get_video_source_link(bvid, cid, qn=VIDEO_DOWNLOAD_QUALITY_ID, session_id=SESSION_ID):
    url = 'https://api.bilibili.com/x/player/playurl'
    params = {
        'bvid': bvid,
        'cid': cid,
        'qn': qn,
        'fnval': '0',
        'fnver': '0',
        'fourk': '1'
    }
    cookies = {'SESSDATA': session_id}
    try:
        response = requests.get(url, params=params, cookies=cookies)
        tags = []
        json_response = response.json()
        data = json_response['data']
        return data['durl'][0]['url']
    except Exception as error:
        print("An exception occurred:", type(error).__name__, "–", error)


def download_video(bvid, video_url, qn=VIDEO_DOWNLOAD_QUALITY_ID, path=VIDEO_DOWNLOAD_PATH):
    video_name = bvid + '_' + str(qn) + '.mp4'
    full_path = path + video_name
    cmd = [
        "wget",
        video_url,
        "--referer", "https://www.bilibili.com",
        "-O", full_path
    ]
    #
    # subprocess.run(cmd)
    # print("download finish")

    try:
        # subprocess.run(cmd, capture_output=True, text=True, check=True)
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # If you want to see the output or errors, you can print them
        print(result.stdout)  # Standard output
        print(result.stderr)  # Error output

        print("Download finished!")

    except subprocess.CalledProcessError as e:
        print(f"Command failed with error code {e.returncode}")
        print(e.stderr)
    except Exception as error:
        print("An exception occurred:", type(error).__name__, "–", error)


def get_all_videos_with_detailed_info(mid):
    try:
        all_video_id_list = get_all_videos(mid)
        res = []
        for v in all_video_id_list:
            res.append(get_video_info(v['bvid']))
        return res
    except Exception as error:
        print("An exception occurred:", type(error).__name__, "–", error)


def get_all_series_list_with_video_ids(mid):
    try:
        res = []
        series_lists = get_series_lists(mid)
        for ser_list in series_lists:
            series_id = ser_list['series_id']
            video_ids = []
            series_videos = get_series_list_videos(mid, ser_list['series_id'])
            for v in series_videos:
                video_ids.append(v['bvid'])

            temp = {
                'id': series_id,
                'title': ser_list['name'],
                'video_ids': video_ids,
            }
            res.append(temp)
        return res
    except Exception as error:
        print("An exception occurred:", type(error).__name__, "–", error)

def create_youtube_playlist_for_uploader(mid):
    try:
        bplaylists = []
        series_lists = get_series_lists(mid)
        for series in series_lists:
            series_id = series['series_id']
            videos = get_series_list_videos(mid, series_id)
            youtube_video_list = []
            for video in videos:
                youtube_video_list.append(video['bvid'])
            playlist = PlaylistInfo(
                    title=series['name'],
                    description=series['description'],
                    tags=[],
                    defaultLanguage="en",
                    privacyStatus="public",
                    platform=Platform.BILIBILI,
                    videoList=youtube_video_list,
                )
            bplaylists.append(playlist)
        return bplaylists
    except Exception as error:
        print("An exception occurred:", type(error).__name__, "–", error)

def get_and_download_all_videos_from_bilibili_for_youtube(mid, session_id=SESSION_ID, qn=VIDEO_DOWNLOAD_QUALITY_ID, path=VIDEO_DOWNLOAD_PATH):
    try:
        bvideos = []
        all_video_list = get_all_videos(mid)
        for video in all_video_list:
            bvid = video['bvid']
            video_info = get_video_info(bvid)
            video_tags = get_video_tags(bvid, session_id)
            cid = video_info['cid']

            vurl = get_video_source_link(bvid, cid)
            download_video(bvid, vurl, qn, path)

            youtube_video = VideoInfo(
                filename=VIDEO_DOWNLOAD_PATH + bvid + '_' + str(VIDEO_DOWNLOAD_QUALITY_ID) + '.mp4',
                title=video_info['title'],
                platform=Platform.BILIBILI,
                id=bvid,
                description=video_info['desc'],
                tags=video_tags,
                privacyStatus="private",
            )
            bvideos.append(youtube_video)
        return bvideos
    except Exception as error:
        print("An exception occurred:", type(error).__name__, "–", error)


if __name__ == '__main__':
    print("hello world")

    mid = '1794123514'

    # print(create_youtube_playlist_for_uploader(mid))

    # print(get_and_download_all_videos_from_bilibili_for_youtube(mid))


    # print out own account info by using the session id got from QR code login
    # print("print out own account info by using the session id got from QR code login")
    # user = get_user_info(SESSION_ID)
    # print(user)

    # # get all the videos uploaded by a user ordered by latest created time
    # print("get all the videos uploaded by Meetfood觅食 ordered by latest created time")
    # mid = '447317111' # Meetfood觅食 user id
    # all_video_id_list = get_all_videos(mid)
    # print(len(all_video_id_list))
    # for v in all_video_id_list:
    #     print(v)

    # # get a user's all series list
    # print("get Meetfood觅食's all series list")
    # mid = '447317111' # Meetfood觅食 user id
    # series_lists = get_series_lists(mid)
    # for ser_list in series_lists:
    #     print(ser_list)

    # get one of the series_ids from a user's series_list, get all the videos from that list
    # print("get one of the series_ids from Meetfood觅食's series_list, get all the videos from that list")
    # mid = '447317111' # Meetfood觅食 user id
    # series_id = 3634963
    # videos = get_series_list_videos(mid, series_id)
    # for video in videos:
    #     print(video)

    # # get the detailed info of a video
    # print("get the detailed info of a video")
    # bvid = "BV1Ls4y137Hq"
    # video = get_video_info(bvid)
    # print(video)
    # # get the tags of a video
    # tags = get_video_tags(bvid)
    # print(tags)

    # # get the source link of a video
    # print("get the source link of a video")
    # # bvid = "BV1Ls4y137Hq"
    # vurl = get_video_source_link(bvid, video['cid'])
    # print(vurl)

    # # download the video
    # # print("download the video")
    # # download_video(bvid, vurl)




    # # get a user's all videos and all series list with video ids, and bundle togehter
    # print("get a user's all videos and all series list with video ids, and bundle togehter")
    # user = get_user_info(SESSION_ID)
    # mid = user['mid']
    # # mid = '1794123514'
    #
    # all_videos = get_all_videos_with_detailed_info(mid)
    # all_series_with_video_ids = get_all_series_list_with_video_ids(mid)
    # data = {
    #     'videos': all_videos,
    #     'sets': all_series_with_video_ids,
    # }
    #
    # print(data)



