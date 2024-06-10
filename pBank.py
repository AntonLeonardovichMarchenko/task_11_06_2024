from bs4 import BeautifulSoup


import re
import requests
import json

# текущие ссылки на курсы валют ЦБ РФ

# 1 - URL = 'https://www.cbr-xml-daily.ru/latest.js'
# 2 - URL = 'http://www.cbr.ru/scripts/XML_daily.asp'
# 3 - URL = 'https://www.cbr-xml-daily.ru/daily_utf8.xml'
# 4 - URL = 'https://www.cbr.ru/scripts/XML_daily.asp'
# 5 - URL = 'https://www.cbr-xml-daily.ru/daily_utf8.xml'
# 6 - URL = 'https://www.cbr-xml-daily.ru/daily_eng_utf8.xml'


URL = 'https://www.cbr.ru/scripts/XML_daily.asp'


currencySet = set()
currencyLst = list()


rex = None


# список словарей. словарь - это запись о валюте на основе исходнго списка по заданному URL.
# В исходном списке может быть несколько записей с описанием одной валюты.
# Так вот при создании списка словарей функция следит за тем, чтобы в currencyLst входила
# только одна запись. Читается файл - строится список словарей.def load_exchange():

def load_exchange():
    rex = requests.get(URL)
    soup = BeautifulSoup(rex.text,'html.parser')

    strSoup = str(soup).split('valcurs date')
    strSoup = strSoup[1:]

    xxx = str(strSoup).split('valute id')  # Список разделили по разделителю 'valute id'
    cyrrencyData = xxx[0]

    # в первой записи содержится информация о дате записи информации о валютах
    # отличается стуктурой и не имеет отношения ко всему списку записей о валюте.
    # это элемент с индексом 0. его отбросили.
    Valutes = xxx[1:]

    # Работа с элементами в списке.
    # извлечение элемента (полная запись о валюте - элементы одного формата) из списка Valutes.
    for valute in Valutes:
        valuteElem = str(valute).split('>')  # разделение записи по разделителю '>'.

        cL = []


        currencyCode = valuteElem[0]
        currencyCode = currencyCode.replace('\"', '')
        currencyCode = currencyCode.replace('=', '')
        cL.append(currencyCode)
        # cL+=currencyCode
        # cL += '^0^'


        numCode = valuteElem[2]
        numCode = numCode.replace('</numcode','')
        cL.append(numCode)
        # cL+=numCode
        # cL += '^1^'

        charCode = valuteElem[4] # код валюты
        charCode = charCode.replace('</charcode','')
        cL.append(charCode)
        # cL+=charCode
        # cL += '^2^'

        nominal = valuteElem[6]
        nominal = nominal.replace('</nominal','')
        cL.append(nominal)
        # cL += nominal
        # cL +='^_3_^'

        currencyName = valuteElem[8]  # имя валюты
        currencyName = currencyName.replace('</name','')
        cL.append(currencyName)
        # cL+=currencyName
        # cL += '^4^'

        currencyValue = valuteElem[10]  # значение валюты
        currencyValue = currencyValue.replace('</value', '')
        cL.append(currencyValue)
        # cL+=currencyValue
        # cL += '^5^'

        currencyUnitrate = valuteElem[12]  # значение валюты
        currencyUnitrate = currencyUnitrate.replace('</vunitrate','')
        cL.append(currencyUnitrate)
        # cL+=currencyUnitrate
        # cL+= '^6^'

        currencyLst.append(cL)

        # множество, которое позволяет отслеживать уникальность записи о валюте.
        # в список вкючается первая запись
        currencySet.add(charCode)



# фактически здесь проверяется совпадение того, что возвращает load_exchange
# с входным параметром charCode.
# В случае совпадения - возвращается  строка с инфой о валюте, которая формируется
# функцией load_exchange, если же такого кода во множестве нет - возвращается False
def get_exchange(charCode):


    if charCode in currencySet:                   # 1. если нету - и это уже видно по множеству
        for clst in currencyLst:                  #    а если есть - то в списке currencyLst надо найти эту строку
            if charCode == clst[2]:               # 2. charCode входит в список. индекс его вхождения в запись
                return clst                       #    равна 2. И эта запись совпадает со значением аргумента
                                                  # тогда строка с записью о charCode валюты уходит в функцию,
                                                  # которая вызвала get_exchange

    else:
        return False                              # в случае 1. вместо строки о charCode валюты уходит False.






