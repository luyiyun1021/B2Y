import requests
import math
from Backend.data_portability.bili2youtube.youtube_utils import *


SESSION_ID = ''

def get_followings_list(mid, page_size=10, session_id=SESSION_ID):
    url = 'https://api.bilibili.com/x/relation/followings'
    base_params = {
        'vmid': mid,
        'ps': page_size,
        'pn': 1,
    }
    cookies = {'SESSDATA': session_id}

    try:
        response = requests.get(url, params=base_params, cookies=cookies)
        json_response = response.json()
        res = []
        total_followings = json_response['data']['total']
        total_pages = math.ceil(total_followings / page_size)
        # print('total_followings', total_followings)
        # print('total_pages', total_pages)

        for page in range(1, total_pages + 1):
            params = {
                'vmid': mid,
                'ps': page_size,
                'pn': page,
            }
            response = requests.get(url, params=params, cookies=cookies)
            json_response = response.json()
            following_list = json_response['data']['list']
            for item in following_list:
                followed_user = {'mid': item['mid'], 'uname': item['uname']}
                res.append(followed_user)
        return res
    except Exception as error:
        print("An exception occurred:", type(error).__name__, "–", error)

def get_collection_folders(mid):
    url = 'https://api.bilibili.com/x/v3/fav/folder/created/list-all'
    params = {
        'up_mid': mid,
    }
    try:
        response = requests.get(url, params=params)
        res = []
        json_response = response.json()
        folder_list = json_response['data']['list']
        for folder in folder_list:
            cur_folder = {}
            cur_folder['id'] = folder['id']
            cur_folder['title'] = folder['title']
            res.append(cur_folder)
        return res

    except Exception as error:
        print("An exception occurred:", type(error).__name__, "–", error)

def get_collection_folder_intro_description(folder_id, session_id=SESSION_ID):
    url = 'https://api.bilibili.com/x/v3/fav/resource/list'
    cookies = {'SESSDATA': session_id}
    params = {
        'media_id': folder_id,
        'ps': 10,
        'pn': 1,
        'platform': 'web',
    }
    try:
        response = requests.get(url, params=params, cookies=cookies)
        json_response = response.json()
        info_data = json_response['data']['info']
        description = info_data['intro']
        return description
    except Exception as error:
        print("An exception occurred:", type(error).__name__, "–", error)

def get_collection_videos_from_a_folder(folder_id, page_size=2, session_id=SESSION_ID):
    url = 'https://api.bilibili.com/x/v3/fav/resource/list'
    cookies = {'SESSDATA': session_id}
    res = []
    page_num = 1
    try:
        while True:
            params = {
                'media_id': folder_id,
                'ps': page_size,
                'pn': page_num,
                'platform': 'web',
            }
            response = requests.get(url, params=params, cookies=cookies)
            json_response = response.json()
            video_list = json_response['data']['medias']
            for item in video_list:
                video = {'bvid': item['bvid'],
                         'title': item['title'],
                         'owner': {
                             'mid': item['upper']['mid'],
                             'name': item['upper']['name'],
                            },
                         }
                res.append(video)
            has_more = json_response['data']['has_more']
            if has_more:
                page_num += 1
            else:
                break
        return res
    except Exception as error:
        print("An exception occurred:", type(error).__name__, "–", error)

def create_youtube_playlist_for_viewer(mid, session_id=SESSION_ID):
    try:
        youtube_playlists = []
        folder_list = get_collection_folders(mid)
        for folder in folder_list:
            folder_id = folder['id']
            folder_description = get_collection_folder_intro_description(folder_id, session_id=session_id)
            collection_videos = get_collection_videos_from_a_folder(folder_id, session_id=session_id)
            videos = []
            for video in collection_videos:
                videos.append(video['bvid'])
            playlist = PlaylistInfo(
                title=folder['title'],
                description=folder_description,
                tags=[],
                defaultLanguage="en",
                privacyStatus="private",
                platform=Platform.BILIBILI,
                videoList=videos,
            )
            youtube_playlists.append(playlist)
        return youtube_playlists
    except Exception as error:
        print("An exception occurred:", type(error).__name__, "–", error)


# NOTE: current limitation:
# 1. can only get most recent 20 likes, couldn't find correct pagination method;
#   but from mobile app, it seems can load more than 20
# 2. if the user set account to private, can't get their like history

def get_like_history(mid):
    url = f'https://api.bilibili.com/x/space/like/video?vmid={mid}'
    try:
        response = requests.get(url)
        json_response = response.json()
        res = []
        video_list = json_response['data']['list']
        for item in video_list:
            video = {'bvid':item['bvid'],
                     'title': item['title'],
                     'owner': {
                        'mid': item['owner']['mid'],
                        'name': item['owner']['name'],
                     }}
            res.append(video)
        return res
    except Exception as error:
        print("An exception occurred:", type(error).__name__, "–", error)

if __name__ == '__main__':
    print("hello world")

    mid = 1794123514 # Ziran's user id


    print(create_youtube_playlist_for_viewer(mid))







    # v1 = VideoInfo(
    #     filename="xxx",
    #     title="zzz",
    #     platform=Platform.BILIBILI,
    #     id="bvid00000",
    #     description="",
    #     tags=[],
    #     privacyStatus="private",
    # )
    # print(v1)











    # get a list of accounts that the given user is following
    # print("get a list of accounts that the given user is following")
    # following_list = get_followings_list(1794123514)
    # for x in following_list:
    #     print(x)


    # # get all the collection folders created by a user
    # print("get all the collection folders created by a user")
    # folder_list = get_collection_folders(mid)
    # for x in folder_list:
    #     print(x)
    #
    #
    # # get all the videos from one of the collections folders
    # print("get all the videos from one of the collections folders")
    # folder_id = 2533049514
    # collection_videos = get_collection_videos_from_a_folder(folder_id=folder_id)
    # for videos in collection_videos:
    #     print(videos)
    #
    #
    # # get the recent 20 videos liked by a user
    # print("get the recent 20 videos liked by a user")
    # liked_videos = get_like_history(mid)
    # for video in liked_videos:
    #     print(video)
    #

