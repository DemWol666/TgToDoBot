import telebot
from heandlers import initialization

bot = telebot.TeleBot('8172761160:AAF6TGFZa2AeCxFoxuR2k0SIxE44pKy3w3k')

initialization(bot)

bot.polling(none_stop=True)