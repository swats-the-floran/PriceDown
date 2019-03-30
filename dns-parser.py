import requests   # библиотека для запросов к веб-страницам, она же используется для API Telegram
import urllib.request
from bs4 import BeautifulSoup # html-парсер
import pickle   # упаковка любой переменной для записи в файл и восстановления при повторном запуске
import re       # регулярные выражения
import datetime            # дата и время
import misc                # в файле misc.py хранятся переменные token и chat_id - секретные данные для авторизации
                           #  telegram-бота, которые не будут опубликованы в тексте работы
import input               # входные данные - переменные BASE_DNS_URL, MIN_PRICE, MAX_PRICE в отдельном файле

token = misc.token
chat_id = misc.my_chat_id
misha_chat_id = misc.misha_chat_id
BASE_DNS_URL = input.BASE_DNS_URL
MIN_PRICE = input.MIN_PRICE
MAX_PRICE = input.MAX_PRICE
TELEGRAM_URL = 'https://api.telegram.org/bot' + token + '/'

ads_dict = {} # переменная типа словарь, в которой мы храним базу объявлений
message = ''  # сообщение которое мы отправим пользоавтелю

def get_html(url):
    response = urllib.request.urlopen(url)
    return response.read()

def get_page_data(html):
    global ads_dict
    global message
    soup = BeautifulSoup(html, "html.parser")
    ads = soup.find_all('div', class_="product")
    for ad in ads:
        try:
            tittle = ad.find("div", class_="item-name").find('a').text
            desc = re.sub('\s+', ' ', ad.find("div", class_="item-desc").find('a').text)
            desc1 = re.sub('\s+', ' ', ad.find("div", class_="characteristic-description").text)
            price = int(re.sub(' ','',(ad.find("div", class_="price_g").find('span').text)))
            ad_url = ad.find("div", class_="item-desc").find('a').get('href')
#            print(price, tittle, desc1, desc, ad_url, sep=' : ')
            if ads_dict.get(ad_url) is None:  #если объявление новое ....
                if MIN_PRICE <= price <= MAX_PRICE or price < 0:
#                   print('Новое объявление: ', price, 'руб', tittle, desc, desc1, ad_url)
                    message+=('Новое объявление: Цена '+str(price)+' руб \n'+tittle+'\n'+desc+'\n'+desc1+'\n'+ad_url+'\n')
            elif price != ads_dict[ad_url][1]: # если изменилась цена
                if MIN_PRICE <= price <= MAX_PRICE or price < 0:
#                    print('Изменилась цена: ', ads_dict[ad_url][1], '-->', tittle, desc, desc1, ad_url)
                    message+=('Изменилась цена: '+str(ads_dict[ad_url][1])+' -> '+str(price)+'\n'+tittle+'\n'+desc+'\n'+ desc1+'\n'+ad_url+'\n')
            ads_dict[ad_url] = [tittle, price, desc, desc1]
        except:
            f1 = open('logs/error.log', 'a', encoding='utf-8')
            f1.write(str(datetime.datetime.now()))
            f1.write('Цена или описание не найдено:')
            f1.write(ad.prettify())
            f1.close()

def telegram_send_me(message): # функция отправляет сообщение мне в telegram
    url = TELEGRAM_URL + 'sendmessage?chat_id={}&text={}&disable_web_page_preview=true'.format(chat_id, message)
    requests.get(url)

def telegram_send_misha(message): # функция отправляет сообщение мне в telegram
    url = TELEGRAM_URL + 'sendmessage?chat_id={}&text={}&disable_web_page_preview=true'.format(misha_chat_id, message)
    requests.get(url)

def main():
    global ads_dict
    global message
    message = ''
    try: # считываем базу объявлений из файла в переменную типа словарь ads_dict
        f = open('data-dns-shop.bin', 'rb')
        ads_dict = pickle.load(f)
        f.close()
        print('База успешно считана')
        first_run = False
    except: # если файла data-dns-shop.bin нет, то программа запускается первый раз
        print('База не найдена - Первый запуск')
        first_run = True
    print('Программа считывает страницу ', BASE_DNS_URL)
    print('Не закрывай меня')
    html = get_html(BASE_DNS_URL) # считываем содержание веб-страницы в переменную типа текст

    get_page_data(html) # выполняем поиск и анализстраницы с объявлениями

    # Упаковка в файл базы объявлений ads_dict для следующего запуска
    f = open('data-dns-shop.bin', 'wb')
    pickle.dump(ads_dict, f)
    f.close()
    # Запись сообщения в файл для контроля сообщений, которые были отправлены пользователю
    now = re.sub(':| |\.', '-', str(datetime.datetime.now())) # дата и время, заменяем двоеточие точку и пробел на -
    f = open('messages/message-' + now + '.txt', 'w', encoding='utf-8')
    f.write(message)
    f.close()
    if message != '': # and not first_run:  #если message не пусто, и не первый запуск, то отправляем сообщение через Telegram
        telegram_send_me(message)
        #telegram_send_misha(message)
if __name__ == '__main__':
    main()     # запуск программы
