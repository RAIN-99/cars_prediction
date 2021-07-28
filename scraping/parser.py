#!/usr/bin/env python3

import csv
import re
import time
from random import uniform
from typing import List, Tuple

import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from tqdm import trange

BASE_URL = "https://kolesa.kz"
URL = f"{BASE_URL}/cars/avtomobili-s-probegom/almaty/"
HEADERS = {
    "accept": "*/*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    " AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/89.0.4389.90 Safari/537.36",
}


def get_html(url: str) -> str:
    """Принимает URL-адрес в качестве аргумента запроса,
    возвращает html-страницу из запроса.

    Uses `get()` method from `requests` package

    Args:
        url ([str]): link to the website

    Returns:
        [str]: HTML page from the request
    """
    response = requests.get(url, headers=HEADERS)
    html = response.text
    return html


def pages_count(html: str) -> int:
    """Определение количества страниц в каталоге объявления

    Args:
        html (str): The page to search in which
        the value of the last page is being searched

    Returns:
        int: Last page value
    """
    soup = BeautifulSoup(html, "lxml")
    # находим пагинатор с перечислением всех страниц
    paginator = soup.find("div", {"class": "pager"}).find_all("li")

    # если пагинатор найден, то последняя страница равна последнему элементу
    if paginator:
        last_page = int(paginator[-1].text.strip())
    else:
        last_page = 1
    return last_page


def gather_valuable_data(advert: Tag) -> Tuple[str, ...]:
    """Получение определенных полей в объявлений

    Args:
        advert (Tag): [description]

    Returns:
        Tuple[str, ...]: [description]
    """
    # для выявления паттерна с объемом двигателя
    engine_volume_pattern = re.compile(r"(^\d+.*)(\s)(л$)")
    # все виды топлива указываемые в объявлении
    fuels = ("бензин", "дизель", "газ-бензин", "газ", "гибрид", "электричество")
    # КПП
    kpp = ('КПП механика',"КПП автомат", "КПП типтроник", "КПП вариатор", "КПП робот")
    # название техники, берем всегда только первые три слова из названия
    vehicle_mark = " ".join(
        advert.find("span", {"class": "a-el-info-title"}).text.split()[:3]
    )
    price = "".join(advert.find("span", {"class": "price"}).text.split()[:-1])

    #emergency 
    if advert.find("span", {"class": "emergency"}):
        need_repair = 1
    else:
        need_repair = 0

    
    # блок с описанием объявления
    description = (
        advert.find("div", {"class": "a-search-description"})
        .text.strip()
        .split(",")[:6]
    )
    year = description[0].strip()
    # проверка на соответствие с другими данными,
    # если нет то, второе значение в описании является типом техники
    if (
        description[1].strip() not in fuels
        and re.match(engine_volume_pattern, description[1].strip()) is None
    ):
        vehicle_type = description[1].strip()
    else:
        vehicle_type = ""
    # проверка на соответствие с паттерном объема двигателя
    if re.match(engine_volume_pattern, description[2].strip()):
        engine_volume = description[2].strip()
    elif re.match(engine_volume_pattern, description[1].strip()):
        engine_volume = description[1].strip()
    else:
        engine_volume = ""
    # по умолчанию пустое значение типа топлива и кпп и пробег
    fuel_type = ""
    kpp_type = ""
    mileage = ''
    # проверка на соответствие с одним из значений топлива и КПП и пробег
    for target in description[1:]:
        if target.strip() in fuels:
            fuel_type = target.strip()
        if target.strip() in kpp:
            kpp_type = target.strip()
        if target.strip().startswith("с пробегом"):
            mileage = target.strip()




    data = (
        vehicle_mark,
        year,
        price,
        fuel_type,
        engine_volume,
        vehicle_type,
        kpp_type,
        mileage,
        need_repair,

    )

    return data


def collect_data(adverts: ResultSet) -> List:
    """Сбор всех блоков с объявлениями со страницы

    Args:
        adverts (ResultSet): результат поиска блока с объявлениями

    Returns:
        List: список из объявлении
    """
    collection = []
    for ad in adverts:
        try:
            data = gather_valuable_data(ad)
            collection.append(data)
        except AttributeError:
            continue
        except IndexError:
            continue
        except: 
            continue
    return collection


def save_data(filename, data: List) -> None:
    """Сохраняем данные в формате csv

    Args:
        filename ([type]): имя файла
        data (List): список со всеми спарсенными данными
    """
    with open(filename, "wt", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            (
                "vehicle",
                "year",
                "price",
                "fuel_type",
                "engine_volume",
                "vehicle_type",
                "kpp_type",
                "mileage",
                "need_repair",
            )
        )

        for row in data:
            writer.writerow(row)


def main():
    last_page = pages_count(get_html(URL))

    data_collection = []
    # цикл с визуальной шкалой прогресса
    for i in trange(1, last_page + 1, desc="Progress"):
        html = get_html(f"{URL}?page={i}")
        soup = BeautifulSoup(html, "lxml")
        ads_list = soup.find_all("div", {"class": "a-elem"})
        data = collect_data(ads_list)
        data_collection.extend(data)
        # устанавливаем рандомное значение секунды из диапазона
        rand_sec = round(uniform(0.4, 2.5), 2)
        # паузим выполнение на рандомную секунду
        time.sleep(rand_sec)

    save_data("../data/data_cars.csv", data_collection)


if __name__ == "__main__":
    main()
