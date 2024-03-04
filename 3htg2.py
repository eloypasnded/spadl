import os
import telebot
from bs4 import BeautifulSoup
import requests
import psutil

TOKEN = '6743528124:AAF5BtyqNTQbffrXtFdrJdW_pLL8RFGQnSk'
bot = telebot.TeleBot(TOKEN)
CHANNEL_NAME = '@animexnube'

def check_memory():
    # Get the memory usage in bytes
    memory_usage = psutil.Process(os.getpid()).memory_info().rss
    # Convert to MB
    memory_usage_mb = memory_usage / (1024 * 1024)
    return memory_usage_mb < 500

def send_images(chat_id, url):
    if not check_memory():
        bot.send_message(chat_id=chat_id, text='Espere un momento a que se libere RAM')
        return

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    img_tags = soup.find_all('img', {'src': lambda x: x and 't.jpg' in x})

    images = []
    for i, img_tag in enumerate(img_tags):
        if not check_memory():
            bot.send_message(chat_id=chat_id, text='Espere un momento a que se libere RAM')
            break

        img_url = img_tag['src'].replace('t.jpg', '.jpg')
        images.append(telebot.types.InputMediaPhoto(img_url))

        # Send images in groups of 10
        if len(images) == 10:
            bot.send_media_group(chat_id=chat_id, media=images)
            images = []

    # Send any remaining images
    if images:
        bot.send_media_group(chat_id=chat_id, media=images)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 'Hola, estoy listo para recibir mensajes.')

@bot.message_handler(commands=['code'])
def echo_all(message):
    command, *args = message.text.split()
    if not args:
        bot.reply_to(message, 'Introduzca un código')
        return
    text = args[0]
    urls = [f'https://es.3hentai.net/d/{text}', f'https://es.3hentai.net/g/{text}']
    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            page_title = soup.title.string
            img_url = soup.find('img', {'src': lambda x: x and 'cover.jpg' in x})['src']
            img_tags = soup.find_all('img', {'src': lambda x: x and 't.jpg' in x})
            download_command = '/d' if 'd' in url else '/g'
            bot.send_photo(chat_id=message.chat.id, photo=img_url, caption=f'El nombre de la página es: {page_title}. La página contiene {len(img_tags)} imágenes. Si desea descargarlas, use el comando {download_command} {text}.')
            break
        else:
            bot.reply_to(message, 'Ha introducido un código incorrecto')

@bot.message_handler(commands=['d', 'g'])
def download_images_command(message):
    command, *args = message.text.split()
    if not args:
        bot.reply_to(message, 'Introduzca un código')
        return
    text = args[0]
    url = f'https://es.3hentai.net/{command[1:]}/{text}'
    send_images(message.chat.id, url)

bot.polling()
