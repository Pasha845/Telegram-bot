import telebot

Core_bot = telebot.TeleBot('1725950265:AAFYFq2JhJkjYNvPrbFjwnXo709RKstJJL4')


@Core_bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Привет":
        Core_bot.send_message(message.from_user.id, "Привет, чем я могу тебе помочь?")
    elif message.text == "/hello-world":
        Core_bot.send_message(message.from_user.id, "Напиши привет")
    else:
        Core_bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /hello-world.")


Core_bot.polling(none_stop=True, interval=0)
