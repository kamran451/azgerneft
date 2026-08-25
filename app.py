import os
import asyncio
import threading
from flask import Flask, render_template
from flask_socketio import SocketIO
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import GiftEvent, ConnectEvent

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Komandaların xalları
game_data = {
    "left_score": 0,
    "right_score": 0
}

# Öz TikTok istifadəçi adını bura yaz (məsələn: "@kamran_live")
TIKTOK_USERNAME = "@senin_tiktok_adın"
client: TikTokLiveClient = TikTokLiveClient(unique_id=TIKTOK_USERNAME)

@client.on("connect")
async def on_connect(event: ConnectEvent):
    print(f"TikTok Live-a ugurla qosuldu: {client.unique_id}")

@client.on("gift")
async def on_gift(event: GiftEvent):
    if event.gift.streakable and event.gift.repeat_end:
        count = event.gift.repeat_count
    elif not event.gift.streakable:
        count = 1
    else:
        return

    gift_name = event.gift.name.lower()
    user_name = event.user.unique_id
    points = event.gift.diamond_count * count
    
    # Hədiyyə adında "rose" (və ya gül) varsa sola, qalanlar sağ tərəfə xal yazır
    if "rose" in gift_name or "gül" in gift_name:
        game_data["left_score"] += points
        side = "left"
    else:
        game_data["right_score"] += points
        side = "right"

    # Veb səhifəyə (ekrana) məlumat ötürürük
    socketio.emit('update_game', {
        "left_score": game_data["left_score"],
        "right_score": game_data["right_score"],
        "user": user_name,
        "gift": event.gift.name,
        "count": count,
        "side": side
    })

@app.route('/')
def index():
    return render_template('index.html')

def run_tiktok():
    try:
        asyncio.run(client.start())
    except Exception as e:
        print(f"TikTok qosulma xətası: {e}")

if __name__ == '__main__':
    # TikTok dinləyicisini arxa fonda işə salırıq
    t = threading.Thread(target=run_tiktok, daemon=True)
    t.start()
    
    # Render-in təyin etdiyi portu götürürük
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
