#!/usr/bin/python3
import csv
from time import sleep
import bs4
import requests as req
from os import stat

# имя файла для сохранения данных
csv_filename = "csv_data.csv"
# ссылка на сайт каталога всеинструменты
main_url = "https://spb.vseinstrumenti.ru/krepezh/metricheskij/"
# количество страниц для парсинга
page_nums = 5
# задержка перед переходом на другую страницу (сек)
get_delay = 0.3


def parse_vseinstrumenty_firstpage(response: str) -> dict:
    """
    Получает имена товаров и стоимость с первой страницы сайта всеинструменты
    :param response: текст HTML
    :return: :dict: словарь значений <имя : стоимость>
    """
    parsed = bs4.BeautifulSoup(response, 'lxml')
    goods_list = parsed.findAll("tr", attrs={"class": "goodBlock"})
    good: bs4.Tag
    retdict = dict()
    for good in goods_list:
        name = good.find("span", attrs={"itemprop": "name"})
        price = good.find("span", attrs={"class": "rash-list-price"})
        retdict[name.text.strip()] = price.text.strip()
    return retdict


def parse_vseinstrumenty_other_page(response: str) -> dict:
    """
    Распарсить имена и стоимость позиций сайта всеинструменты с страницы >= 2
    :param response: текст страницы HTML
    :return: :dict: словарь значений <имя : стоимость>
    """
    parsed = bs4.BeautifulSoup(response, 'lxml')
    goods_list = parsed.findAll("tr", attrs={"class": "goodBlock"})
    good: bs4.Tag
    retdict = dict()
    for good in goods_list:
        nametag = good.find("a")
        pricetag = good.find("span", attrs={"class": "rash-list-price"})

        if nametag.contents is not None and pricetag is not None:
            name = nametag.contents[0]
            price = pricetag.contents[0]
            retdict[name.strip()] = price.strip()
    return retdict


result = {}
print(f"запрос на адрес {main_url}")
first_page = req.get(main_url)
print("{0}".format("OK" if first_page.ok else "ERROR"))
result.update(parse_vseinstrumenty_firstpage(first_page.text))
print("Страница 1 {0}".format("данные получены" if len(result) > 0 else "ошибка"))
sleep(get_delay)
for i in range(2, page_nums):
    addr = f"{main_url}page{i}/"
    page = req.get(addr)
    if not page.ok:
        print(f"Страница {i} ошибка")
        break
    else:
        result.update(parse_vseinstrumenty_other_page(page.text))
        print(f"Страница {i} данные получены")
        sleep(get_delay)

if len(result) > 0:
    with open(csv_filename, encoding="UTF8", mode="w") as csv_file:
        writer = csv.writer(csv_file, delimiter=";")
        print("сохранение значений в файл")
        for key in result.keys():
            writer.writerow([key, result[key]])

    try:
        file_stat = stat(csv_filename)
        print(f"Записано {file_stat.st_size} байт")
    except FileNotFoundError:
        print("При сохранении произошла ошибка")
else:
    print("Данные для сохранения отсуствуют")

print("\nЗавершение работы")
