import telebot
import sqlite3
import datetime
from datetime import timedelta

bot = telebot.TeleBot('6873895553:AAFuFtFXFDwcPmvJJ3grT8uidsFfuSSHeGo')
name = None
fdate = None


@bot.message_handler(commands=['start'])
def database_start(message):
    connect = sqlite3.connect('base.db')
    cursor = connect.cursor()
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, prodname TEXT, fdate TEXT, ldate TEXT)')
    connect.commit()
    cursor.close()
    connect.close()
    bot.send_message(message.chat.id, 'Бот запущен')


@bot.message_handler(commands=['addprod'])
def addproduct(message):
    bot.send_message(message.chat.id, 'Какой продукт вы хотите добавить?')
    bot.register_next_step_handler(message, write_name)


def write_name(message):
    global name
    name = message.text
    bot.send_message(message.chat.id, 'Когда этот товар был произведен? В формате "год-месяц-день"')
    bot.register_next_step_handler(message, write_fdate)


def write_fdate(message):
    global fdate
    fdate = message.text
    bot.send_message(message.chat.id, 'Введите срок годности этого товара (в сутках)')
    bot.register_next_step_handler(message, count_ldate)


def count_ldate(message):
    global name
    global fdate
    strfdate = datetime.datetime.strptime(fdate, '%Y-%m-%d')
    maxkeep = int(message.text)
    ldate = strfdate + timedelta(days=maxkeep)

    connect = sqlite3.connect('base.db')
    cursor = connect.cursor()
    cursor.execute("INSERT INTO products (prodname, fdate, ldate) VALUES (?, ?, ?)",
                   (name, fdate, ldate.strftime('%Y-%m-%d')))
    connect.commit()
    cursor.close()
    connect.close()
    bot.send_message(message.chat.id, 'Товар добавлен')


@bot.message_handler(commands=['showlist'])
def showprodlist(message):
    connect = sqlite3.connect('base.db')
    cursor = connect.cursor()
    prodlist = ''

    cursor.execute('SELECT * FROM products')
    productstable = cursor.fetchall()
    for product in productstable:
        prodlist += f'Название товара: {product[1]}, дата смерти: {product[3]}\n'

    cursor.close()
    connect.close()
    if not prodlist:
        bot.send_message(message.chat.id, 'База данных пуста')
    else:
        bot.send_message(message.chat.id, prodlist)


@bot.message_handler(commands=['showhotlist'])
def show_hot_list(message):
    connect = sqlite3.connect('base.db')
    cursor = connect.cursor()
    prodlist = ''

    cursor.execute('SELECT * FROM products')
    productstable = cursor.fetchall()
    for product in productstable:
        nowadate = datetime.datetime.now()
        productname = str(product[1])
        if nowadate + timedelta(days=1) >= datetime.datetime.strptime(product[3], '%Y-%m-%d'):
            prodlist += f'Название товара: {product[1]}, дата смерти: {product[3]}\n'
            cursor.execute(f'DELETE FROM products WHERE prodname == ?', (productname,))

    connect.commit()
    cursor.close()
    connect.close()
    if not prodlist:
        bot.send_message(message.chat.id, 'Горящих товаров нет')
    else:
        bot.send_message(message.chat.id, prodlist)


@bot.message_handler(commands=['clearbase'])
def clearing_base(message):
    connect = sqlite3.connect('base.db')
    cursor = connect.cursor()

    cursor.execute('DELETE FROM products')

    connect.commit()
    cursor.close()
    connect.close()
    bot.send_message(message.chat.id, 'База данных успешно очищена')


bot.polling()