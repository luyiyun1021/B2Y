from fake_useragent import UserAgent

COOKIE = (
    "buvid3=BD50D87E-E743-1743-C2A1-9A41DC86273F95198infoc; b_nut=1694354195; i-wanna-go-back=-1; b_ut=7; _uuid=23CA6788-D728-9B77-5E5F-F10D24638A18195282infoc;"
    "home_feed_column=4; buvid4=D17D272D-3947-6103-59E9-B477F4A6F10096454-023091021-ADgaJkpv35ag3jEPdUjt5A%3D%3D; header_theme_version=CLOSE;"
    "SESSDATA=87481b1e%2C1709943379%2C0441c%2A92CjAHfmGBZolEBjVXoxNTSolsIZoib7Jtc9i-EMWOeEhrBNhv2FlQbDNa0gn_sGGIhpoSVlNMSDBubVZKd1E4VU84Uk5WZlBETHpBRzFOekwxNG1NY3MtNkN0ZHNnVDFrUzFpWnZDNi1La2FyRFlxTktyZEVkdEJsc1ZjM1VuQ1duTzFkb1llUmtBIIEC;"
    "bili_jct=b7a72f2b5318bc9825f355e72b7d043c; DedeUserID=210437382; DedeUserID__ckMd5=f39352f467bcdc4c; sid=5kfzrj3i; rpdid=|(J|)RYllukR0J'uYmRJmuJmu;"
    "CURRENT_QUALITY=80; is-2022-channel=1; fingerprint=c92d21e3c77cb459556d4c284764ee0e; buvid_fp_plain=undefined; hit-new-style-dyn=1;"
    "hit-dyn-v2=1; LIVE_BUVID=AUTO8316944407472560; bsource=search_baidu; browser_resolution=1373-670; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9."
    "eyJleHAiOjE2OTU0NDkwOTYsImlhdCI6MTY5NTE4OTg5NiwicGx0IjotMX0.kezcVsJdP_jTH8IHoi3Cz_r9suiWvZfj3SpA1L2zv70; bili_ticket_expires=1695449096; PVID=1;"
    "CURRENT_BLACKGAP=0; CURRENT_FNVAL=4048; bp_video_offset_210437382=844202489484935223; buvid_fp=c92d21e3c77cb459556d4c284764ee0e; b_lsid=9F13B10610_18ABF3F3F36"
)


def generate_headers(cookie=COOKIE):
    ua = UserAgent()
    headers = {
        "User-Agent": ua.random,
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.bilibili.com/",
        "Cookie": cookie,  # 添加 Cookie
    }
    return headers
