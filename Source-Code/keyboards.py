from telebot import types

def home_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('🆕 Добавить задачу')
    btn2 = types.KeyboardButton('📋 Мои задачи')
    btn3 = types.KeyboardButton('⚙️ Настройки')
    btn4 = types.KeyboardButton('🔞 Секретная функция е621')
    markup.add(btn1, btn2, btn3, btn4)
    return markup

def settings_Keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn1 = types.KeyboardButton('1 час до дедлайна')
    btn2 = types.KeyboardButton('2 часа до дедлайна')
    btn3 = types.KeyboardButton('3 часа до дедлайна')
    btn4 = types.KeyboardButton('6 часов до дедлайна')
    btn_back = types.KeyboardButton('⬅️ Назад')
    markup.add(btn1, btn2, btn3, btn4, btn_back)
    return markup

def tasks_Keyboard(number_of_task):
    markup = types.InlineKeyboardMarkup()
    complete_button = types.InlineKeyboardButton('✅ Выполнено', callback_data=f'complete_{number_of_task-1}')
    edit_button = types.InlineKeyboardButton('✏️ Редактировать', callback_data=f'editRem_{number_of_task-1}')
    markup.add(complete_button, edit_button)
    return markup

def back_button():
    markup_back = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn_back = types.KeyboardButton('⬅️ Назад')
    markup_back.add(btn_back)
    return markup_back