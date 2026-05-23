import os
import random
from pydub import AudioSegment

# --- НАША ЗАПЛАТКА СТАРТА ---
from PIL import Image
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS
# --- НАША ЗАПЛАТКА КОНЕЦ ---

from moviepy.editor import AudioFileClip, ImageClip, VideoFileClip, CompositeVideoClip, vfx

def process_audio(input_track_path, sfx_path, output_audio_path):
    print(f"[Звук] Обработка трека: {input_track_path}")
    
    # Загружаем оригинальную музыку и фоновый шум (например, дождь)
    track = AudioSegment.from_file(input_track_path)
    noise = AudioSegment.from_file(sfx_path) - 22  # Делаем шум тише на 22 децибела
    
    # Если шум короче песни, мы его дублируем (зацикливаем)
    if len(noise) < len(track):
        loops_needed = (len(track) // len(noise)) + 1
        noise = noise * loops_needed
    
    # Обрезаем шум ровно под длину трека
    noise = noise[:len(track)]
    
    # Накладываем шум поверх музыки
    combined = track.overlay(noise)
    
    # Случайно ускоряем трек от 1% до 2.5%, чтобы обмануть роботов YouTube (Content ID)
    speed_factor = random.uniform(1.01, 1.025)
    
    # Техническая магия Pydub для изменения скорости без сильного искажения голоса/звука
    sound_with_altered_frame_rate = combined._spawn(combined.raw_data, overrides={
        "frame_rate": int(combined.frame_rate * speed_factor)
    })
    final_audio = sound_with_altered_frame_rate.set_frame_rate(combined.frame_rate)
    
    # Сохраняем готовый уникальный MP3
    final_audio.export(output_audio_path, format="mp3", bitrate="320k")
    return output_audio_path

def build_video(audio_path, image_path, overlay_video_path, output_mp4_path):
    print(f"[Видео] Старт рендера: {output_mp4_path}")
    
    # Загружаем подготовленный аудиофайл
    audio = AudioFileClip(audio_path)
    duration = audio.duration
    
    # Создаем видеоряд из статичной картинки длиной с аудиофайл
    base_img = ImageClip(image_path).set_duration(duration).set_opacity(1).resize((1920, 1080))
    
    # 1. Слегка увеличиваем картинку на 10%, чтобы при покачивании не вылезали черные края
    zoomed_base = base_img.resize(1.1) 

    # 2. Создаем функцию плавного покачивания (движение по круговой траектории)
    import math
    def wiggle(t):
       # Картинка будет плавно смещаться на 10 пикселей туда-сюда
       x_offset = 10 * math.sin(t * 0.8)
       y_offset = 5 * math.cos(t * 0.5)
       
       # Считаем позицию от центра экрана (1920x1080)
       x_pos = int((1920 - zoomed_base.w) / 2 + x_offset)
       y_pos = int((1080 - zoomed_base.h) / 2 + y_offset)
       return (x_pos, y_pos)

    # 3. Применяем покачивание к нашей картинке
    zoom_clip = zoomed_base.set_position(wiggle)
    
    # Загружаем видео с помехами (пыль/старая пленка) и убираем из него звук
    overlay = VideoFileClip(overlay_video_path).without_audio().resize((1920, 1080))
    # Зацикливаем анимацию пыли на всю длину трека
    overlay = overlay.fx(vfx.loop, duration=duration)
    # Делаем анимацию полупрозрачной (30% видимости)
    overlay = overlay.set_opacity(0.3).set_position(('center', 'center'))
    
    # Накладываем прозрачную пыль поверх увеличивающейся картинки
    final_video = CompositeVideoClip([zoom_clip, overlay], size=base_img.size)
    final_video = final_video.set_audio(audio)
    
    # Запускаем сохранение готового MP4 файла
    # threads=4 указывает процессору работать в 4 потока для ускорения
    final_video.write_videofile(
        output_mp4_path, 
        fps=24, 
        codec="libx264", 
        audio_codec="aac",
        preset="medium", 
        threads=4
    )
    
    # Закрываем файлы, чтобы не забивать оперативную память
    audio.close()
    base_img.close()
    overlay.close()
    final_video.close()