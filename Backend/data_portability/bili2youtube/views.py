from django.http import HttpResponse, HttpRequest, JsonResponse
from pyyoutube import Client
import bili2youtube.youtube_utils as youtube_utils
from bili2youtube.models import UserIDMapping, VideoIDMapping
import requests
import bili2youtube.bilibili_utils.uploader as bili_utils_u
import bili2youtube.bilibili_utils.viewer as bili_utils_v

VIDEO_DOWNLOAD_PATH = "/Users/ziranmin/Downloads/"
VIDEO_DOWNLOAD_QUALITY_ID = 32 # 清晰度参考 https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/video/videostream_url.md

def migrate_uploader(request: HttpRequest) -> HttpResponse:
    try:
        b_session_data = request.GET.get("SESSDATA")
        user = bili_utils_u.get_user_info(b_session_data)
        # Get Bilibili UID
        buid = user['mid']

        ### Initialize YouTube client
        youtube_access_token = request.GET.get("youtube_access_token")
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
        bvideos = bili_utils_u.get_and_download_all_videos_from_bilibili_for_youtube(buid, session_id=b_session_data, qn=VIDEO_DOWNLOAD_QUALITY_ID, path=VIDEO_DOWNLOAD_PATH)

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
            yplaylist = bplaylist.copy()
            yplaylist.platform = youtube_utils.Platform.YOUTUBE
            for bvid in bplaylist.videoList:
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


def migrate_viewer(request: HttpRequest) -> HttpResponse:
    b_session_data = request.GET.get("SESSDATA")
    y_access_token = request.GET.get("access_token")
    user = bili_utils_u.get_user_info(b_session_data)
    mid = user['mid']

    try:
        # Get Bilibili subscription list
        following_list = bili_utils_v.get_followings_list(mid, session_id=b_session_data)
        bsub_list = []
        for x in following_list:
            bsub_list.append(x['mid'])

        # Get Bilbili playlists
        bplaylists = bili_utils_v.create_youtube_playlist_for_viewer(mid, session_id=b_session_data)

        # Get Bilibili ratings
        liked_videos = bili_utils_v.get_like_history(mid)
        bratings = []
        for video in liked_videos:
            bratings.append((video['bvid'], 'like'))

        ### Initialize YouTube client
        youtube_access_token = request.GET.get("youtube_access_token")
        youtube_client = Client(access_token=youtube_access_token)

        ### migrate subscription list
        for buid in bsub_list:
            if UserIDMapping.objects.filter(buid=buid).exists():
                yuid = UserIDMapping.objects.get(buid=buid).yuid
                youtube_utils.subscribe_youtube_channel(youtube_client, yuid)

        ### migrate playlists
        for bplaylist in bplaylists:
            yplaylist = bplaylist.copy()
            yplaylist.platform = youtube_utils.Platform.YOUTUBE
            for bvid in bplaylist.videoList:
                if VideoIDMapping.objects.filter(bvid=bvid).exists():
                    yvid = VideoIDMapping.objects.get(bvid=bvid).yvid
                    yplaylist.videoList.append(yvid)
            youtube_utils.create_new_youtube_playlist(youtube_client, yplaylist)

        ### migrate ratings
        for brating in bratings:
            bvid, rating = brating
            if VideoIDMapping.objects.filter(bvid=bvid).exists():
                yvid = VideoIDMapping.objects.get(bvid=bvid).yvid
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
        return JsonResponse(requests.get("https://passport.bilibili.com/x/passport-login/web/qrcode/generate").json(), safe=False)
    except Exception as e:
        # traceback.print_exc(e)
        response = {}
        response["result"] = "error_bad_datasource"
        response["data"] = e.__str__()
        print(e.__str__())
        return JsonResponse(response)

def check_Bilibili_QRcode(request: HttpRequest) -> HttpResponse:
    try:
        data = requests.get(f'https://passport.bilibili.com/x/passport-login/web/qrcode/poll?qrcode_key={request.GET.get("qrcode_key")}')
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
        b_session_data = request.GET.get("SESSDATA")
        y_access_token = request.GET.get("access_token")
        user = bili_utils_u.get_user_info(b_session_data)
        mid = user['mid']
        all_videos = bili_utils_u.get_all_videos_with_detailed_info(mid)
        all_series_with_video_ids = bili_utils_u.get_all_series_list_with_video_ids(mid)
        data = {
            'videos': all_videos,
            'sets': all_series_with_video_ids,
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
        b_session_data = request.GET.get("SESSDATA")
        y_access_token = request.GET.get("access_token")
        # TODO
        # data = {
        # videos: [ ### Same as uploader videos, includes all videos in all playlist
        #     {
        #     id: "BV1LC4y1Z7Li",
        #     bvid: "BV1LC4y1Z7Li",
        #     aid: 789284286,
        #     cid: 1291466320,
        #     title: "Foggy Brown",
        #     desc: "Bronw University Main Green on a foggy data",
        #     img: "http://i2.hdslb.com/bfs/archive/4632e780d3411dccd8fd6758e7d39968449cebf5.jpg",
        #     owner_mid: 1794123514,
        #     owner_name: "robertmin96",
        #     view: 6,
        #     like: 0,
        #     star: 0,
        #     share: 0,
        #     comment: 1,
        #     disable: false,
        #     checked: false,
        #     },
        # ],
        # sets: [
        #     {
        #     id: 3737408,
        #     title: "list3",
        #     video_ids: ["BV1LC4y1Z7Li"], ### same as uploader, only need id
        #     },
        #     {
        #     id: 3737407,
        #     title: "list2",
        #     video_ids: ["BV1y8411C7Mw"],
        #     },
        #     {
        #     id: 3670927,
        #     title: "list1",
        #     video_ids: ["BV1LC4y1Z7Li", "BV1y8411C7Mw"],
        #     },
        # ],
        # likes: [ ### same as uploader's videos, all infomation need.
        #     {
        #     id: "BV1LC4y1Z7Li",
        #     bvid: "BV1LC4y1Z7Li",
        #     aid: 789284286,
        #     cid: 1291466320,
        #     title: "Foggy Brown",
        #     desc: "Bronw University Main Green on a foggy data",
        #     img: "http://i2.hdslb.com/bfs/archive/4632e780d3411dccd8fd6758e7d39968449cebf5.jpg",
        #     owner_mid: 1794123514,
        #     owner_name: "robertmin96",
        #     view: 6,
        #     like: 0,
        #     star: 0,
        #     share: 0,
        #     comment: 1,
        #     disable: false,
        #     checked: false,
        #     },
        # ],
        # follow: [
        #     { id: "1", name: "xxx", img: "img", disable: false, checked: false },
        #     { id: "2", name: "yyy", img: "img", disable: false, checked: false },
        #     { id: "3", name: "zzz", img: "img", disable: false, checked: false },
        # ],
        # };

        return JsonResponse({"status": "success", "data": data})
    except Exception as e:
        # traceback.print_exc(e)
        response = {}
        response["result"] = "error_bad_datasource"
        response["data"] = e.__str__()
        print(e.__str__())
        return JsonResponse(response)