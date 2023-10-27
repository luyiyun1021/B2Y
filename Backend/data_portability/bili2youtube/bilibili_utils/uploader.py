
import requests
import math
import subprocess

SESSION_ID = ''
VIDEO_DOWNLOAD_PATH = "/Users/ziranmin/Downloads/"
VIDEO_DOWNLOAD_QUALITY_ID = 32

def get_user_info(session_id=SESSION_ID):
    url = 'https://api.bilibili.com/x/web-interface/nav'
    cookies = {'SESSDATA': session_id}
    response = requests.get(url, cookies=cookies)
    user = {}

    if response.status_code == 200:
        json_response = response.json()
        user['uname'] = json_response['data']['uname']
        user['mid'] = json_response['data']['mid']
        return user

    else:
        print(f"Request failed with status code: {response.status_code}")

def get_series_lists(mid):
    '''

    :param mid: user id
    :return:
    '''
    base_url = f'https://api.bilibili.com/x/polymer/web-space/seasons_series_list?mid={mid}&page_num=1&page_size=20'
    response = requests.get(base_url)

    if response.status_code != 200:
        print(f"Request failed with status code: {response.status_code}")
        return []

    json_response = response.json()

    # Calculate total pages
    total_videos = json_response['data']['items_lists']['page']['total']
    page_size = json_response['data']['items_lists']['page']['page_size']
    total_pages = math.ceil(total_videos / page_size)

    # print("total_pages", total_pages)
    res = []

    for page in range(1, total_pages + 1):
        url = f'https://api.bilibili.com/x/polymer/web-space/seasons_series_list?mid={mid}&page_num={page}&page_size={page_size}'
        response = requests.get(url)
        if response.status_code == 200:
            json_response = response.json()
            series_list = json_response['data']['items_lists']['series_list']
            for item in series_list:
                res.append({'series_id': item['meta']['series_id'], 'name': item['meta']['name']})
        else:
            print(f"Request for page {page} failed with status code: {response.status_code}")

    return res

def get_series_list_videos(mid, series_id):
    base_url = f'https://api.bilibili.com/x/series/archives?mid={mid}&series_id={series_id}&only_normal=true&sort=desc&pn=1&ps=30'
    response = requests.get(base_url)

    if response.status_code != 200:
        print(f"Request failed with status code: {response.status_code}")
        return []

    json_response = response.json()

    # Calculate total pages
    total_videos = json_response['data']['page']['total']
    page_size = json_response['data']['page']['size']
    total_pages = math.ceil(total_videos / page_size)

    # print("total_pages", total_pages)
    res = []

    for page in range(1, total_pages + 1):
        url = f'https://api.bilibili.com/x/series/archives?mid={mid}&series_id={series_id}&only_normal=true&sort=desc&pn={page}&ps={page_size}'
        response = requests.get(url)
        if response.status_code == 200:
            json_response = response.json()
            for item in json_response['data']['archives']:
                # each video has two types of id, aid and bvid, we store both of them, but we primarily use bvid
                res.append({'aid': item['aid'],
                            'bvid': item['bvid'],
                            'title': item['title'],
                            })
        else:
            print(f"Request for page {page} failed with status code: {response.status_code}")

    return res

def get_video_info(bvid):
    '''

    :param bvid: video id
    :return:
    '''
    url = 'https://api.bilibili.com/x/web-interface/view'
    params = {'bvid': bvid}
    response = requests.get(url, params=params)
    video = {'bvid': bvid}

    if response.status_code == 200:
        json_response = response.json()
        data = json_response['data']
        video["title"] = data["title"]
        video["desc"] = data["desc"]
        video["cid"] = data["cid"]
        return video

    else:
        print(f"Request failed with status code: {response.status_code}")

def get_video_tags(bvid, session_id=SESSION_ID):
    url = 'https://api.bilibili.com/x/tag/archive/tags'
    params = {'bvid': bvid}
    cookies = {'SESSDATA': session_id}
    response = requests.get(url, params=params, cookies=cookies)
    tags = []

    if response.status_code == 200:
        json_response = response.json()
        data = json_response['data']
        for item in data:
            tags.append(item['tag_name'])
        return tags

    else:
        print(f"Request failed with status code: {response.status_code}")

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
    response = requests.get(url, params=params, cookies=cookies)
    tags = []

    if response.status_code == 200:
        json_response = response.json()
        data = json_response['data']
        return data['durl'][0]['url']

    else:
        print(f"Request failed with status code: {response.status_code}")

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
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    print("hello world")
    # print out own account info by using the session id got from QR code login
    print("print out own account info by using the session id got from QR code login")
    user = get_user_info(SESSION_ID)
    print(user)

    # use 盗月社 for later example
    mid = '99157282'  # 盗月社 user id

    # get 盗月社's all series list
    print("get 盗月社's all series list")
    series_lists = get_series_lists(mid)
    for ser_list in series_lists:
        print(ser_list)

    # get one of the series_ids from 盗月社's series_list, get all the videos from that list
    print("get one of the series_ids from 盗月社's series_list, get all the videos from that list")
    series_id = 299848
    videos = get_series_list_videos(mid, series_id)
    for video in videos:
        print(video)

    # get the detailed info of a video
    print("get the detailed info of a video")
    bvid = "BV1b94y187VN"
    video = get_video_info(bvid)
    print(video)
    # get the tags of a video
    tags = get_video_tags(bvid)
    print(tags)

    # get the source link of a video
    # print("get the source link of a video")
    vurl = get_video_source_link(bvid, video['cid'])
    print(vurl)

    # download the video
    # print("download the video")
    # download_video(bvid, vurl)









