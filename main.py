import requests
import os

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

API_URL = "https://api.p2pquake.net/v2/history?codes=551&limit=1"

STATE_FILE = "last_id.txt"

def get_scale_string(scale):
    """APIの震度数値をわかりやすい文字列に変換"""
    scale_map = {
        10: "1", 20: "2", 30: "3", 40: "4",
        45: "5弱", 50: "5強", 55: "6弱", 60: "6強", 70: "7"
    }
    return scale_map.get(scale, "不明")

def main():
  
    last_id = ""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            last_id = f.read().strip()


    res = requests.get(API_URL)
    if res.status_code != 200:
        return
    data = res.json()
    if not data:
        return

    latest_quake = data[0]
    current_id = latest_quake["id"]

  
    if current_id == last_id:
        print("新しい地震情報はありません。")
        return

    
    eq = latest_quake.get("earthquake", {})
    hypocenter = eq.get("hypocenter", {}).get("name", "不明")
    magnitude = eq.get("hypocenter", {}).get("magnitude", "不明")
    depth = eq.get("hypocenter", {}).get("depth", "不明")
    max_scale = get_scale_string(eq.get("maxScale", 0))
    time_str = eq.get("time", "不明")

  
    embed = {
        "title": " ⚠️ 地震情報",
        "color": 16711680, # 赤色 (震度によって変えることも可能)
        "fields": [
            {"name": "発生時刻", "value": time_str, "inline": True},
            {"name": "震源地", "value": hypocenter, "inline": True},
            {"name": "最大震度", "value": max_scale, "inline": True},
            {"name": "マグニチュード", "value": f"M{magnitude}", "inline": True},
            {"name": "深さ", "value": f"{depth}km", "inline": True}
        ],
        "footer": {"text": "情報元: 気象庁 / P2P地震情報API"}
    }

    lat = eq.get("hypocenter", {}).get("latitude")
    lon = eq.get("hypocenter", {}).get("longitude")
    if lat != -200 and lon != -200: # -200はAPIにおける「不明」の値
        map_url = f"https://www.google.com/maps?q={lat},{lon}"
        embed["description"] = f"[📍 震源地を地図で確認する]({map_url})"

    
    payload = {"embeds": [embed]}
    requests.post(WEBHOOK_URL, json=payload)


    with open(STATE_FILE, "w") as f:
        f.write(current_id)
    print("Discordに通知を送信しました。")

if __name__ == "__main__":
    main()
