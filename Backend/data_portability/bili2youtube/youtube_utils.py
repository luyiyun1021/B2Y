from pyyoutube import Client
import pyyoutube.models as mds
from pyyoutube.media import Media
import multiprocessing
from enum import Enum
import json


def get_subscription_id_list(client: Client) -> list[str]:
    sub_list = client.subscriptions.list(mine=True, parts=["snippet"], return_json=True)
    ret = []
    # print(json.dumps(sub_list["items"], indent=4))
    for item in sub_list["items"]:
        ret.append(item["id"])
    print(f"Subscription ID list: {ret}")
    return ret


def subscribe_youtube_channel(client: Client, channel_id: str) -> str:
    try:
        ret = client.subscriptions.insert(
            part="snippet",
            body={
                "snippet": {
                    "resourceId": {"kind": "youtube#channel", "channelId": channel_id}
                }
            },
            return_json=True,
        )
        ret = ret["id"]
        # print(json.dumps(ret, indent=4))
        print(f'Channel "{ret}" subscribed successfully.')
        return ret
    except Exception as e:
        print(e)
        return None


def unsubscribe_youtube_channel(client: Client, channel_id: str):
    try:
        ret = client.subscriptions.delete(
            subscription_id=channel_id,
        )
        print(f'Channel "{channel_id}" unsubscribed successfully.')
        return ret
    except Exception as e:
        print(e)
        return None


class Platform(Enum):
    DEFAULT = 1
    YOUTUBE = 2
    BILIBILI = 3


class VideoInfo:
    def __init__(
        self,
        filename: str,
        title: str,
        platform: Platform = Platform.DEFAULT,
        id: str = "",
        description: str = "",
        tags: list[str] = [],
        privacyStatus: str = "private",
    ):
        self.filename = filename
        self.title = title
        self.description = description
        self.tags = tags
        self.privacyStatus = privacyStatus
        self.platform = platform
        self.id = id

    def __repr__(self):
        d = (
            "{"
            + "\n"
            + f" 'filename': {self.filename},"
            + "\n"
            + f" 'title': {self.title},"
            + "\n"
            + f" 'platform': {self.platform},"
            + "\n"
            + f" 'id': {self.id},"
            + "\n"
            + f" 'description': {self.description},"
            + "\n"
            + f" 'tags': {self.tags},"
            + "\n"
            + f" 'privacyStatus': {self.privacyStatus},"
            + "\n"
            + "}"
        )
        return d


class PlaylistInfo:
    def __init__(
        self,
        title: str,
        description: str = "",
        tags: list[str] = [],  # B站没有
        defaultLanguage="en",
        privacyStatus: str = "private",
        platform: Platform = Platform.DEFAULT,
        videoList: list[str] = [],
    ):
        self.title = title
        self.description = description
        self.tags = tags
        self.defaultLanguage = defaultLanguage
        self.privacyStatus = privacyStatus
        self.platform = platform
        self.videoList = videoList

    def __repr__(self):
        d = (
            "{"
            + "\n"
            + f" 'title': {self.title},"
            + "\n"
            + f" 'description': {self.description},"
            + "\n"
            + f" 'tags': {self.tags},"
            + "\n"
            + f" 'defaultLanguage': {self.defaultLanguage},"
            + "\n"
            + f" 'privacyStatus': {self.privacyStatus},"
            + "\n"
            + f" 'platform': {self.platform},"
            + "\n"
            + f" 'videoList': {self.videoList},"
            + "\n"
            + "}"
        )
        return d


def create_new_youtube_playlist(
    client: Client,
    playlist_info: PlaylistInfo,
):
    try:
        request_body = {
            "snippet": {
                "title": playlist_info.title,
                "description": playlist_info.description,
                "tags": playlist_info.tags,
                "defaultLanguage": playlist_info.defaultLanguage,
            },
            "status": {"privacyStatus": playlist_info.privacyStatus},
        }
        ret = client.playlists.insert(
            part=["snippet", "status"],
            body=request_body,
            return_json=True,
        )
        ret = ret["id"]
        print(f'Playlist "{ret}" created successfully.')
        for video_id in playlist_info.videoList:
            insert_video_into_playlist(client, ret, video_id)
        return ret
    except Exception as e:
        print(e)
        return None


def get_playlist_id_list(client: Client) -> list[str]:
    sub_list = client.playlists.list(mine=True, parts=["snippet"], return_json=True)
    ret = []
    for item in sub_list["items"]:
        ret.append(item["id"])
    print(f"Playlist ID list: {ret}")
    return ret


def delete_playlist(client: Client, playlist_id: str):
    try:
        ret = client.playlists.delete(
            playlist_id=playlist_id,
        )
        print(f'Playlist "{playlist_id}" deleted successfully.')
        return ret
    except Exception as e:
        print(e)
        return None


def get_video_ids_in_playlist(client: Client, playlist_id: str):
    try:
        play_list_items = client.playlistItems.list(
            playlist_id=playlist_id,
            parts=["snippet"],
            return_json=True,
        )
        # print(json.dumps(play_list_items["items"], indent=4))
        ret = []
        for item in play_list_items["items"]:
            ret.append(item["snippet"]["resourceId"]["videoId"])
        print(f"Video ID list: {ret} in playlist {playlist_id}")
        return ret
    except Exception as e:
        print(e)
        return None


def get_video_ids_in_channel(client: Client) -> list[str]:
    channel_info = client.channels.list(
        mine=True, parts=["snippet", "contentDetails"], return_json=True
    )
    channel_playlist_id = channel_info["items"][0]["contentDetails"][
        "relatedPlaylists"
    ]["uploads"]
    ret = get_video_ids_in_playlist(client, channel_playlist_id)
    return ret


def insert_video_into_playlist(client: Client, playlist_id: str, video_id: str):
    try:
        request_body = {
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {"kind": "youtube#video", "videoId": video_id},
            }
        }
        ret = client.playlistItems.insert(
            part=["snippet"],
            body=request_body,
            return_json=True,
        )
        print(
            f'Video "{video_id}" inserted into playlist "{playlist_id}" successfully.'
        )
        return ret
    except Exception as e:
        print(e)
        return None


def rate_video(client: Client, video_id: str, rating: str = "like"):
    try:
        ret = client.videos.rate(
            video_id=video_id,
            rating=rating,
            return_json=True,
        )
        print(f'Video "{video_id}" rated "{rating}" successfully.')
        return ret
    except Exception as e:
        print(e)
        return None


def upload_video(
    client: Client,
    video_info: VideoInfo,
):
    try:
        body = mds.Video(
            snippet=mds.VideoSnippet(
                title=video_info.title,
                description=video_info.description,
                tags=video_info.tags,
            ),
            status=mds.VideoStatus(privacyStatus=video_info.privacyStatus),
        )
        media = Media(filename=video_info.filename)
        upload = client.videos.insert(
            body=body, media=media, parts=["snippet", "status"], notify_subscribers=True
        )
        video_body = None
        while video_body is None:
            status, video_body = upload.next_chunk()
            if status:
                print(f"Upload progress: {status.progress()}")
        print(f'Video "{video_body["id"]}" uploaded successfully.')
        return video_body["id"]
    except Exception as e:
        print(e)
        return None


def upload_videos(client: Client, video_info_list: list[VideoInfo]):
    with multiprocessing.Pool(processes=len(video_info_list)) as pool:
        results = []
        for video_info in video_info_list:
            results.append(pool.apply_async(upload_video, (client, video_info)))
        ret = [result.get() for result in results]
        print(f"Video ID list: {ret} uploaded successfully.")
        return ret


def delete_video(client: Client, video_id: str):
    try:
        ret = client.videos.delete(
            video_id=video_id,
        )
        print(f'Video "{video_id}" deleted successfully.')
        return ret
    except Exception as e:
        print(e)
        return None


def get_channel_id(client: Client) -> str:
    channel_info = client.channels.list(mine=True, parts=["snippet"], return_json=True)
    channel_id = channel_info["items"][0]["id"]
    print(f"Channel ID: {channel_id}")
    return channel_id


def get_channel_thumbnail(client: Client):
    channel_info = client.channels.list(mine=True, parts=["snippet"], return_json=True)
    return channel_info["items"][0]["snippet"]["thumbnails"]["default"]["url"]


def get_channel_name(client: Client):
    channel_info = client.channels.list(mine=True, parts=["snippet"], return_json=True)
    return channel_info["items"][0]["snippet"]["title"]


def clear_account(client: Client):
    try:
        video_id_list = get_video_ids_in_channel(client)
        for video_id in video_id_list:
            delete_video(client, video_id)
        playlist_id_list = get_playlist_id_list(client)
        for playlist_id in playlist_id_list:
            delete_playlist(client, playlist_id)
        subscription_id_list = get_subscription_id_list(client)
        for subscription_id in subscription_id_list:
            unsubscribe_youtube_channel(client, subscription_id)
        print(f"Account cleared successfully.")
    except Exception as e:
        print(e)
        return None


if __name__ == "__main__":
    ACCESS_TOKEN = ""
    client = Client(access_token=ACCESS_TOKEN)
    clear_account(client)
