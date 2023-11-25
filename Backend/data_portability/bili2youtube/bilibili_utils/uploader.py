import requests
import math
import subprocess
import time
import concurrent.futures
import traceback
from fake_useragent import UserAgent
import os
from ..youtube_utils import *
from bili2youtube.bilibili_utils.wbi import getSignedParams
from bili2youtube.bilibili_utils.header_gen import generate_headers
from bili2youtube.models import VideoIDMapping, UserIDMapping

# from Backend.data_portability.bili2youtube.youtube_utils import *

SESSION_ID = ""
VIDEO_DOWNLOAD_PATH = os.path.join(os.environ["HOME"], "Downloads/")
VIDEO_DOWNLOAD_QUALITY_ID = 32  # 清晰度参考 https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/video/videostream_url.md
ENABLE_MULTI_THREAD = True


def get_user_info(session_id=SESSION_ID):
    url = "https://api.bilibili.com/x/web-interface/nav"
    cookies = {"SESSDATA": session_id}
    try:
        params = getSignedParams({})
        headers = generate_headers(f"SESSDATA={session_id}")
        response = requests.get(url, cookies=cookies, params=params, headers=headers)
        response.raise_for_status()
        json_response = response.json()
        user = {}
        user["uname"] = json_response["data"]["uname"]
        user["mid"] = json_response["data"]["mid"]
        user["profile_pic"] = json_response["data"]["face"]
        return user

    except Exception as error:
        print("An exception occurred:", type(error).__name__, "–", error)
        traceback.print_stack()


def get_all_videos(mid):
    """

    :param mid: user id
    :return:
    """
    # agent_set = set()
    # first_agent = ua.random
    # agent_set.add(first_agent)

    base_url = f"https://api.bilibili.com/x/space/wbi/arc/search?mid={mid}&ps=30&pn=1"
    # headers = {
    #     # 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    #     'Referer': f'https://space.bilibili.com/{mid}/video',
    #     # 'Referer': f'https://space.bilibili.com/',
    #     # "User-Agent": first_agent,
    #     "User-Agent": ua.random,
    # }

    # time.sleep(2)

    try:
        response = requests.get(base_url, headers=generate_headers())
        json_response = response.json()

        # print(json_response)

        res = []
        total_videos = json_response["data"]["page"]["count"]
        page_size = json_response["data"]["page"]["ps"]
        total_pages = math.ceil(total_videos / page_size)

        # print("total_pages", total_pages)
        for page in range(1, total_pages + 1):
            # print('page: ', page)
            url = f"https://api.bilibili.com/x/space/wbi/arc/search?mid={mid}&ps=30&pn={page}"

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

            response = requests.get(url, headers=generate_headers())
            json_response = response.json()
            video_list = json_response["data"]["list"]["vlist"]
            for v in video_list:
                res.append(
                    {
                        "bvid": v["bvid"],
                        "aid": v["aid"],
                        "title": v["title"],
                        # 'description': v['description'],
                        # 'pic': v['pic'],
                        # 'play_count': v['play'],
                        # 'created_at': v['created'],
                        # 'owner_mid': v['mid'],
                        # 'owner_name': v['author'],
                    }
                )
            time.sleep(0.5)

        return res

    except Exception as error:
        print("An exception occurred:", type(error).__name__, "–", error)


def get_series_lists(mid):
    """

    :param mid: user id
    :return:
    """
    base_url = f"https://api.bilibili.com/x/polymer/web-space/seasons_series_list?mid={mid}&page_num=1&page_size=20"
    try:
        headers = generate_headers()
        response = requests.get(base_url, headers=headers)
        json_response = response.json()

        total_videos = json_response["data"]["items_lists"]["page"]["total"]
        page_size = json_response["data"]["items_lists"]["page"]["page_size"]
        total_pages = math.ceil(total_videos / page_size)

        # print("total_pages", total_pages)
        res = []
        if ENABLE_MULTI_THREAD:
            response_futures = []
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for page in range(1, total_pages + 1):
                    url = f"https://api.bilibili.com/x/polymer/web-space/seasons_series_list?mid={mid}&page_num={page}&page_size={page_size}"
                    future = executor.submit(requests.get, url, headers=headers)
                    response_futures.append(future)

            for response_future in response_futures:
                response = response_future.result()
                json_response = response.json()
                series_list = json_response["data"]["items_lists"]["series_list"]
                for item in series_list:
                    res.append(
                        {
                            "series_id": item["meta"]["series_id"],
                            "name": item["meta"]["name"],
                            "description": item["meta"]["description"],
                        }
                    )
        else:  # single thread
            for page in range(1, total_pages + 1):
                url = f"https://api.bilibili.com/x/polymer/web-space/seasons_series_list?mid={mid}&page_num={page}&page_size={page_size}"
                response = requests.get(url, headers=headers)
                json_response = response.json()
                series_list = json_response["data"]["items_lists"]["series_list"]
                for item in series_list:
                    res.append(
                        {
                            "series_id": item["meta"]["series_id"],
                            "name": item["meta"]["name"],
                            "description": item["meta"]["description"],
                        }
                    )
        return res

    except Exception as error:
        print("An exception occurred:", type(error).__name__, "–", error)


def get_series_list_videos(mid, series_id):
    base_url = f"https://api.bilibili.com/x/series/archives?mid={mid}&series_id={series_id}&only_normal=true&sort=desc&pn=1&ps=30"
    try:
        response = requests.get(base_url)
        json_response = response.json()

        total_videos = json_response["data"]["page"]["total"]
        page_size = json_response["data"]["page"]["size"]
        total_pages = math.ceil(total_videos / page_size)

        # print("total_pages", total_pages)
        res = []

        for page in range(1, total_pages + 1):
            url = f"https://api.bilibili.com/x/series/archives?mid={mid}&series_id={series_id}&only_normal=true&sort=desc&pn={page}&ps={page_size}"
            response = requests.get(url)
            json_response = response.json()
            for item in json_response["data"]["archives"]:
                # each video has two types of id, aid and bvid, we store both of them, but we primarily use bvid
                res.append(
                    {
                        "bvid": item["bvid"],
                        "aid": item["aid"],
                        "title": item["title"],
                    }
                )
        return res

    except Exception as error:
        print("An exception occurred:", type(error).__name__, "–", error)


def get_video_info(bvid):
    """

    :param bvid: video id
    :return:
    """
    url = "https://api.bilibili.com/x/web-interface/view"
    # params = {"bvid": bvid}
    try:
        params = {"bvid": bvid}
        response = requests.get(url, params=params, headers=generate_headers())
        response.raise_for_status()
        json_response = response.json()
        # video = {'bvid': bvid}
        data = json_response["data"]
        # print(json.dumps(json_response, indent=4, sort_keys=True))
        video = {
            "id": bvid,
            "bvid": bvid,
            "aid": data["aid"],
            "cid": data["cid"],
            "title": data["title"],
            "desc": data["desc"],
            "img": data["pic"],
            "owner_mid": data["owner"]["mid"],
            "owner_name": data["owner"]["name"],
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
        traceback.print_stack()


def get_video_tags(bvid, session_id=SESSION_ID):
    url = "https://api.bilibili.com/x/tag/archive/tags"
    params = {"bvid": bvid}
    cookies = {"SESSDATA": session_id}
    try:
        response = requests.get(url, params=params, cookies=cookies)
        tags = []
        json_response = response.json()
        data = json_response["data"]
        for item in data:
            tags.append(item["tag_name"])
        return tags
    except Exception as error:
        print("An exception occurred:", type(error).__name__, "–", error)


def get_video_source_link(
    bvid, cid, qn=VIDEO_DOWNLOAD_QUALITY_ID, session_id=SESSION_ID
):
    url = "https://api.bilibili.com/x/player/playurl"
    params = {
        "bvid": bvid,
        "cid": cid,
        "qn": qn,
        "fnval": "0",
        "fnver": "0",
        "fourk": "1",
    }
    cookies = {"SESSDATA": session_id}
    try:
        response = requests.get(url, params=params, cookies=cookies)
        tags = []
        json_response = response.json()
        data = json_response["data"]
        return data["durl"][0]["url"]
    except Exception as error:
        print("An exception occurred:", type(error).__name__, "–", error)


def download_video(
    bvid, video_url, qn=VIDEO_DOWNLOAD_QUALITY_ID, path=VIDEO_DOWNLOAD_PATH
):
    video_name = bvid + "_" + str(qn) + ".mp4"
    full_path = path + video_name
    cmd = ["wget", video_url, "--referer", "https://www.bilibili.com", "-O", full_path]
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


def get_all_videos_with_detailed_info(mid, youtube_client):
    try:
        all_video_id_list = get_all_videos(mid)
        res = []
        if ENABLE_MULTI_THREAD:
            video_info_futures = []
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for v in all_video_id_list:
                    future = executor.submit(get_video_info, v["bvid"])
                    video_info_futures.append(future)
            for future in concurrent.futures.as_completed(video_info_futures):
                video_info = future.result()
                not_exist = not VideoIDMapping.objects.filter(
                    bvid=video_info["bvid"]
                ).exists()
                checked = (
                    is_uploaded(
                        youtube_client,
                        VideoIDMapping.objects.get(bvid=video_info["bvid"]).yvid,
                    )
                    if not not_exist
                    else False
                )
                video_info["checked"] = checked
                video_info["disable"] = checked
                res.append(video_info)
        else:
            for v in all_video_id_list:
                video_info = get_video_info(v["bvid"])
                not_exist = not VideoIDMapping.objects.filter(bvid=v["bvid"]).exists()
                checked = (
                    is_uploaded(
                        youtube_client, VideoIDMapping.objects.get(bvid=v["bvid"]).yvid
                    )
                    if not not_exist
                    else False
                )
                video_info["checked"] = checked
                video_info["disable"] = checked
                res.append(video_info)
        return res
    except Exception as error:
        print("An exception occurred:", type(error).__name__, "–", error)


def get_all_series_list_with_video_ids(mid):
    try:
        res = []
        series_lists = get_series_lists(mid)
        if ENABLE_MULTI_THREAD:
            ser_list_futures = []
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for ser_list in series_lists:
                    future = executor.submit(
                        get_series_list_videos, mid, ser_list["series_id"]
                    )
                    ser_list_futures.append(future)
            i = 0
            for ser_list_future in ser_list_futures:
                series_videos = ser_list_future.result()
                video_ids = []
                for v in series_videos:
                    video_ids.append(v["bvid"])
                temp = {
                    "id": series_lists[i]["series_id"],
                    "title": series_lists[i]["name"],
                    "desc": series_lists[i]["description"],
                    "video_ids": video_ids,
                }
                res.append(temp)
                i += 1
        else:
            for ser_list in series_lists:
                series_id = ser_list["series_id"]
                video_ids = []
                series_videos = get_series_list_videos(mid, ser_list["series_id"])
                for v in series_videos:
                    video_ids.append(v["bvid"])

                temp = {
                    "id": series_id,
                    "title": ser_list["name"],
                    "desc": ser_list["description"],
                    "video_ids": video_ids,
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
            series_id = series["series_id"]
            videos = get_series_list_videos(mid, series_id)
            youtube_video_list = []
            for video in videos:
                youtube_video_list.append(video["bvid"])
            playlist = PlaylistInfo(
                title=series["name"],
                description=series["description"],
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


def get_and_download_all_videos_from_bilibili_for_youtube(
    mid, session_id=SESSION_ID, qn=VIDEO_DOWNLOAD_QUALITY_ID, path=VIDEO_DOWNLOAD_PATH
) -> list[VideoInfo]:
    try:
        bvideos = []
        all_video_list = get_all_videos(mid)
        for video in all_video_list:
            bvid = video["bvid"]
            video_info = get_video_info(bvid)
            video_tags = get_video_tags(bvid, session_id)
            cid = video_info["cid"]

            vurl = get_video_source_link(bvid, cid)
            download_video(bvid, vurl, qn, path)

            youtube_video = VideoInfo(
                filename=VIDEO_DOWNLOAD_PATH
                + bvid
                + "_"
                + str(VIDEO_DOWNLOAD_QUALITY_ID)
                + ".mp4",
                title=video_info["title"],
                platform=Platform.BILIBILI,
                id=bvid,
                description=video_info["desc"],
                tags=video_tags,
                privacyStatus="public",
            )
            bvideos.append(youtube_video)
        return bvideos
    except Exception as error:
        print("An exception occurred:", type(error).__name__, "–", error)


def get_and_download_video_from_bilibili_for_youtube(
    bvid, session_id=SESSION_ID, qn=VIDEO_DOWNLOAD_QUALITY_ID, path=VIDEO_DOWNLOAD_PATH
):
    try:
        video_info = get_video_info(bvid)
        video_tags = get_video_tags(bvid, session_id)
        cid = video_info["cid"]
        vurl = get_video_source_link(bvid, cid)
        download_video(bvid, vurl, qn, path)
        youtube_video = VideoInfo(
            filename=VIDEO_DOWNLOAD_PATH
            + bvid
            + "_"
            + str(VIDEO_DOWNLOAD_QUALITY_ID)
            + ".mp4",
            title=video_info["title"],
            platform=Platform.BILIBILI,
            id=bvid,
            description=video_info["desc"],
            tags=video_tags,
            privacyStatus="public",
        )
        return youtube_video
    except Exception as error:
        print("An exception occurred:", type(error).__name__, "–", error)


if __name__ == "__main__":
    print("hello world")

    mid = "1794123514"

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
