import os
import json
import datetime
from e621 import E621
import requests
from PIL import Image
from io import BytesIO
from moviepy import *
import tempfile
import shutil

e621 = E621()
current_dir = os.path.dirname(os.path.abspath(__file__))
TASKS_FILE = os.path.join(current_dir, '..', 'Json-files', 'tasks.json')
SETTINGS_FILE = os.path.join(current_dir, '..', 'Json-files', 'settings.json')
VIDEOOUTPUT_FILE = os.path.join(current_dir, '..', 'Temporary-files', 'output.mp4')
COMPRESSED_IMAGE_FILE = os.path.join(current_dir, '..', 'Temporary-files', 'compressed_image.jpg')
TEMPORALE_FILES = os.path.join(current_dir, '..', 'Temporary-files')

def load_file(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}

def save_file(data, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

tasks = load_file(TASKS_FILE)
settings = load_file(SETTINGS_FILE)

def set_reminding_time(message):
    try:
        user_id = str(message.chat.id)
        time_map = {
            '1 час до дедлайна': 1,
            '2 часа до дедлайна': 2,
            '3 часа до дедлайна': 3,
            '6 часов до дедлайна': 6
        }
        reminder_time = time_map[message.text]
        settings[user_id] = {'reminder_time': reminder_time}
        save_file(settings, SETTINGS_FILE)
    except:
        print(f'set_reminding_time ERROR {reminder_time}')
        return -1

def save_task(message, task_text):
    try:
        deadline = datetime.datetime.strptime(message.text, '%d.%m.%Y %H:%M')
    except ValueError:
        return '❌ Неверный формат даты. Попробуй снова (ДД.ММ.ГГГГ ЧЧ:ММ).'
    user_id = str(message.chat.id)
    if user_id not in tasks:
        tasks[user_id] = []
    tasks[user_id].append({'task': task_text, 'deadline': message.text})
    save_file(tasks, TASKS_FILE)
    return  f'✅ Задача "{task_text}" добавлена с дедлайном {message.text}.'

def show_tasks(message):
    user_id = str(message.chat.id)
    user_tasks = tasks.get(user_id, [])

    if not user_tasks:
        return 'У вас нет задач'
    
    for i, task in enumerate(user_tasks, start=1):
        response = f'📋 Задача {i}:\n*{task["task"]}*\n🕒 Дедлайн: {task["deadline"]}'
        return response, i

def edit_task(call):
    user_id = str(call.message.chat.id)
    task_index = int(call.data.split('_')[1])  # Получаем индекс задачи
    user_tasks = tasks.get(user_id, [])

    if 0 <= task_index < len(user_tasks):
        task_to_edit = user_tasks[task_index]
        error_code = 0
        return error_code, user_id, task_index, task_to_edit, 'Теперь отправь новый текст для задачи.'
    else:
        error_code = 1
        return error_code, user_id, task_index, task_to_edit, '❌ Задача не найдена.'
    
def process_edit_task(new_text, user_id, task_index, task_to_edit):
    tasks[user_id][task_index]['task'] = new_text
    save_file(tasks, TASKS_FILE)
    return f'✅ Задача обновлена: {new_text}'

def complete_task(call):
    user_id = str(call.message.chat.id)
    task_index = int(call.data.split('_')[1])
    user_tasks = tasks.get(user_id, [])

    if 0 <= task_index < len(user_tasks):
        completed_task = user_tasks.pop(task_index)
        save_file(tasks, TASKS_FILE)
        return f'✅ Задача "{completed_task["task"]}" выполнена!', 0
    else:
        return '❌ Задача уже удалена.', -1

def check_valid_summ(message):
    try:
        limit = int(message.text.strip())
        if limit > 10:
            return '❌ Не более 10 изображений! Введи корректное число ❌', -1, -1
        else:
            print(f'Limit check_valid_summ {limit}')
            return 'All good', 0, limit
    except ValueError:
        return '❌ Введи ЧИСЛО ❌', -1, -1
    
def compress_image(image_url):
    response = requests.get(image_url)
    
    # Проверяем успешность запроса и тип содержимого
    if response.status_code != 200:
        print(f"Failed to retrieve image from {image_url}. Status code: {response.status_code}")
        return None
    
    # Проверяем тип содержимого
    if 'image' not in response.headers.get('Content-Type', ''):
        print(f"The URL {image_url} does not point to an image.")
        return None
    
    try:
        img = Image.open(BytesIO(response.content))
    except Exception as e:
        print(f"Error opening image from {image_url}: {e}")
        return None
    
    img = img.convert("RGB")
        
    compressed_image_path = COMPRESSED_IMAGE_FILE
    img.save(compressed_image_path, quality=100)
    
    return compressed_image_path

def convert_webp_to_mp4(webp_url, output_file=VIDEOOUTPUT_FILE):
    #Скачиваем файл .webp по URL
    response = requests.get(webp_url)
    if response.status_code != 200:
        print(f"Не удалось скачать .webp: {webp_url}")
        return None
    
    webp_path = 'input.webp'
    with open(webp_path, 'wb') as f:
        f.write(response.content)

    #Конвертируем .webp в .mp4
    try:
        clip = VideoFileClip(webp_path)
        clip.write_videofile(output_file, codec='libx264', audio=True)
    except Exception as e:
        print(f"Ошибка при конвертации .webp в .mp4: {e}")
        return None
    #Удаляем временный файл webp_path
    if os.path.exists(webp_path):
        try:
            os.remove(webp_path)
        except Exception as e:
            print(f"❌ Ошибка при удалении .webp файла: {e}")
    else:
        print(f"⚠️ Файл {webp_path} не найден, возможно он уже удалён.")
    return output_file

def handle_response(message, tags, limit):
    print(f'Limit handle_response {limit}')
    posts = e621.posts.search(tags=tags, limit=limit)
    image_url = [post.file.url for post in posts]
    print(f'Image url {image_url}')
    all_media = []
    return_number = []

    if image_url != []:
        for url in image_url:
            if url is None:
                print("Skipping invalid URL")
                continue
            if url.endswith('.webm'):
                mp4_video = convert_webp_to_mp4(url)
                temp_video = tempfile.NamedTemporaryFile(dir=TEMPORALE_FILES, delete=False)
                with open(mp4_video, 'rb') as video_file:
                    shutil.copyfileobj(video_file, temp_video)
                temp_video.close()
                all_media.append(open(temp_video.name, 'rb'))
                return_number.append(1)
                print(all_media)
            else:
                compressed_image_path = compress_image(url)
                temp_image = tempfile.NamedTemporaryFile(dir=TEMPORALE_FILES, delete=False)
                with open(compressed_image_path, 'rb') as image_file:
                    shutil.copyfileobj(image_file, temp_image)
                temp_image.close()
                all_media.append(open(temp_image.name, 'rb'))
                return_number.append(2)
        return all_media, return_number
    else:
        return None, None 
