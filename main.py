import requests
from bs4 import BeautifulSoup
import json

def fetch_data():
    session = requests.Session()
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
    }
    res = session.post("https://awb.cpbl.com.tw/home/getdetaillist", headers=headers)
    data = res.json()
    games = json.loads(data["GameDetailJson"])

    result  = []
    for g in games:
        start_time_full = g["GameDateTimeS"]       # 取得的資料：2025-11-18T12:05:00
        start_time_fmt = start_time_full.replace("T", " ")[:-3]  # 2025-11-18 12:05
        start_hhmm = start_time_fmt[-5:]           # 12:05

        result.append({
            "field": g["FieldAbbe"],
            "matchup": f"{g['VisitingTeamName']} vs {g['HomeTeamName']}",
            "start_time_full": start_time_fmt,
            "start_hhmm": start_hhmm
        })

    # print(result)
    return result

def get_today_msg(games):
    if(len(games) == 0):
        return "今天沒有比賽唷！"
    
    msg = f"今天有 {len(games)} 場比賽！\n" + f"{'-'*30}\n"
    for g in games:    
        msg += (
            f"📍 場地：{g['field']}\n"
            f"⚾ 對戰：{g['matchup']}\n"
            f"🕒 開賽時間：{g['start_hhmm']}\n"
            f"{'-'*30}\n"
        )
    # print(msg)
    return msg

def get_next_game_msg(games, now):
    now_hhmm = now.strftime("%H:%M")

    count = 0
    msg = ""

    for g in games:
        if(g["start_hhmm"] == now_hhmm):
            count+=1
            msg += (
                f"📍 場地：{g['field']}\n"
                f"⚾ 對戰：{g['matchup']}\n"
                f"🕒 開賽時間：{g['start_time']}\n"
                f"{'-'*30}\n"
            )

    if(count == 0):
        return 0
    
    final_msg = f"等等有 {count} 場比賽唷！\n" + "-"*30 + "\n" + msg
    return final_msg

def send_msg(messages_text):
    import os
    import requests
    import json
    from dotenv import load_dotenv

    load_dotenv()
    TOKEN = os.getenv('TOKEN')

    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}"
    }

    body = {
        "messages": [
            { "type": "text",
                "text": messages_text
            } ]
    }

    # print(messages_text)
    res = requests.post(url, headers=headers, data=json.dumps(body))
    print(res.status_code, res.text)

def check_time():
    import datetime
    now = datetime.now()
    hr, min = now.hour, now.minute

    if(hr == 0 and min == 0):
        games = fetch_data()
        msg = get_today_msg(games)
        send_msg(msg)
        return
    
    games = fetch_data()
    
    if(hr == 12 and min == 0):
        msg = get_next_game_msg(games, datetime.strptime("12:05", "%H:%M"))
        if(msg != 0):
            send_msg(msg)
    elif(hr == 18 and min == 0):
        msg = get_next_game_msg(games, datetime.strptime("18:05", "%H:%M"))
        if(msg  != 0):
            send_msg(msg)

check_time()