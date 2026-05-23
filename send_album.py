import os
import requests
import json
from requests_toolbelt.multipart.encoder import MultipartEncoder

BOT_TOKEN = "8295960895:AAESOpD4WuonWs5ghOU9I7SAyZutN2RDiAw"
CHANNEL_ID = -1003917503298  # Твой точный ID канала

def send_perfect_audio_post():
    print("[Telegram] Сборка идеального аудио-поста...")
    
    audio_folder = "album_data/tracks"
    
    # Мощный, визуально красивый текст, который привяжется к альбому
    caption_text = (
        "✨ *NEW ALBUM OUT NOW* ✨\n"
        "🎬 *Lofi Night Moods* — *Volume 1*\n"
        "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n\n"
        "🌌 *Immerse yourself in the ultimate night chill.* "
        "The perfect soundtrack for late-night coding, studying, reading, or deep relaxation. "
        "Each beat is crafted to boost your focus and bring peace of mind.\n\n"
        "📜 *Tracklist:*\n"
        "🔹 01. Midnight Pocket Tape 2\n"
        "🔹 02. Midnight Pocket Tape\n"
        "🔹 03. Paper Lantern Replay 2\n"
        "🔹 04. Paper Lantern Replay\n"
        "🔹 05. Rain on Wool\n\n"
        "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        "#lofi #lofialbum #chillbeats #musicforstudy #lofifactory"
    )

    if not os.path.exists(audio_folder):
        print(f"[Ошибка] Папка с треками не найдена: {audio_folder}")
        return

    # Берем строго 5 MP3 файлов, сортируем по имени
    tracks = [f for f in os.listdir(audio_folder) if f.endswith('.mp3')]
    tracks = sorted(tracks)[:5]

    if not tracks:
        print("[Ошибка] В папке нет MP3 файлов!")
        return

    fields = {
        "chat_id": str(CHANNEL_ID),
        "media": ""
    }

    media_payload = []

    # Упаковываем треки в поток
    for index, track_name in enumerate(tracks):
        clean_title = os.path.splitext(track_name)[0]
        track_path = os.path.join(audio_folder, track_name)
        
        file_key = f"audio_{index}"
        # Открываем файл в бинарном режиме
        fields[file_key] = (track_name, open(track_path, "rb"), "audio/mpeg")
        
        audio_item = {
            "type": "audio",
            "media": f"attach://{file_key}",
            "title": clean_title,
            "performer": "Lofi Factory"  # Имя автора для всех треков
        }
        
        # Привязываем наш сочный текст ТОЛЬКО к первому треку пачки
        if index == 0:
            audio_item["caption"] = caption_text
            audio_item["parse_mode"] = "Markdown"
            
        media_payload.append(audio_item)

    fields["media"] = json.dumps(media_payload)

    print("[Telegram] Стабилизация потока данных...")
    m = MultipartEncoder(fields=fields)
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMediaGroup"
    
    print("[Telegram] Отправка альбома в ленту...")
    try:
        response = requests.post(
            url, 
            data=m, 
            headers={"Content-Type": m.content_type}, 
            timeout=(30, 600)  # Даем 10 минут, если сеть тупит из-за рендера
        )
        
        result = response.json()
        if result.get("ok"):
            print("\n[Успех] Пост-альбом успешно опубликован! Глазки радуются!")
        else:
            print(f"[Ошибка Телеграма]: {result.get('description')}")
            
    except Exception as e:
        print(f"[Сетевая ошибка]: {e}")
    finally:
        # Чистим за собой память и закрываем дескрипторы файлов
        for key, value in fields.items():
            if isinstance(value, tuple):
                value[1].close()

if __name__ == "__main__":
    send_perfect_audio_post()