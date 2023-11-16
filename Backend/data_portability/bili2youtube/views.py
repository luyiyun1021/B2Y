import json
from django.http import HttpResponse, HttpRequest, JsonResponse
from pyyoutube import Client
import bili2youtube.youtube_utils as youtube_utils
from bili2youtube.models import UserIDMapping, VideoIDMapping
import requests
import bili2youtube.bilibili_utils.uploader as bili_utils_u
import bili2youtube.bilibili_utils.viewer as bili_utils_v

VIDEO_DOWNLOAD_PATH = "/Users/ziranmin/Downloads/"
VIDEO_DOWNLOAD_QUALITY_ID = 32  # 清晰度参考 https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/video/videostream_url.md


def migrate_uploader(request: HttpRequest) -> HttpResponse:
    try:
        b_session_data = request.GET.get("SESSDATA")
        body_unicode = request.body.decode("utf-8")
        body = json.loads(body_unicode)
        videos_ids = body.get("videos")
        sets_ids = body.get("sets")
        # TDOD migration...

        user = bili_utils_u.get_user_info(b_session_data)
        # Get Bilibili UID
        buid = user["mid"]

        ### Initialize YouTube client
        youtube_access_token = request.GET.get("access_token")
        youtube_client = Client(access_token=youtube_access_token)

        ## Get Youtube channel ID
        yuid = youtube_utils.get_channel_id(youtube_client)

        ### Store the map between Bilibili UID and YouTube UID
        if (
            not UserIDMapping.objects.filter(buid=buid).exists()
            and not UserIDMapping.objects.filter(yuid=yuid).exists()
        ):
            UserIDMapping.objects.create(buid=buid, yuid=yuid)
        else:
            return JsonResponse(
                {"status": "success", "data": "Already migrated this user!"}
            )

        # Download Bilibili videos
        bvideos = bili_utils_u.get_and_download_all_videos_from_bilibili_for_youtube(
            buid,
            session_id=b_session_data,
            qn=VIDEO_DOWNLOAD_QUALITY_ID,
            path=VIDEO_DOWNLOAD_PATH,
        )

        ### Upload Bilibili videos to YouTube, use multi-processing to speed up
        yvideo_ids = youtube_utils.upload_videos(youtube_client, bvideos)

        ### Store the map between Bilibili UID and YouTube UID
        for yvideo_id, bvideo in zip(yvideo_ids, bvideos):
            if (
                not VideoIDMapping.objects.filter(bvid=bvideo.id).exists()
                and not VideoIDMapping.objects.filter(yvid=yvideo_id).exists()
            ):
                VideoIDMapping.objects.create(bvid=bvideo.id, yvid=yvideo_id)

        # Get Bilbili playlists
        bplaylists = bili_utils_u.create_youtube_playlist_for_uploader(buid)

        ### Migrate uploader's playlists
        for bplaylist in bplaylists:
            bVideoList = bplaylist.videoList.copy()
            yplaylist = bplaylist
            yplaylist.videoList = []
            yplaylist.platform = youtube_utils.Platform.YOUTUBE
            for bvid in bVideoList:
                if VideoIDMapping.objects.filter(bvid=bvid).exists():
                    yvid = VideoIDMapping.objects.get(bvid=bvid).yvid
                    yplaylist.videoList.append(yvid)
            youtube_utils.create_new_youtube_playlist(youtube_client, yplaylist)

        return JsonResponse({"status": "success", "data": "Hello, world!"})
    except Exception as e:
        # traceback.print_exc(e)
        response = {}
        response["result"] = "error_bad_datasource"
        response["data"] = e.__str__()
        print(e.__str__())
        return JsonResponse(response)


def migrate_uploader_all(request: HttpRequest) -> HttpResponse:
    try:
        b_session_data = request.GET.get("SESSDATA")
        user = bili_utils_u.get_user_info(b_session_data)
        # Get Bilibili UID
        buid = user["mid"]
        ### Initialize YouTube client
        youtube_access_token = request.GET.get("access_token")
        youtube_client = Client(access_token=youtube_access_token)

        ## Get Youtube channel ID
        yuid = youtube_utils.get_channel_id(youtube_client)

        # Download Bilibili videos
        bvideos = bili_utils_u.get_and_download_all_videos_from_bilibili_for_youtube(
            buid,
            session_id=b_session_data,
            qn=VIDEO_DOWNLOAD_QUALITY_ID,
            path=VIDEO_DOWNLOAD_PATH,
        )

        ### Upload Bilibili videos to YouTube, use multi-processing to speed up
        yvideo_ids = youtube_utils.upload_videos(youtube_client, bvideos)

        ### Store the map between Bilibili UID and YouTube UID
        for yvideo_id, bvideo in zip(yvideo_ids, bvideos):
            if (
                not VideoIDMapping.objects.filter(bvid=bvideo.id).exists()
                and not VideoIDMapping.objects.filter(yvid=yvideo_id).exists()
            ):
                VideoIDMapping.objects.create(bvid=bvideo.id, yvid=yvideo_id)

        # Get Bilbili playlists
        bplaylists = bili_utils_u.create_youtube_playlist_for_uploader(buid)

        ### Migrate uploader's playlists
        for bplaylist in bplaylists:
            bVideoList = bplaylist.videoList.copy()
            yplaylist = bplaylist
            yplaylist.videoList = []
            yplaylist.platform = youtube_utils.Platform.YOUTUBE
            for bvid in bVideoList:
                if VideoIDMapping.objects.filter(bvid=bvid).exists():
                    yvid = VideoIDMapping.objects.get(bvid=bvid).yvid
                    yplaylist.videoList.append(yvid)
            youtube_utils.create_new_youtube_playlist(youtube_client, yplaylist)

        ### Store the map between Bilibili UID and YouTube UID
        if (
            not UserIDMapping.objects.filter(buid=buid).exists()
            and not UserIDMapping.objects.filter(yuid=yuid).exists()
        ):
            UserIDMapping.objects.create(buid=buid, yuid=yuid)
        elif UserIDMapping.objects.filter(buid=buid).exists():
            UserIDMapping.objects.filter(buid=buid).update(yuid=yuid)
        elif UserIDMapping.objects.filter(yuid=yuid).exists():
            UserIDMapping.objects.filter(yuid=yuid).update(buid=buid)

        return JsonResponse({"status": "success", "data": "Hello, world!"})
    except Exception as e:
        # traceback.print_exc(e)
        response = {}
        response["result"] = "error_bad_datasource"
        response["data"] = e.__str__()
        print(e.__str__())
        return JsonResponse(response)


def migrate_viewer(request: HttpRequest) -> HttpResponse:
    b_session_data = request.GET.get("SESSDATA")
    youtube_access_token = request.GET.get("access_token")
    body_unicode = request.body.decode("utf-8")
    body = json.loads(body_unicode)
    sets_ids = body.get("sets")
    likes_ids = body.get("likes")
    follow_ids = body.get("follow")
    # TDOD migration...

    user = bili_utils_u.get_user_info(b_session_data)
    mid = user["mid"]

    try:
        # Get Bilibili subscription list
        following_list = bili_utils_v.get_followings_list(
            mid, session_id=b_session_data
        )
        bsub_list = []
        for x in following_list:
            bsub_list.append(x["id"])

        # Get Bilbili playlists
        bplaylists = bili_utils_v.create_youtube_playlist_for_viewer(
            mid, session_id=b_session_data
        )

        # Get Bilibili ratings
        liked_videos = bili_utils_v.get_like_history(mid)
        bratings = []
        for video in liked_videos:
            bratings.append((video["bvid"], "like"))

        ### Initialize YouTube client
        youtube_client = Client(access_token=youtube_access_token)

        ### migrate subscription list
        for buid in bsub_list:
            if UserIDMapping.objects.filter(buid=buid).exists():
                yuid = UserIDMapping.objects.get(buid=buid).yuid
                youtube_utils.subscribe_youtube_channel(youtube_client, yuid)

        ### migrate playlists
        for bplaylist in bplaylists:
            bVideoList = bplaylist.videoList.copy()
            yplaylist = bplaylist
            yplaylist.videoList = []
            yplaylist.platform = youtube_utils.Platform.YOUTUBE
            for bvid in bVideoList:
                if VideoIDMapping.objects.filter(bvid=bvid).exists():
                    yvid = VideoIDMapping.objects.get(bvid=bvid).yvid
                    yplaylist.videoList.append(yvid)
            youtube_utils.create_new_youtube_playlist(youtube_client, yplaylist)

        ### migrate ratings
        for brating in bratings:
            bvid, rating = brating
            if VideoIDMapping.objects.filter(bvid=bvid).exists():
                yvid = VideoIDMapping.objects.get(bvid=bvid).yvid
                print(yvid)
                youtube_utils.rate_video(youtube_client, yvid, rating)
        return JsonResponse({"status": "success", "data": "Hello, world!"})
    except Exception as e:
        # traceback.print_exc(e)
        response = {}
        response["result"] = "error_bad_datasource"
        response["data"] = e.__str__()
        print(e.__str__())
        return JsonResponse(response)


def migrate_viewer_all(request: HttpRequest) -> HttpResponse:
    b_session_data = request.GET.get("SESSDATA")
    youtube_access_token = request.GET.get("access_token")
    user = bili_utils_u.get_user_info(b_session_data)
    mid = user["mid"]

    try:
        # Get Bilibili subscription list
        following_list = bili_utils_v.get_followings_list(
            mid, session_id=b_session_data
        )
        bsub_list = []
        for x in following_list:
            bsub_list.append(x["id"])

        # Get Bilbili playlists
        bplaylists = bili_utils_v.create_youtube_playlist_for_viewer(
            mid, session_id=b_session_data
        )

        # Get Bilibili ratings
        liked_videos = bili_utils_v.get_like_history(mid)
        bratings = []
        for video in liked_videos:
            bratings.append((video["bvid"], "like"))

        ### Initialize YouTube client
        youtube_client = Client(access_token=youtube_access_token)

        ### migrate subscription list
        for buid in bsub_list:
            if UserIDMapping.objects.filter(buid=buid).exists():
                yuid = UserIDMapping.objects.get(buid=buid).yuid
                youtube_utils.subscribe_youtube_channel(youtube_client, yuid)

        ### migrate playlists
        for bplaylist in bplaylists:
            bVideoList = bplaylist.videoList.copy()
            yplaylist = bplaylist
            yplaylist.videoList = []
            yplaylist.platform = youtube_utils.Platform.YOUTUBE
            for bvid in bVideoList:
                if VideoIDMapping.objects.filter(bvid=bvid).exists():
                    yvid = VideoIDMapping.objects.get(bvid=bvid).yvid
                    yplaylist.videoList.append(yvid)
            youtube_utils.create_new_youtube_playlist(youtube_client, yplaylist)

        ### migrate ratings
        for brating in bratings:
            bvid, rating = brating
            if VideoIDMapping.objects.filter(bvid=bvid).exists():
                yvid = VideoIDMapping.objects.get(bvid=bvid).yvid
                print(yvid)
                youtube_utils.rate_video(youtube_client, yvid, rating)

        return JsonResponse({"status": "success", "data": "Hello, world!"})
    except Exception as e:
        # traceback.print_exc(e)
        response = {}
        response["result"] = "error_bad_datasource"
        response["data"] = e.__str__()
        print(e.__str__())
        return JsonResponse(response)


def get_Bilibili_QRcode(request: HttpRequest) -> HttpResponse:
    try:
        return JsonResponse(
            requests.get(
                "https://passport.bilibili.com/x/passport-login/web/qrcode/generate"
            ).json(),
            safe=False,
        )
    except Exception as e:
        # traceback.print_exc(e)
        response = {}
        response["result"] = "error_bad_datasource"
        response["data"] = e.__str__()
        print(e.__str__())
        return JsonResponse(response)


def check_Bilibili_QRcode(request: HttpRequest) -> HttpResponse:
    try:
        data = requests.get(
            f'https://passport.bilibili.com/x/passport-login/web/qrcode/poll?qrcode_key={request.GET.get("qrcode_key")}'
        )
        json = data.json()
        json["data"]["SESSDATA"] = data.cookies.get_dict()["SESSDATA"]
        return JsonResponse(json, safe=False)
    except Exception as e:
        # traceback.print_exc(e)
        response = {}
        response["result"] = "error_bad_datasource"
        response["data"] = e.__str__()
        print(e.__str__())
        return JsonResponse(response)


def B2Y_get_uploader_info(request: HttpRequest) -> HttpResponse:
    try:
        y_access_token = request.GET.get("access_token")
        youtube_client = Client(access_token=y_access_token)

        b_session_data = request.GET.get("SESSDATA")
        b_session_data = "cda35e2e%2C1713064715%2Cc8245%2Aa1CjAKIiBK7h1tvo8DlV7C4IGmQVcDIFk_rvrkUqo3YvlwD6jiR3gUEKUn8FyFRdrUf7USVmd0Z3FBTFhLeFVwQmpISkg5emdJX2l5YkNsVW93cGhkMk9tSHhCZ3htR0RVbDFzR3ZUdW9fSE5YdjJmQl9La29VaWFMWlFMMkxLUDFjU2N3NVdTbU5nIIEC"
        user = bili_utils_u.get_user_info(b_session_data)
        mid = user["mid"]
        all_videos = bili_utils_u.get_all_videos_with_detailed_info(mid)
        all_series_with_video_ids = bili_utils_u.get_all_series_list_with_video_ids(mid)
        data = {
            "b_user_name": user["uname"],
            "b_user_profile": user["profile_pic"],
            "videos": all_videos,
            "sets": all_series_with_video_ids,
            "y_user_name": youtube_utils.get_channel_name(youtube_client),
            "y_user_profile": youtube_utils.get_channel_thumbnail(youtube_client),
        }
        return JsonResponse({"status": "success", "data": data})
    except Exception as e:
        # traceback.print_exc(e)
        response = {}
        response["result"] = "error_bad_datasource"
        response["data"] = e.__str__()
        print(e.__str__())
        return JsonResponse(response)


def B2Y_get_viewer_info(request: HttpRequest) -> HttpResponse:
    try:
        y_access_token = request.GET.get("access_token")
        youtube_client = Client(access_token=y_access_token)
        b_session_data = request.GET.get("SESSDATA")
        b_session_data = "bcece945%2C1715697192%2Cda0e6%2Ab2CjAihC-Qf3pszWTFWI9ZHETJgwNB6VSzXkUoZbWs23LxrHXGexvEGDKhdbbdpmIWAI8SVmtaa3p3LVlTVEp4Z20xOTVkczdSX1lpcnRSNFJsQjF2clJPSmRpRERnWTMxTWRHNENTanhuVkpNS2ItNFd3VVFkLW5LRUNzTHFJX28telc5NzRxeFpBIIEC"
        user = bili_utils_u.get_user_info(b_session_data)
        mid = user["mid"]
        videos, sets = bili_utils_v.get_collections_with_video_ids_and_all_videos_info(
            mid, session_id=b_session_data
        )
        likes = bili_utils_v.get_like_history(mid)
        follow = bili_utils_v.get_followings_list(mid, session_id=b_session_data)
        data = {
            "b_user_name": user["uname"],
            "b_user_profile": user["profile_pic"],
            "videos": videos,
            "sets": sets,
            "likes": likes,
            "follow": follow,
            "y_user_name": youtube_utils.get_channel_name(youtube_client),
            "y_user_profile": youtube_utils.get_channel_thumbnail(youtube_client),
        }
        return JsonResponse({"status": "success", "data": data})
    except Exception as e:
        # traceback.print_exc(e)
        response = {}
        response["result"] = "error_bad_datasource"
        response["data"] = e.__str__()
        print(e.__str__())
        return JsonResponse(response)
