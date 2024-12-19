from telebot import types
from keyboards import *
from keyboards import tasks_Keyboard
from Utils import *


def initialization(bot):
    @bot.message_handler(commands=['start'])
    def start_message(message):
        bot.send_message(message.chat.id, 'Это Avaka бот', reply_markup=home_keyboard())
    
    @bot.message_handler(func=lambda message: message.text == '⚙️ Настройки')
    def settings_message(message):
        bot.send_message(message.chat.id, 'Выбери за сколько часов до дедлайна ты хочешь получать уведомления.', reply_markup=settings_Keyboard())

    @bot.message_handler(func=lambda message: message.text in ['1 час до дедлайна', '2 часа до дедлайна', '3 часа до дедлайна', '6 часов до дедлайна'])
    def message_reminding_time(message):
        if set_reminding_time(message) != -1:
            bot.send_message(message.chat.id, '✅ Установлено')
            start_message(message)

    @bot.message_handler(func=lambda message: message.text == '⬅️ Назад')
    def go_home_page(message):
        start_message(message)
    
    @bot.message_handler(func=lambda message: message.text == '🆕 Добавить задачу')
    def message_add_task(message):
        bot.send_message(message.chat.id, 'Отправь текст задачи.')
        bot.register_next_step_handler(message, get_deadline)
    
    def get_deadline(message):
        task_text = message.text.strip()
        bot.send_message(message.chat.id, 'Теперь отправь дату дедлайна в формате ДД.ММ.ГГГГ ЧЧ:ММ')
        bot.register_next_step_handler(message, send_deadline, task_text)

    def send_deadline(message, task_text):
        result = save_task(message, task_text)
        bot.send_message(message.chat.id, result)
    
    @bot.message_handler(func=lambda message: message.text == '📋 Мои задачи')
    def message_show_tasks(message):
        response, num = show_tasks(message)
        bot.send_message(message.chat.id, response, parse_mode='Markdown', reply_markup=tasks_Keyboard(num))
        bot.send_message(message.chat.id, '⬅️ Нажмите "Назад", чтобы вернуться в главное меню.', reply_markup=back_button())

    @bot.callback_query_handler(func=lambda call: call.data.startswith('editRem_'))
    def callback_edit_message(call):
        error_code, user_id, task_index, task_to_edit, response = edit_task(call)
        if error_code == 0:
            bot.answer_callback_query(call.id, response)
            bot.register_next_step_handler(call.message, message_edit_task, user_id, task_index, task_to_edit)
        else:
            bot.answer_callback_query(call.id, response)
    
    def message_edit_task(message, user_id, task_index, task_to_edit):
        new_text = message.text.strip()
        if not new_text:
            bot.send_message(message.chat.id, '❌ Новый текст задачи не может быть пустым.')
            return
        response = process_edit_task(new_text, user_id, task_index, task_to_edit)
        bot.send_message(message.chat.id, response)
        show_tasks(message)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('complete_'))
    def message_complete_task(call):
        response, isError = complete_task(call)
        if isError == 0:
            bot.answer_callback_query(call.id, response)
            bot.delete_message(call.message.chat.id, call.message.message_id)
        else:
            bot.answer_callback_query(call.id, response)

    @bot.message_handler(func=lambda message: message.text == '🔞 Секретная функция е621')
    def messege_ask_tags(message):
        bot.send_message(message.chat.id, '🔎 Отправь желаемые теги через пробел', reply_markup=back_button())
        bot.register_next_step_handler(message, check_home)

    def check_home(message):
        if message.text.strip() == '⬅️ Назад':
            start_message(message)
        else:
            message_ask_summ(message)
    
    def message_ask_summ(message):
        tags = message.text.strip()
        bot.send_message(message.chat.id, '🔢 Введи необходимое кол-во изображений (не более 10)')
        bot.register_next_step_handler(message, message_check_valid_summ, tags)

    def message_check_valid_summ(message, tags):
        response, Error_code, limit = check_valid_summ(message)
        if Error_code == -1:
            bot.send_message(message.chat.id, response)
            bot.register_next_step_handler(message, message_check_valid_summ, tags)
        else:
            print(f'message_check_valid_summ {limit}')
            send_media(message, tags, limit)

    def send_media(message, tags, limit):
        media, code_number = handle_response(message, tags, limit)
        number = 0
        print(f'media content {media}')
        for content in media:
            if code_number[number] == 1:
                bot.send_video(message.chat.id, content, supports_streaming=True)
                number += 1
            elif code_number[number] == 2:
                bot.send_photo(message.chat.id, content)
                number += 1
            else:
                bot.send_message(message.chat.id, "❌ Таких тегов нет/Ответ пуст. Повторите попытку /wolf")
        messege_ask_tags(message)


        





            


    

