import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload

# Указываем, что нам нужны права на загрузку видео
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service():
    # Скрипт ищет твой скачанный ключ
    client_secrets_file = "client_secrets.json"
    
    # При первом запуске откроется браузер, где нужно будет нажать "Разрешить"
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, SCOPES
    )
    credentials = flow.run_local_server(port=0)
    
    # Возвращаем готовый канал связи с YouTube
    return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

def upload_video(youtube, video_file, title, description, tags):
    print(f"[YouTube] Отправка файла {video_file} на канал...")
    
    # Формируем посылку: название, описание, теги и настройки приватности
    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "10",  # 10 — это категория "Музыка" на YouTube
        },
        "status": {
            # Загружаем как "private" (Доступ по ссылке/Приватное), чтобы канал не забанили за спам.
            # Опубликуешь вручную по графику, когда проверишь, что всё красиво.
            "privacyStatus": "private",  
            "selfDeclaredMadeForKids": False,
        },
    }

    # Подгружаем сам медиафайл
    media_file = MediaFileUpload(video_file, chunksize=-1, resumable=True)

    # Создаем запрос на загрузку
    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media_file
    )

    # Процесс загрузки с отображением процентов
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Загружено: {int(status.progress() * 100)}%")

    print(f"[Успех] Видео загружено! Ссылка для проверки: https://youtu.be/{response['id']}")
    return response['id']