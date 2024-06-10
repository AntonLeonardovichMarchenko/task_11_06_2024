import telebot
import config
import datetime # ловится компилятором, но не используется в приложении
import pytz
import json # ранее применялся. В настоящее время не используется


import pBank   # модуль, в котором происходит чтение информации о валютах по ссылке
               # и возвращение информации о валюте, заданной параметром (нажатие одной
               # из трёх кнопок)

P_TIMEZONE = pytz.timezone(config.TIMEZONE)
TIMEZONE_COMMON_NAME = config.TIMEZONE_COMMON_NAME

# токен от папы-бота. Уникальная строка из символов, которая нужна для того,
# чтобы установить подлинность бота в системе. Токен генерируется при создании бота.
bot = telebot.TeleBot('6712637110:AAEpHGXaKnEm8nOlduiq0a3UVtGKhpKCHSU')

# если список описаний pBank.currencyLst ещё не построен - построить. в список
# записей валют за один раз загружаются курсы всех валют по указанному URL-адресу
# этот список дальше используется для получения записей валют по заданному идентификатору
# валюты в формате списка их заданных значений
if len(pBank.currencySet) == 0:
    pBank.load_exchange()


# ответ: - список описателей валют. Это результат компиляции.
# Пока приблизительный формат описателя в списке описателей с информацией о валютах:
#
# [
#    exMark = {
#               'ccy':      0, # currencyCode
#               'num':      1, # numCode
#               'char':     2, # charCode
#               'nomin':    3, # nominal
#               'name':     4, # name
#               'curr':     5, # currency
#               'currUnit': 6, # currencyUnitrate
#           }
# ]
#
# pyTelegramBot Api использует декораторы Python для запуска обработчиков
# разных команд Telegram.
# Также можно перехватывать сообщения с помощью регулярных выражений,
# узнавать тип содержимого в них и применять лямбда-функции.
# Например, если результат присвоения (см декоратор) commands=['start']
# равно True, тогда будет вызвана функция start_command. Объект сообщения
# (десериализованный тип Message) message.chat.id (куда писать) будет
# передан методу send_message с параметром message.chat.id (send_message(message.chat.id))
# сообщения и текстом (что и куда писать)
#
# Из переменной бота можно вызывать методы API Telegram-бота: далее -
# обработчик команды /start. Он добавляется перед строкой bot.polling(none_stop=True):
#
# метод bot.send_message пишет и рисует в окне бота
# для него первым параметром нужен id. Это всегда один и тот же идентификатор.
# Вторым параметром идёт text. У этого метода много параметров,
# поэтому в при вызове метода в списке параметров могут быть и другие.
#
#
#       == 0 ==

# описатель валюты

exMark = {'ccy':      0, # currencyCode
          'num':      1, # numCode
          'char':     2, # charCode
          'nomin':    3, # nominal
          'name':     4, # name
          'curr':     5, # currency
          'currUnit': 6, # currencyUnitrate
          }



globalKeyboard = None
charCode = ''
oldResult = 0.0
diffCurrency = 0.0
ex = None

#       === 1 ===
# Реакция на команду start (commands=['start']): в цикле, который описывается идентификатором
# message.chat.id в цикле под управлением bot.polling(none_stop=True). Здесь идёт демонстрация
# пояснительной надписи с ожиданием нажатия на /exchange или /help. Это два разных события со
# своими функциями функции обработки.
# ========================================================================
@bot.message_handler(commands=['start'])
def start_command(message):


    ##### !!!!!
    #  это сообщение. Представляется в виде окна. Параметры функции - его описание.
    #  функция start_command(...) посылает разные сообщения в зависимости от значения
    #  атрибута  message.story, который устанавливается в функции send_exchange_result(...)

    START = 'start'

    if message.story != 2:
        bot.send_message(  # id  text
            message.chat.id,
            'Поздравления! I can show you exchange rates.\n' +
            'To get the exchange rates press /exchange.\n' +
           'To get help press /help.'
        )
    elif message.story == 2:
        bot.send_message(  # id  text
            message.chat.id,
            'Внимание! It is possible to show the last exchange rates.\n' +
            'To get the exchange rates press /exchange.\n' +
            'To get help press /help.'
        )

#           === 2 ===
# Отработка события help - реакция на команду commands=['help']):
# отправление сообщения и создание окна для обработчика события 'help'.
# При этом производится специальная подготовка объекта keyboard
#
# keyboard = telebot.types.InlineKeyboardMarkup() с добавлением необходимых атрибутов:
#
# атрибутам объекта keyboard с помощью метода keyboard.add(...) присваиваются параметры,
# которые будут описывать свойства окна. потом будет отправлено сообщение (создано окно)
# и при его создании объект keyboard с оределённой клавиатурой передаётся параметром
# в функцию отправления сообщения bot.send_message(...) создания окна.

# ссылка для команду 'help' (commands=['help']) в декораторе.
@bot.message_handler(commands=['help'])
def help_command(message):

    # ====================================================================
    # объект keyboard с определёнными атрибутами: к этому объекту добавляется одна
    # кнопка с надписью 'Message the developer'. Этот объект также создаётся методом
    # telebot.types.InlineKeyboardButton(...).  В результате метод получает
    # встроенную клавиатуру (InlineKeyboardMarkup) с одной кнопкой (InlineKeyboardButton)
    # и следующим текстом: “Message the developer” и url='telegram.me/@AnMar_21_04_2024_bot'
    # при нажатии на эту кнопку происходит переход по этому адресу (зачем ?).
    #

    keyboard = telebot.types.InlineKeyboardMarkup()   # клавиатура
    keyboard.add(

        telebot.types.InlineKeyboardButton('Message the developer',
                                           url='telegram.me/@AnMar_21_04_2024_bot')
                                           # url ссылка на бот
    )   # keyboard с окнопкой 'Message the developer'.


    # отправление события (создание окна help).
    # keyboard с добавленным атрибутом идёт параметром
    bot.send_message(  # id, text, keyboard
        message.chat.id, # id окна - message.chat.id. Далее - текст...
        '1) To receive a list of available currencies press /exchange.\n' +
        '2) Click on the currency you are interested in.\n' +
        '3) You will receive a message containing information regarding the source and the target currencies, ' +
        'buying rates and selling rates.\n' +
        '4) Click “Update” to receive the current information regarding the request. ' +
        'The bot will also show the difference between the previous and the current exchange rates.\n' +
        '5) The bot supports inline. Type @<botusername> in any chat and the first letters of a currency.',
        reply_markup=keyboard # заряженный объект с одной кнопкой
    )


# ========================================================================
#                   === 3 ===
#   функция - обработчик команды exchange (реакция на команду exchange):
#   отправляет сообщение (определяет окно с тремя кнопками),
#   каждая из которых соответствует фиксированной валюте: юань, евро, доллар )
@bot.message_handler(commands=['exchange'])
def exchange_command(message):

    keyboard = telebot.types.InlineKeyboardMarkup()  # окно - объект keyboard
    # Далее добавление кнопок - генераторов соответствующих событий, для которых
    # тоже будут свои функции обработки событий.
    # Тип кнопок — Inline (telebot.types.InlineKeyboardButton).
    # Такие кнопки отображаются под окном сообщения.
    # Для их создания используется метод InlineKeyboardButton.
    # Параметр text отвечает за имя кнопки, а callback_data — за возвращаемую
    # строку при нажатии. Параметр  callback_data= ... определяет функционал кнопки

    keyboard.row(
        telebot.types.InlineKeyboardButton(text='CNY', callback_data='get-CNY'),
        telebot.types.InlineKeyboardButton(text='EUR', callback_data='get-EUR'),
        telebot.types.InlineKeyboardButton(text='USD', callback_data='get-USD')
    )

    # Опять клавиатура, (идёт параметром в bot.send_message),
    # кнопки с соответствующими параметрами text=... и callback_data=...
    # Для создания кнопок используется метод InlineKeyboardButton.
    # Параметр text отвечает за название кнопки (надпись на кнопке),
    # а callback_data — за возвращаемую строку для реализации функционала кнопки
    # при нажатии на кнопку.
    #
    # Далее выполняется метод send_message (боту отправляется сообщение) и добавляется клавиатура
    # окно с тремя кнопками для выбора валют.

    bot.send_message(  # id, text, keyboard
        message.chat.id,
        'Click on the currency of choice:',
        reply_markup=keyboard,
        parse_mode='HTML')

#               === 4 ===
#   обработчик для кнопок трёхкнопочной клавиатуры
#   нажата одна из трёх кнопок. Принцип работы InlineKeyboardButton: когда
#   нажимается одна из кнопок, генерится событие CallbackQuery
#   (в параметре callback-data при создании кнопки содержится информация о
#   её callback_data). Таким образом по этой информации становится известно,
#   какая именно кнопка была нажата и как её обработать. Здесь обработка
#   одинаковая для всех трёх кнопок. Особенности обработки определяются
#   параметром callback_data, который определяет информацию о валюте из списка
#   описателей валют, ранее полученного в результате трансляции. При этом настройка
#   на конкретный описатель валюты не требует особых усилий за счёт ранее прозведённой
#   компиляции исходного списка валют (см. pBank.py)

@bot.callback_query_handler(func=lambda call: True)
def exchange_callback(query):


    global charCode
    global oldResult
    global ex

    diffCurrency = 0.0

    data = query.data

    if data.startswith('get-'):
        data = data[4:]
        # получить запись о валюте по значению data(4:). Здесь используются глобальные
        # переменные и не надо заморачиваться по этоме поводу: если переменные будут
        # локальными глобальным, то придётся ещё раз повторять вызов этой функции.
        query.data = query.data[4:]
        ex = pBank.get_exchange(query.data)

    # ====================================================================

    # обработка событий нажатия на кнопки клавиатуры (много раз на одну и ту же
    # или на разные кнопки). Обеспечивается сравнением кодов кнопок.
    # Тест на нажатую кнопку. Если нажимаются разные кнопки - изменяется код
    # валюты и обнуляются ранее сохранённые значения. Всё начинается заново

        if charCode == '':
            # самое первое нажатие на кнопку

            charCode = data
            oldResult = 0.0
            currencyNow = float(ex[exMark['curr']].replace(',', '.'))
            diffCurrency = 0.0


        elif charCode != '' and charCode != data:
        # нажатие на другую кнопку (в первом и во втором случае выполняются одни и те же действия


            charCode = data
            oldResult = 0.0
            currencyNow = float(ex[exMark['curr']].replace(',','.'))
            diffCurrency = 0.0

        # в обоих сучаях переменным oldResult и diffCurrency присваивается
        # значение 0.0

    # ====================================================================

    #  На одну и ту же кнопку можно нажать
    #  несколько раз подряд. При этом код валюты не меняется, разница в цене
    #  вычисляется на основе ранее сохранённого и текущего значений.

        elif charCode == data:
            # повторное нажатие на кнопку (совпадают идентификаторы валют),
            # которая задаёт ту же самую валюту
            # сопровождается поправкой на изменение значения для выбранной валюты

            # в описании валюты "стоимость" валюты как и остальная информация
            # в описании задаются в текстовом формате, так что здесь выполняется
            # преобразование из текстового формата во float.
            currencyNow = float(ex[exMark['curr']].replace(',', '.'))
            oldResult = currencyNow  # надо запомнить текущее значение.
            # При следующем нажатии на ту же кнопку это значение
            # будет уже старым значением.
            # Далее - вычисление частного от деления старого
            # значения на новое: частное меньше 1 - валюта подорожала,
            #                    частное больше 1 - валюта подешевела

            diffCurrency = oldResult / currencyNow


    get_ex_callback(query, diffCurrency)

# ========================================================================

def get_ex_callback(query, diffCurrency ):

    # обращение к боту для восстановления кнопки после нажатия
    bot.answer_callback_query(query.id)
    # в параметре query уже содержится информация об имени
    # нажатой кнопки (и валюты)
    send_exchange_result(query, diffCurrency)

def send_exchange_result(query, diffCurrency):
    global globalKeyboard

    # получить запись о валюте из списка описателей валюты по значению data
    # в pBankpBank(...)
    ex = pBank.get_exchange(query.data)

    # послать по запросу, который определяется идентификатором
    # query.message.chat.id результат преобразования serialize_ex(ex),
    # и запихнуть это всё в клавиатуру, которая создаётся get_update_keyboard(ex)
    bot.send_message(
        query.message.chat.id,
        serialize_ex(ex, diffCurrency), # это текст (строка)
        # с именем валюты, который отправляется функцией serialize_ex -
        # в параметре ex.
        # функция serialize_ex вызывается в функции bot.send_message.
        # Она это текст размещает в сообщении (в окне)
        reply_markup=  get_update_keyboard(query),   # reply_markup= ...
        # определяет действие, которое должно быть выполнено при выполнении
        # запроса к боту. Создать клавиатуру по ходу выполениея запроса
	    parse_mode='HTML'
    )

    # при выборе валюты с помощью одной из трёх кнопок все окна (клавиатуры) перемещаются
    # наверх. Каждый раз становится всё сложнее выбирать валюты. Для оптимизации доступа
    # к клавиатурам здесь применяются разные способы. Запрос к боту для вызова
    # метода start_command(query.message) - обесечивает повторное возвращение к началу
    # работы приложения с изменённым (для большей наглядности) значением атрибута
    # query.message.story = 2 появляется новая стартовая клавиатурас тремя кнопками
    # в самом низу окна. При этм выбирать валюту становится проще, поскльку кнопки становятся доступнее
    # (ну ещё бы).
    query.message.story = 2 # изменение значения атрибута query.message.story - для
    # возможного изменения алгоритма работы метода start_command(query.message) при
    # его повторном вызове.

    bot.send_message(
                query.message.chat.id,
                '/exchange',
                reply_markup=start_command(query.message)
            )

#           === 5 ===

# Метод serialize_ex показывает
# разницу между текущим и старыми курсами валют (после нажатия кнопки Update)
def serialize_ex(ex, diffCurrency = None):

    global charCode
    global oldResult

    # текущее значение валюты в формате float ============================
    currVal = ex[exMark['curr']]
    fCurrVal = currVal.replace(',', '.')
    floatResult = float(fCurrVal)


    # здесь всё равно всё приводится к строковому формату
    if diffCurrency != None:
        #  Эта запись касается нового курса валюты
        #                   имя валюты                 текущее  преобразованое значение
        result = '<b>' + ex[exMark['name']] + ' -> ' + str(floatResult) + ':</b>\n\n' + \
                'Old:' + str(oldResult) + ":" + str(diffCurrency)
    else:
        result = '<b>' + ex[exMark['name']] + ' -> ' + str(floatResult) + ':</b>\n\n' + \
                 'Old:' + str(oldResult)

    return result

#           === 6 ===


@bot.message_handler(commands=['get_update_keyboard'])
def get_update_keyboard(query):
    global globalKeyboard
    global doIt

    # создание двухкнопочной клавиатуры с разными эффектами за счёт различных опций
    # в функции создания кнопок. Одна из кнопок этой клавиатуры также обеспечивает
    # возвращение приложения в первоначальное состояние (новая трёхкнопочная клавиатура
    # в самом низу главного окна приложения). Нажатие на эту кнопку приводит за счёт
    # параметра switch_inline_query_current_chat приводит к появлению строки, которая
    # состит из имени бота и команды '/exchange', которая также обеспечивает возвращение
    # к исходному состоянию приложения. Это происходит на следующем этапе (после
    # реализаци запроса '/start') выполнения приложения.
    globalKeyboard = telebot.types.InlineKeyboardMarkup()  # определение клавиатуры

    # две кнопки
    globalKeyboard.row(

        telebot.types.InlineKeyboardButton(
                                           text='Exchange',
                                           switch_inline_query_current_chat='     /exchange',
                                           ### url='telegram.me/@AnMar_21_04_2024_bot'
                                           ),
    #  Если в списке параметров функции InlineKeyboardButton опция
    #  switch_inline_query_current_chat установлена, то при нажатии на кнопку в поле ввода
    #  текущего чата будет вставлено имя бота (пользователя бота) и указанный инлайн-запрос.
    #  В данном случае - имя бота и запрос (команда '     /exchange')
    #  Опция может быть пустой, в этом случае будет вставлено только имя бота.

        # объявление этих кнопок...

        telebot.types.InlineKeyboardButton(text='Share',
                                           ###url='telegram.me/@AnMar_21_04_2024_bot',
                                           switch_inline_query=''),
        #                                                Если опция switch_inline_query установлена, то при
        #                                                нажатии на кнопку будет предложено выбрать один
        #                                                из набора чатов (своих чатов), открыть этот чат и вставить
        #                                                в поле ввода имя бота и указанный инлайн-запрос.
        #                                                Может быть пустым, в этом случае будет вставлено только
        #                                                имя пользователя бота.
        #                                                switch_inline_query - после нажатия будет
        #                                                предложен выбор чата где будет использован бот
        #                                                во встроенном режиме (???). Открыть этот чат и вставить
        #                                                логин бота и указанный встроенный запрос в поле ввода.
        #                                                встроенный запрос может быть пустым, и в этом случае
        #                                                будет вставлен только логин бота.
        #
    )


    return globalKeyboard

# ========================================================================
# при работе приложения появление новых окон с информацией о валютах приводит
# к перемещению ране созданных методами bot.send_message и связанных с ними
# окон и клавиатур. И это затрудняет работу с приложением, поскольку клавиатура
# с тремя кнопками (выбора клавиатур) перемещается за пределы окна и становится
# недоступной. Одной из задач этого бота является создание различных способов
# оптимизации интерфейса для работы ботом.

# ========================================================================

# Это двигатель (цикл) всего приложения ====================================
bot.polling(non_stop=True)
