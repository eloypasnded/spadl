import os
import shutil
import zipfile
import telebot as telebot
from bs4 import BeautifulSoup
import requests

TOKEN = '6743528124:AAF5BtyqNTQbffrXtFdrJdW_pLL8RFGQnSk'
bot = telebot.TeleBot(TOKEN)

def download_images(chat_id, url, page_title):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    img_tags = soup.find_all('img', {'src': lambda x: x and 't.jpg' in x})

    # Create a directory with the page title as the name
    directory = "".join(c for c in page_title if c.isalnum() or c in (' ',)).rstrip()
    os.makedirs(directory, exist_ok=True)

    for i, img_tag in enumerate(img_tags):
        img_url = img_tag['src'].replace('t.jpg', '.jpg')
        response = requests.get(img_url, stream=True)
        with open(os.path.join(directory, f'image{i}.jpg'), 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response

    # Create a CBZ file
    with zipfile.ZipFile(f'{directory}.cbz', 'w') as zipf:
        for file in os.listdir(directory):
            zipf.write(os.path.join(directory, file), arcname=file)

    # Send the CBZ file
    with open(f'{directory}.cbz', 'rb') as cbz_file:
        bot.send_document(chat_id=chat_id, data=cbz_file)

    # Delete the directory
    shutil.rmtree(directory)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.from_user.username == 'Zoe_Ebe':
        bot.reply_to(message, 'Hola, estoy listo para recibir mensajes.')

@bot.message_handler(commands=['code'])
def echo_all(message):
    if message.from_user.username == 'Zoe_Ebe':
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
                bot.send_photo(chat_id=message.chat.id, photo=img_url, caption=f'El nombre de la página es: {page_title}. La página contiene {len(img_tags)} imágenes. Si desea descargarlas, use el comando {download_command} {text} para obtener un archivo CBZ.')
                break
            else:
                bot.reply_to(message, 'Ha introducido un código incorrecto')

@bot.message_handler(commands=['d', 'g'])
def download_images_command(message):
    if message.from_user.username == 'Zoe_Ebe':
        command, *args = message.text.split()
        if not args:
            bot.reply_to(message, 'Introduzca un código')
            return
        text = args[0]
        url = f'https://es.3hentai.net/{command[1:]}/{text}'
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            page_title = soup.title.string
            download_images(message.chat.id, url, page_title)

bot.polling()
