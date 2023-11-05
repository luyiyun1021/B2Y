from django.http import HttpResponse, HttpRequest, JsonResponse
from pyyoutube import Client
import bili2youtube.youtube_utils as youtube_utils
from bili2youtube.models import UserIDMapping, VideoIDMapping
import requests
import bili2youtube.bilibili_utils.uploader as bili_utils_u
import bili2youtube.bilibili_utils.viewer as bili_utils_v
def migrate_helloworld(request: HttpRequest) -> HttpResponse:
    mid = "1794123514"
    all_videos = bili_utils_u.get_all_videos_with_detailed_info(mid)
    all_series_with_video_ids = bili_utils_u.get_all_series_list_with_video_ids(mid)
    data = {
        'videos': all_videos,
        'sets': all_series_with_video_ids,
    }
    return JsonResponse({"status": "success", "data": data})
    # return HttpResponse("hello world!")
    # return JsonResponse({"status": "success", "data": "hello world!"})
def migrate_uploader(request: HttpRequest) -> HttpResponse:
    try:
        ### TODO: Get Bilibili UID
        buid = ""

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

        ### TODO: Download Bilibili videos
        ### sample videos
        bvideos = [
            youtube_utils.VideoInfo(
                filename="",
                title="",
                platform=youtube_utils.Platform.BILIBILI,
                id="bvid00000",
                description="",
                tags=[],
                privacyStatus="private",
            )
        ]

        ### Upload Bilibili videos to YouTube, use multi-processing to speed up
        yvideo_ids = youtube_utils.upload_videos(youtube_client, bvideos)

        ### Store the map between Bilibili UID and YouTube UID
        for yvideo_id, bvideo in zip(yvideo_ids, bvideos):
            if (
                not VideoIDMapping.objects.filter(bvid=bvideo.id).exists()
                and not VideoIDMapping.objects.filter(yvid=yvideo_id).exists()
            ):
                VideoIDMapping.objects.create(bvid=bvideo.id, yvid=yvideo_id)

        ### TODO: Get Bilbili playlists
        ### sample playlists
        bplaylists = [
            youtube_utils.PlaylistInfo(
                title="",
                description="",
                tags=[],
                defaultLanguage="en",
                privacyStatus="private",
                platform=youtube_utils.Platform.BILIBILI,
                videoList=["bvid00000"],
            )
        ]

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